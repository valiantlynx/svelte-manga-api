import lancedb
import numpy as np
import pandas as pd
from hashlib import md5
import re  # For extracting numeric values from strings

# Load manga data
mangas = pd.read_csv('mangas_embedded.csv')
mangas.drop_duplicates(subset=['title'], inplace=True)
# Assuming 'mangas' is your DataFrame
mangas.fillna({'title': '', 'description': '', 'authors': '', 'genres': '', 'latestChapter': 'Chapter 0', 'rating': 0.0, 'views': 0}, inplace=True)

# Convert columns to their expected types explicitly
mangas['title'] = mangas['title'].astype(str)
mangas['description'] = mangas['description'].astype(str)
mangas['authors'] = mangas['authors'].astype(str).apply(lambda x: x if x != "['']" else '')  # Handle list-like string representation
mangas['genres'] = mangas['genres'].astype(str)
mangas['latestChapter'] = mangas['latestChapter'].astype(str)
mangas['rating'] = mangas['rating'].apply(pd.to_numeric, errors='coerce').fillna(0.0)
mangas['views'] = mangas['views'].apply(pd.to_numeric, errors='coerce').fillna(0)

# Ensure columns are treated as strings and fill NaN values with empty strings
string_columns = ['title', 'description', 'authors', 'genres', 'latestChapter']
for column in string_columns:
    mangas[column] = mangas[column].fillna('').astype(str)
    
# Encoding functions for different attributes
def encode_text(text):
    """Simplified encoding for text attributes to a fixed-size vector."""
    hash_digest = md5(text.encode('utf-8')).hexdigest()
    return np.array([int(hash_digest[i:i+2], 16) for i in range(0, len(hash_digest), 2)])

def encode_numeric(value, max_value):
    """Normalize numeric values."""
    try:
        return np.array([float(value) / max_value])
    except ValueError:
        return np.array([0.0])

def encode_date(date_str):
    """Convert dates into a timestamp."""
    try:
        return np.array([pd.to_datetime(date_str).timestamp()])
    except:
        return np.array([0.0])

def extract_numeric_from_text(text):
    """Extract the first numeric value from a text string."""
    numbers = re.findall(r'\d+', text)
    return numbers[0] if numbers else "0"

# Vector generation for each manga based on specified attributes
def generate_vector(manga, attributes):
    vector_parts = []
    for attribute in attributes:
        if attribute == 'title' or attribute == 'description' or attribute == 'authors' or attribute == 'genres':
            vector_parts.append(encode_text(manga[attribute]))
        elif attribute == 'rating' or attribute == 'views':
            value = manga[attribute]
            max_value = 5 if attribute == 'rating' else 1e9  # Example max values
            vector_parts.append(encode_numeric(value, max_value))
        elif attribute == 'latestChapter':
            chapter_num = extract_numeric_from_text(manga['latestChapter'])
            vector_parts.append(encode_numeric(chapter_num, 10000))  # Assuming a max chapter count
        elif attribute == 'lastUpdated':
            vector_parts.append(encode_date(manga['lastUpdated']))
    return np.concatenate(vector_parts)

# Specify attributes to use for embedding
attributes = ['title', 'authors', 'genres', 'rating'] # ['title', 'description', 'authors', 'genres', 'rating', 'views', 'latestChapter', 'lastUpdated']

# Apply embedding generation
mangas['vector'] = mangas.apply(lambda row: generate_vector(row, attributes), axis=1)

# Prepare data for LanceDB
data = [{
    "id": row['id'],
    "title": row['title'],
    "vector": row['vector'].tolist(),
} for index, row in mangas.iterrows()]
# Before adding data to LanceDB, ensure that vectors are correctly serialized
for item in data:
    # Ensure 'vector' is a list of floats (or a similar numeric format)
    item['vector'] = item['vector'].tolist() if hasattr(item['vector'], 'tolist') else list(item['vector'])

    # Example: Convert other fields to string if necessary
    item['title'] = str(item['title'])
    # Repeat for other fields as needed based on your schema requirements
# Before creating the table, log the data types of the first item (for debugging)
if data:  # Ensure data is not empty
    for sample_item in data:
        print(f"sample_item: {sample_item['title']}")

        
# Then proceed to initialize and populate the LanceDB table
db = lancedb.connect("./data/manga-db")
try:
    db.drop_table("manga_set")
except Exception as e:
    print(e)



table = db.create_table("manga_set", data=data)

def get_recommendations(query_title, limit=10):
    query_vector = next(row['vector'] for index, row in mangas.iterrows() if row["title"] == query_title)
    result = table.search(query_vector).limit(limit + 1).to_pandas()
    return result[result['title'] != query_title][['title']].head(limit)

# Example usage
print(get_recommendations("Ragnarok: Into The Abyss", limit=20))
