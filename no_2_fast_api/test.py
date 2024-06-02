import asyncpg
import asyncio

DATABASE_URL = "postgresql://postgres:admin@localhost:5432/pokedb"

async def test_connection():
    try:
        pool = await asyncpg.create_pool(DATABASE_URL)
        async with pool.acquire() as conn:
            result = await conn.fetch('SELECT 1')
            print("Connection successful:", result)
    except Exception as e:
        print(f"Error connecting to the database: {e}")

asyncio.run(test_connection())
