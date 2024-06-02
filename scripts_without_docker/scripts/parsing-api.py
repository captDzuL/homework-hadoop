from itertools import chain
import asyncio
import aiohttp
import pandas as pd
import os

async def fetch_data(data: dict, index: int):
    # Filter data
    effect = data['effect_entries'][0]['effect']
    language = data['effect_entries'][0]['language']
    short_effect = data['effect_entries'][0]['short_effect']
    
    id = [index]
    pokemon_ability_id = [index]
    effect = [effect]
    language = [language]
    short_effect = [short_effect]

    return id, pokemon_ability_id, effect, \
        language, short_effect


async def handle_index(data: dict, index: int):
    id = [index]
    pokemon_ability_id = [index]
    effect = [None]
    language = [data['flavor_text_entries'][0]['language']]
    short_effect = [None]

    return id, pokemon_ability_id, effect, \
        language, short_effect

async def handle_status(index: int):
    id = [index]
    pokemon_ability_id = [index]
    effect = [None]
    language = [None]
    short_effect = [None]

    return id, pokemon_ability_id, effect, \
        language, short_effect

async def fetch(session: aiohttp.ClientSession, URL: str, id: int) -> dict:
    frame = dict()

    async with session.get(URL) as response:
        if response.status == 200:
            try:
                data = await response.json()

                # Filter data
                id, pokemon_ability_id, effect, \
                    language, short_effect = await fetch_data(data, id)

                # Append data
                frame['id'] = id
                frame['pokemon_ability_id'] = pokemon_ability_id
                frame['effect'] = effect
                frame['language'] = language
                frame['short_effect'] = short_effect

            except IndexError:
                # Filter data
                id, pokemon_ability_id, effect, \
                    language, short_effect = await handle_index(data, id)

                # Append data
                frame['id'] = id
                frame['pokemon_ability_id'] = pokemon_ability_id
                frame['effect'] = effect
                frame['language'] = language
                frame['short_effect'] = short_effect
                
        else:
            # Filter data
            id, pokemon_ability_id, effect, \
                language, short_effect = await handle_status(id)
            
            # Append data
            frame['id'] = id
            frame['pokemon_ability_id'] = pokemon_ability_id
            frame['effect'] = effect
            frame['language'] = language
            frame['short_effect'] = short_effect

    return frame

async def merge_data(result: list) -> dict:
    id = []
    pokemon_ability_id = []
    effect = []
    language = []
    short_effect = []

    # Loop for make multi-dimensional list
    for dt in result:
        id.append(dt['id'])
        pokemon_ability_id.append(dt['pokemon_ability_id'])
        effect.append(dt['effect'])
        language.append(dt['language'])
        short_effect.append(dt['short_effect'])

    """
        chain.from_iterable => Marge multi-dimensional list,
        like [[1, 2, 3], [4, 5, 6], [7, 8, 9]] => [1, 2, 3, 4, 5, 6, 7, 8, 9]
    """
    return {
        'id': list(chain.from_iterable(id)),
        'pokemon_ability_id': list(chain.from_iterable(pokemon_ability_id)),
        'effect': list(chain.from_iterable(effect)),
        'language': list(chain.from_iterable(language)),
        'short_effect': list(chain.from_iterable(short_effect))
    }

async def partition_data(df: pd.DataFrame) -> list:
    start_row = [
        i for i in range(0, len(df), 100)
    ] # Create start row for partition data by 100 until 1000

    result = [
        df.iloc[start:start+100] 
        for start in start_row
    ] # Partition data by 100 until 1000

    return result

async def write_csv(chunks: list) -> None:
    # Write csv by chunks
    for df in chunks:
        filename = f'result_{df.index[0] + 1}_{df.index[-1] + 1}.csv'
        dir_file = f'./scripts_without_docker/scripts/data/result_{df.index[0] + 1}_{df.index[-1] + 1}.csv'

        mode = 'a' if os.path.exists(filename) else 'w'
        df.to_csv(dir_file, mode=mode, index=False)

        print(f'File {filename} has been created')

    print('All files have been created')

async def main() -> None:
    URL = 'https://pokeapi.co/api/v2/ability/{ability_id}'
    IDS = [id for id in range(1, 1001)] # Generate Pokemon Ability IDs

    async with aiohttp.ClientSession() as session:
        tasks = [
            fetch(session, URL.format(ability_id=id), id)
            for id in IDS
        ] # Create tasks

        results = await asyncio.gather(
            *tasks
        ) # Run Simultaneously

        data = await merge_data(
            results
        ) # Merge all data that has been get

        df = pd.DataFrame(data)

        # Create chunks
        chunks = await partition_data(df)
        
        # Write csv
        await write_csv(chunks)

asyncio.run(main())