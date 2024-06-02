import debugpy
from prometheus_fastapi_instrumentator import Instrumentator
from typing import Optional, List
from fastapi import FastAPI, Query, HTTPException, Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from .scrapers.manga_scraper import (
    ManganeloScraper, MangaClashScraper, MangaKissScraper, KissMangaScraper, ManhuaTopScraper,
    MangaParkIoScraper, MangaParkNetScraper, ManhuaFastScraper, RMangaScraper, ReadMangaScraper
)
from dotenv import load_dotenv
import httpx
import os
import logging

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

debugpy.listen(("0.0.0.0", 5678))

# Define the server map for scrapers and image base URLs
server_map = {
    "MANGANELO": {
        "scraper": ManganeloScraper,
        "image_base_urls": [os.getenv("MANGANELO_CDN"), os.getenv("MANGANELO")]
    },
    "MANGACLASH": {
        "scraper": MangaClashScraper,
        "image_base_urls": [os.getenv("MANGACLASH_CDN"), os.getenv("MANGACLASH")]
    },
    "MANGAKISS": {
        "scraper": MangaKissScraper,
        "image_base_urls": [os.getenv("MANGAKISS_CDN"), os.getenv("MANGAKISS")]
    },
    "KISSMANGA": {
        "scraper": KissMangaScraper,
        "image_base_urls": [os.getenv("KISSMANGA_CDN"), os.getenv("KISSMANGA")]
    },
    "MANHUATOP": {
        "scraper": ManhuaTopScraper,
        "image_base_urls": [os.getenv("MANHUATOP_CDN"), os.getenv("MANHUATOP")]
    },
    "MANGAPARK_IO": {
        "scraper": MangaParkIoScraper,
        "image_base_urls": [os.getenv("MANGAPARK_IO_CDN"), os.getenv("MANGAPARK_IO")]
    },
    "MANGAPARK_NET": {
        "scraper": MangaParkNetScraper,
        "image_base_urls": [os.getenv("MANGAPARK_NET_CDN"), os.getenv("MANGAPARK_NET")]
    },
    "MANHUAFAST": {
        "scraper": ManhuaFastScraper,
        "image_base_urls": [os.getenv("MANHUAFAST_CDN"), os.getenv("MANHUAFAST")]
    },
    "RMANGA": {
        "scraper": RMangaScraper,
        "image_base_urls": [os.getenv("RMANGA_CDN"), os.getenv("RMANGA")]
    },
    "READMANGA": {
        "scraper": ReadMangaScraper,
        "image_base_urls": [os.getenv("READMANGA_CDN"), os.getenv("READMANGA")]
    }
}


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/api/manga")
async def get_manga(server: str = Query(default='MANGANELO'), genre: Optional[str] = None, page: Optional[int] = None, type: Optional[str] = None):
    try:
        if server not in server_map:
            raise HTTPException(status_code=404, detail="Server not found")

        base_url = os.getenv(server)
        scraper_class = server_map[server]["scraper"]
        scraper = scraper_class(base_url)
        mangas = await scraper.scrape(genre=genre, page=page, type=type)
        return {"mangas": mangas}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/manga/{manga_id}")
async def get_manga_details(server: str = Query(default='MANGANELO'), manga_id: str = Path(..., example="manga-tf996688")):
    try:
        if server not in server_map:
            raise HTTPException(status_code=404, detail="Server not found")

        base_url = os.getenv(server)
        scraper_class = server_map[server]["scraper"]
        scraper = scraper_class(base_url)
        manga_details = await scraper.get_manga_details(manga_id=manga_id)
        return manga_details
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/manga/{manga_id}/{chapter_id}")
async def get_manga_chapter_details(manga_id: str = Path(..., example="manga-tf996688"), chapter_id: str = Path(..., example="chapter-1"), server: str = Query(default='MANGANELO')):
    try:
        if server not in server_map:
            raise HTTPException(status_code=404, detail="Server not found")

        base_url = os.getenv(server)
        scraper_class = server_map[server]["scraper"]
        scraper = scraper_class(base_url)
        chapter_details = await scraper.get_chapter_details(manga_id=manga_id, chapter_id=chapter_id)
        return JSONResponse(content=chapter_details)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/search")
async def search_manga(word: str = Query(..., example="eternal"), page: Optional[int] = 1, server: str = Query(default='MANGANELO')):
    try:
        if server not in server_map:
            raise HTTPException(status_code=404, detail="Server not found")

        base_url = os.getenv(server)
        scraper_class = server_map[server]["scraper"]
        scraper = scraper_class(base_url)
        search_results = await scraper.search_manga(word=word, page=page)
        return search_results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

"""Helper function to fetch image from a list of URLs

Returns:
    _type_: response
"""


async def fetch_image(image_urls: List[str]):
    async with httpx.AsyncClient(follow_redirects=True) as client:
        for url in image_urls:
            if url:
                try:
                    response = await client.get(url)
                    response.raise_for_status()
                    return response
                except httpx.HTTPStatusError:
                    continue
                except httpx.RequestError:
                    continue
    raise HTTPException(
        status_code=404, detail="Failed to fetch image from all sources")


"""for managanelo

Returns:
    _type_: image data
"""


@app.get("/api/mangaimage/{image}")
async def get_image_from_path(server: str = Query(default='MANGANELO'), image: str = Path(..., example="manga-tf996688.jpg")):
    logging.warning(f"heeeelo---------> {image}")
    try:
        if server not in server_map:
            raise HTTPException(status_code=404, detail="Server not found")

        image_base_urls = server_map[server]["image_base_urls"]
        logging.warning(f"---------> {image_base_urls}")
        if not image_base_urls:
            raise HTTPException(
                status_code=404, detail=f"Image base URL not configured for server {server}")

        image_urls = [
            f"{base_url}/mangaimage/{image}" for base_url in image_base_urls if base_url]

        logging.warning(f"---------> {image_urls}")
        response = await fetch_image(image_urls)
        return StreamingResponse(response.iter_bytes(), media_type=response.headers["Content-Type"])
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch image: {str(exc)}")
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=500, detail=f"Request error: {str(exc)}")


"""for managanelo

Returns:
    _type_: image data
"""


@app.get("/api/{id1}/{id2}/{image}")
async def get_image_from_path(server: str = Query(default='MANGANELO'), id1: str = Path(..., example="a4"), id2: str = Path(..., example="45"), image: str = Path(..., example="a4458a2fadf6cd005dc1a92a6ab8e4b3.jpg")):
    try:
        if server not in server_map:
            raise HTTPException(status_code=404, detail="Server not found")

        image_base_urls = server_map[server]["image_base_urls"]
        if not image_base_urls:
            raise HTTPException(
                status_code=404, detail=f"Image base URL not configured for server {server}")

        image_urls = [
            f"{base_url}/{id1}/{id2}/{image}" for base_url in image_base_urls if base_url]
        response = await fetch_image(image_urls)
        return StreamingResponse(response.iter_bytes(), media_type=response.headers["Content-Type"])
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch image: {str(exc)}")
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=500, detail=f"Request error: {str(exc)}")


"""for mangaclash. might change it so that its modular cause it does the same as the one for manganelo just different paths

Returns:
    _type_: image data
"""


@app.get("/api/{id1}/{id2}/{id3}/{id4}/{image}")
async def get_image_from_path(server: str = Query(default='MANGACLASH'), id1: str = Path(..., example="wp-content"), id2: str = Path(..., example="uploads"), id3: str = Path(..., example="2020"), id4: str = Path(..., example="07"), image: str = Path(..., example="thumb_5f1547fc5a52a.jpg")):
    try:
        if server not in server_map:
            raise HTTPException(status_code=404, detail="Server not found")

        image_base_urls = server_map[server]["image_base_urls"]
        if not image_base_urls:
            raise HTTPException(
                status_code=404, detail=f"Image base URL not configured for server {server}")

        image_urls = [
            f"{base_url}/{id1}/{id2}/{id3}/{id4}/{image}" for base_url in image_base_urls if base_url]
        response = await fetch_image(image_urls)
        return StreamingResponse(response.iter_bytes(), media_type=response.headers["Content-Type"])
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch image: {str(exc)}")
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=500, detail=f"Request error: {str(exc)}")


Instrumentator().instrument(app).expose(app)
