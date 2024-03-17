from typing import Optional
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .scrapers.manga_scraper import ManganeloScraper, ChapMangaScraper, MangaClashScraper
from dotenv import load_dotenv
import os

load_dotenv()
app = FastAPI()
allowed_origins = os.getenv("ALLOWED_ORIGINS", "").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
 
import debugpy
debugpy.listen(("0.0.0.0", 5678))

@app.get("/")
def read_root():
    return {"Hello": "World ass wiper"}


@app.get("/api/manga")
async def get_manga(server: str = Query(default='MANGANELO'), genre: Optional[str] = None, page: Optional[int] = None, type: Optional[str] = None):
    # Map server names to their corresponding scrapers
    server_map = {
        "MANGANELO": ManganeloScraper,
        "CHAPMANGANELO": ChapMangaScraper,
        "MANGACLASH": MangaClashScraper,
    }

    # Fetch the base URL from environment variables
    base_url = os.getenv(server)
    if base_url is None or server not in server_map:
        raise HTTPException(status_code=404, detail="Server not found")

    scraper_class = server_map[server]
    scraper = scraper_class(base_url)
    # Pass optional parameters directly to the scrape method, which will handle defaults
    mangas = await scraper.scrape(genre=genre, page=page, type=type)
    return {"mangas": mangas}