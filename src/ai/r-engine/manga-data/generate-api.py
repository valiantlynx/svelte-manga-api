import httpx
import csv
import asyncio

# Your FastAPI application's base URL
BASE_URL = 'http://localhost:8000'

# Predefined list of genres to iterate through, including "All"
GENRES = ['All', 'Action', 'Romance', 'Isekai', 'Comedy']  # Add more as needed

# Function to fetch manga data for a specific page and genre
async def fetch_manga(server='MANGANELO', genre="", page=1):
    async with httpx.AsyncClient() as client:
        response = await client.get(f'{BASE_URL}/api/manga', params={'server': server, 'genre': genre, 'page': page})
        return response.json()['mangas']

# Function to fetch manga details
async def fetch_manga_details(manga_id, server='MANGANELO'):
    async with httpx.AsyncClient() as client:
        response = await client.get(f'{BASE_URL}/api/manga/{manga_id}', params={'server': server})
        return response.json()

# Main async function to orchestrate data fetching and CSV writing
async def main():
    mangas = []  # Initialize an empty list to store all manga data

    # Iterate over each genre and each page up to 50
    for genre in GENRES:
        for page in range(1, 5):  # Iterate through pages 1 to 50
            current_page_mangas = await fetch_manga(genre=genre, page=page)
            mangas.extend(current_page_mangas)  # Add the fetched mangas to the main list
            if not current_page_mangas:  # Break the loop if no mangas are returned for the current page
                break

    # Write manga basic info to CSV
    with open('mangas.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['mangaId', 'title', 'img', 'latestChapter', 'rating', 'src', 'description', 'authors'])
        for manga in mangas:
            manga_details = await fetch_manga_details(manga['id'])
            writer.writerow([
                manga['id'], manga['title'], manga['img'], manga['latestChapter'],
                manga_details.get('rating', ''), manga['src'],
                manga_details.get('description', ''), "|".join(manga_details.get('authors', []))
            ])
    print('Manga CSV file has been created with {} records.'.format(len(mangas)))

# Run the main function
asyncio.run(main())
