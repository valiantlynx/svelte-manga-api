from typing import Union
from fastapi import FastAPI, Query
from .scrapers.manga_scraper import MangaScraper
from dotenv import load_dotenv
import os

load_dotenv()
app = FastAPI()
 
import debugpy
debugpy.listen(("0.0.0.0", 5678))

@app.get("/")
def read_root():
    return {"Hello": "World ass wiper"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

@app.get("/api/manga")
async def get_manga(genre: str = Query(default='genre-45')):
    VITE_IMAGE_URL_MANGANELO = os.getenv('VITE_IMAGE_URL_MANGANELO')
    scraper = MangaScraper(VITE_IMAGE_URL_MANGANELO)
    mangas = await scraper.scrape(genre=genre)
    return {"mangas": mangas}