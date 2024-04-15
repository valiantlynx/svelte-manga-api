import httpx
import asyncio
import pandas as pd
import json
import os
from httpx import Timeout
from tqdm.asyncio import tqdm  # Use asyncio version of tqdm for async loops
import logging
from colorama import init, Fore

init(autoreset=True)  # Initialize colorama to auto-reset styling after each print

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()


# Your FastAPI application's base URL
BASE_URL = 'http://localhost:8000'
timeout = Timeout(10.0, connect=60.0)

GENRES = ['Action',
 'Adventure',
 'Comedy',
 'Cooking',
 'Doujinshi',
 'Drama',
 'Erotica',
 'Fantasy',
 'Gender bender',
 'Harem',
 'Historical',
 'Horror',
 'Isekai',
 'Josei',
 'Manhua',
 'Manhwa',
 'Martial arts',
 'Mature',
 'Mecha',
 'Medical',
 'Mystery',
 'One shot',
 'Pornographic',
 'Psychological',
 'Romance',
 'School life',
 'Sci fi',
 'Seinen',
 'Shoujo',
 'Shoujo ai',
 'Shounen',
 'Shounen ai',
 'Slice of life',
 'Smut',
 'Sports',
 'Supernatural',
 'Tragedy',
 'Webtoons',
 'Yaoi',
 'Yuri']  # Update as needed

async def fetch_manga(server='MANGANELO', genre="", page=1):
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.get(f'{BASE_URL}/api/manga', params={'server': server, 'genre': genre, 'page': page})
        if response.status_code == 200:
            return response.json().get('mangas', [])
        else:
            logger.error(f"{Fore.RED}Failed to fetch manga list for genre '{genre}' at page {page}")
        return []

async def fetch_manga_details(manga_id, server='MANGANELO'):
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.get(f'{BASE_URL}/api/manga/{manga_id}', params={'server': server})
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"{Fore.RED}Failed to fetch details for manga ID {manga_id}")
        return {}

async def fetch_details_for_mangas(manga_list):
    return await asyncio.gather(*(fetch_manga_details(manga['id']) for manga in manga_list))

def append_to_csv(df, filename='mangas_embedded.csv'):
    # Check if file exists and is not empty to decide on writing headers
    file_exists = os.path.isfile(filename) and os.path.getsize(filename) > 0
    df.to_csv(filename, mode='a', header=not file_exists, index=False)

async def main():
    checkpoint_file = 'manga_checkpoint.json'
    processed_manga_ids, checkpoint = set(), {'genre_index': 0, 'page': 1, 'processed_manga_ids': []}
    try:
        with open(checkpoint_file) as file:
            checkpoint = json.load(file)
            processed_manga_ids.update(checkpoint.get('processed_manga_ids', []))
    except FileNotFoundError:
        logger.info(f"{Fore.YELLOW}Checkpoint file not found, starting from scratch.")

    for genre_index, genre in enumerate(GENRES[checkpoint['genre_index']:], start=checkpoint['genre_index']):
        page = checkpoint['page']
        logger.info(f"{Fore.CYAN}Processing genre: {genre}")

        # Wrap the page loop with tqdm for progress tracking
        async for page in tqdm(range(checkpoint['page'], 51), desc=f"{genre}", leave=True):
            current_mangas = await fetch_manga(genre=genre, page=page)
            if not current_mangas:
                break

            manga_details_list = await fetch_details_for_mangas(current_mangas)
            for manga, details in zip(current_mangas, manga_details_list):
                if manga['id'] not in processed_manga_ids and details:
                    manga.update({'authors': '|'.join(str(x) for x in details.get('authors', [])),
                        'genres': '|'.join(str(x) for x in details.get('genres', [])),
                        'lastUpdated': details['lastUpdated'],
                        'views': details['views']})
                    processed_manga_ids.add(manga['id'])

            new_data_df = pd.DataFrame(current_mangas).drop_duplicates(subset=['id'])
            append_to_csv(new_data_df)
            checkpoint.update({'genre_index': genre_index, 'page': page + 1, 'processed_manga_ids': list(processed_manga_ids)})
            with open(checkpoint_file, 'w') as file:
                json.dump(checkpoint, file)

        checkpoint['page'] = 1  # Reset for next genre

asyncio.run(main())