from typing import Optional
from fastapi import FastAPI, Query, HTTPException, Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from .scrapers.manga_scraper import ManganeloScraper, ChapMangaScraper, MangaClashScraper
from dotenv import load_dotenv
import httpx
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

@app.get("/api/getimage")
async def get_image(url: str = Query(..., alias="url")):
    if not url:
        raise HTTPException(status_code=400, detail="No image URL provided")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            response.raise_for_status()
        except httpx.RequestError as exc:
            raise HTTPException(status_code=500, detail=f"Failed to fetch image: {str(exc)}")

    return StreamingResponse(response.iter_bytes(), media_type=response.headers["Content-Type"])

@app.get("/api/mangaimage/{image}")
async def get_image_from_path(
    server: str = Query(default='MANGANELO'), 
    image: str = Path(...)
):
    # Dynamically determining the base URL based on the server parameter
    # Fetch the base URL from environment variables using the server name
    base_url = os.getenv(server)
    if not base_url:
        raise HTTPException(status_code=404, detail=f"Server {server} not found or base URL not configured")

    image_url = f"{base_url}/mangaimage/{image}"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(image_url)
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise HTTPException(status_code=500, detail=f"Failed to fetch image: {str(exc)}")
        except httpx.RequestError as exc:
            raise HTTPException(status_code=500, detail=f"Request error: {str(exc)}")

    return StreamingResponse(response.iter_bytes(), media_type=response.headers["Content-Type"])


@app.get("/api/{id1}/{id2}/{image}")
async def get_image_from_path(
    server: str = Query(default='MANGANELO'), 
    id1: str = Path(...), 
    id2: str = Path(...), 
    image: str = Path(...)
):
    # Dynamically determining the base URL based on the server parameter
    # Fetch the base URL from environment variables using the server name
    base_url = os.getenv(server.upper() + "_CDN")
    if not base_url:
        raise HTTPException(status_code=404, detail=f"Server {server} not found or base URL not configured")

    image_url = f"{base_url}/{id1}/{id2}/{image}"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(image_url)
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise HTTPException(status_code=500, detail=f"Failed to fetch image: {str(exc)}")
        except httpx.RequestError as exc:
            raise HTTPException(status_code=500, detail=f"Request error: {str(exc)}")

    return StreamingResponse(response.iter_bytes(), media_type=response.headers["Content-Type"])