from typing import Optional
from fastapi import FastAPI, Query, HTTPException, Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
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

@app.get("/api/manga/{manga_id}")
async def get_manga_details(server: str = Query(default='MANGANELO'), manga_id: str = Path(...)):
    server_map = {
        "MANGANELO": ManganeloScraper,
        # Add other servers if they have a similar endpoint for fetching manga details
    }

    base_url = os.getenv(server)
    if base_url is None or server not in server_map:
        raise HTTPException(status_code=404, detail="Server not found")

    scraper_class = server_map[server]
    scraper = scraper_class(base_url)
    manga_details = await scraper.get_manga_details(manga_id=manga_id)
    return manga_details

@app.get("/api/manga/{manga_id}/{chapter_id}")
async def get_manga_chapter_details(manga_id: str, chapter_id: str, server: str = Query(default='MANGANELO'),):
    server_map = {
        "MANGANELO": ManganeloScraper,
        # Add other servers if they have a similar endpoint for fetching chapter details
    }

    base_url = os.getenv(server)
    
    if base_url is None or server not in server_map:
        raise HTTPException(status_code=404, detail="Server not found")

    scraper_class = server_map[server]
    scraper = scraper_class(base_url)
    chapter_details = await scraper.get_chapter_details(manga_id=manga_id, chapter_id=chapter_id)
    
    return JSONResponse(content=chapter_details)

@app.get("/api/search")
async def search_manga(word: str, page: Optional[int] = 1, server: str = Query(default='MANGANELO')):
    server_map = {
        "MANGANELO": ManganeloScraper,  # Assuming ManganeloScraper can handle search queries
        # Add other servers if they have a similar endpoint for search
    }

    base_url = os.getenv(server)
    
    if base_url is None or server not in server_map:
        raise HTTPException(status_code=404, detail="Server not found")

    scraper_class = server_map[server]
    scraper = scraper_class(base_url)
    search_results = await scraper.search_manga(word=word, page=page)
    
    return search_results

