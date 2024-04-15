import requests
import csv

# Replace these with your actual PocketBase URL and auth token
POCKETBASE_URL = 'https://animevariant.fly.dev'
AUTH_TOKEN = '12345678'

# Headers for authenticated requests
HEADERS = {
    'Authorization': f'Bearer {AUTH_TOKEN}'
}

# Function to fetch data from a PocketBase collection
def fetch_data(collection):
    response = requests.get(f'{POCKETBASE_URL}/api/collections/{collection}/records', headers=HEADERS)
    if response.status_code == 200:
        return response.json()['items']
    else:
        print(f'Failed to fetch {collection}: {response.status_code}')
        return []

# Function to write data to a CSV file
def write_to_csv(filename, fieldnames, data):
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for item in data:
            writer.writerow(item)

# Define collections and their corresponding CSV filenames and fields
collections = {
    'links': ('links.csv', ['mangaId', 'imdbId', 'tmdbId']),
    'mangas': ('mangas.csv', ['mangaId', 'title', 'genres']),
    'rating': ('rating.csv', ['userId', 'mangaId', 'rating', 'timestamp']),
    'tags': ('tags.csv', ['userId', 'mangaId', 'tag', 'timestamp'])
}

# Fetch data for each collection and write to CSV
for collection, (filename, fieldnames) in collections.items():
    data = fetch_data(collection)
    write_to_csv(filename, fieldnames, data)

print('CSV files generated successfully.')
