import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import asyncpg
import csv
#import pydoop.hdfs as hdfs
import os

app = FastAPI()
DATABASE_URL = "postgresql://poke:p0k3!!123@postgres/pokebase"

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EffectRequest(BaseModel):
    loan_id: str
    user_id: str
    pokemon_ability_id: str

@app.on_event("startup")
async def startup():
    app.state.pool = await asyncpg.create_pool(DATABASE_URL, max_size=10)  # Limit the pool size

@app.on_event("shutdown")
async def shutdown():
    await app.state.pool.close()

@app.post("/pokemon_effect/")
async def pokemon_effect(effect_request: EffectRequest):
    loan_id = effect_request.loan_id
    user_id = effect_request.user_id
    pokemon_ability_id = effect_request.pokemon_ability_id

    logger.info(f"Received request with loan_id: {loan_id}, user_id: {user_id}, pokemon_ability_id: {pokemon_ability_id}")

    try:
        url = f"https://pokeapi.co/api/v2/ability/{pokemon_ability_id}"
        logger.info(f"Fetching data from URL: {url}")
        call = requests.get(url)
        response = call.json()

        #logger.info(f"Received response from PokeAPI: {response}")

        returned_entries = []

        async with app.state.pool.acquire() as conn:
            for effect_entries in response['effect_entries']:
                await conn.execute("""
                    INSERT INTO pokemon_effect (loan_id, user_id, pokemon_ability_id, effect, language, short_effect)
                    VALUES ($1, $2, $3, $4, $5, $6);
                """, int(loan_id), int(user_id), int(pokemon_ability_id), 
                str(effect_entries['effect']), str(effect_entries['language']['name']), str(effect_entries['short_effect']))

                #logger.info(f"Inserted entry: {effect_entries}")

                returned_entries.append(effect_entries)

        return {
            "loan_id": loan_id,
            "user_id": user_id,
            "pokemon_ability_id": pokemon_ability_id,
            "returned_entries": returned_entries
        }
    
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@app.get("/check_db_connection/")
async def check_db_connection():
    try:
        async with app.state.pool.acquire() as conn:
            await conn.execute("SELECT 1")
        return {"status": "Connection successful"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Connection failed: {e}")

# Fungsi untuk menembak API pokemon_effect dengan pokemon_ability_id 1-999 dan menyimpan hasilnya ke HDFS
@app.post("/trigger_pokemon_effects_to_csv/")
async def trigger_pokemon_effects_to_csv():
    fieldnames = ["loan_id", "user_id", "pokemon_ability_id", "effect", "language", "short_effect"]
    
    errors = []
    all_entries = []

    for pokemon_ability_id in range(1, 1000):
        effect_request = EffectRequest(
            loan_id="1",  # ganti sesuai dengan loan_id yang sesuai
            user_id="1",  # ganti sesuai dengan user_id yang sesuai
            pokemon_ability_id=str(pokemon_ability_id)
        )
        try:
            response = await pokemon_effect(effect_request)
            logger.info(f"Success for pokemon_ability_id {pokemon_ability_id}: {response}")
            
            for entry in response["returned_entries"]:
                entry.update({
                    "loan_id": effect_request.loan_id,
                    "user_id": effect_request.user_id,
                    "pokemon_ability_id": effect_request.pokemon_ability_id
                })
                all_entries.append(entry)
                
        except HTTPException as e:
            logger.error(f"Error for pokemon_ability_id {pokemon_ability_id}: {e.detail}")
            errors.append({"pokemon_ability_id": pokemon_ability_id, "error": e.detail})

    # Partition all_entries into chunks of 100
    partition_size = 100
    for i in range(0, len(all_entries), partition_size):
        chunk = all_entries[i:i + partition_size]
        start_id = i + 1
        end_id = i + len(chunk)
        file_name = f"pokemon_effect_{start_id}to{end_id}.csv"
        local_csv_file = f"/tmp/{file_name}"

        # Write each chunk to a separate local CSV file
        with open(local_csv_file, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for entry in chunk:
                writer.writerow({
                    "loan_id": entry["loan_id"],
                    "user_id": entry["user_id"],
                    "pokemon_ability_id": entry["pokemon_ability_id"],
                    "effect": entry["effect"],
                    "language": entry["language"],
                    "short_effect": entry["short_effect"]
                })
        
        # Upload the local CSV file to HDFS
        #hdfs_path = f"/path/in/hdfs/{file_name}"
        #hdfs.put(local_csv_file, hdfs_path)
        #os.remove(local_csv_file)  # Remove local file after upload

    return {"status": "Completed", "errors": errors, "files": [f"pokemon_effect_{i + 1}to{min(i + 100, len(all_entries))}.csv" for i in range(0, len(all_entries), 100)]}
