from .base_scraper import BaseScraper
from bs4 import BeautifulSoup
from typing import Optional
from datetime import datetime
import re


class ManganeloScraper(BaseScraper):
    async def scrape(self, page: Optional[int] = None, genre: Optional[str] = None, type: Optional[str] = None):
        # Apply default values if None
        page = page or '1'  # Default page
        genre = genre or 'Isekai'  # Default genre
        type = type or 'topview'  # Default type

        html = await self.fetch_html(f"{self.base_url}/genre/{genre}?type={type}&page={page}")
        soup = BeautifulSoup(html, 'html.parser')
        mangas = []

        for item in soup.select('.content-genres-item'):
            titleElement = item.select_one('.genres-item-name')
            imgElement = item.select_one('img')
            chaptersElement = item.select_one('.genres-item-chap')
            srcElement = item.select_one('a')
            descriptionElement = item.select_one('.genres-item-description')
            authorElements = item.select('.genres-item-author')
            ratingElement = item.select_one('.genres-item-rate')

            src = srcElement['href'] if srcElement else None
            id = src.split('/')[-1] if src else None
            titleId = titleElement.text.strip() if titleElement else None
            img = imgElement['src'] if imgElement else None

            # Handling authors
            authors = []
            for authorElement in authorElements:
                authorName = authorElement.text.strip()
                authors.append(authorName)

            content = {
                "title": titleId,
                "img": img,
                "latestChapter": chaptersElement.text.strip() if chaptersElement else "",
                "rating": ratingElement.text.strip() if ratingElement else "",
                "src": src,
                "id": id,
                "titleId": titleId,
                "description": descriptionElement.text.strip() if descriptionElement else "",
                "authors": authors,
            }

            mangas.append(content)

        return mangas

    async def get_manga_details(self, manga_id: str):
        url = f"{self.base_url}/manga/{manga_id}"
        html = await self.fetch_html(url)
        soup = BeautifulSoup(html, 'html.parser')

        title = soup.select_one('.story-info-right h1').text
        img = soup.select_one('.info-image img')['src']
        description = soup.select_one(
            '#panel-story-info-description').text.strip()

        # Extracting authors and genres
        all_elements = [elem.text.strip()
                        for elem in soup.select('.table-value a')]
        authors = [all_elements[0]] if all_elements else []
        genres = all_elements[1:] if len(all_elements) > 1 else []

        rating_element = soup.select_one('[property="v:average"]')
        rating = float(rating_element.text) if rating_element else None

        # Extracting and converting last updated date
        lastUpdated_text = soup.select_one(
            '.story-info-right-extent p:nth-of-type(1) .stre-value').text.strip()
        lastUpdated = datetime.strptime(
            lastUpdated_text, "%b %d,%Y - %I:%M %p") if lastUpdated_text else None

        # Extracting and converting views
        views_text = soup.select_one(
            '.story-info-right-extent p:nth-of-type(2) .stre-value').text.strip()
        views = float(re.sub(r'[KM]', lambda x: "e3" if x.group(
            0) == 'K' else "e6", views_text)) if views_text else 0

        chapters = [{
            "src": c['href'],
            "chapterId": c['href'].split('/')[-1],
            "chapterTitle": c.text.strip()
        } for c in soup.select('.chapter-name')]

        return {
            "title": title,
            "img": img,
            "description": description,
            "authors": authors,
            "rating": rating,
            "genres": genres,
            "lastUpdated": lastUpdated.strftime("%Y-%m-%d %H:%M") if lastUpdated else "Unknown",
            "views": views,
            "episodes": chapters,
        }

    async def get_chapter_details(self, manga_id: str, chapter_id: str):
        # Construct the chapter URL based on manga_id and chapter_id
        chapter_url = f"{self.base_url}/chapter/{manga_id}/{chapter_id}"  # Adjust as necessary
        html = await self.fetch_html(chapter_url)
        soup = BeautifulSoup(html, 'html.parser')

        title = soup.select_one('.panel-chapter-info-top h1').text
        images = soup.select('.container-chapter-reader img')
        
        image_data = []
        for index, img in enumerate(images, start=1):
            image_url = img.get('data-src')  # Use 'src' if 'data-src' is not available
            image_data.append({
                "imageUrl": image_url,
                "pageNumber": index,
                "totalPages": len(images)
            })

        return {
            "title": title,
            "images": image_data
        }


class ChapMangaScraper(BaseScraper):
    async def scrape(self, genre: Optional[str] = None):
        genre = genre or 'genre-45'  # Default genre

        html = await self.fetch_html(f"{self.base_url}/{genre}")
        soup = BeautifulSoup(html, 'html.parser')
        mangas = []

        for item in soup.select('.content-genres-item'):
            title = item.select_one('.genres-item-name').text
            img = item.select_one('img')['src']
            chapters = item.select_one('.genres-item-chap').text
            mangas.append({
                "title": title,
                "img": img,
                "latestChapter": chapters,
                # Add more fields as per your original code
            })

        return mangas


class MangaClashScraper(BaseScraper):
    async def scrape(self, genre: Optional[str] = None):
        genre = genre or 'genre'  # Default genre

        html = await self.fetch_html(f"{self.base_url}/{genre}")
        soup = BeautifulSoup(html, 'html.parser')
        mangas = []

        for item in soup.select('.list-truyen-item-wrap'):
            title = item.select_one('.genres-item-name').text
            img = item.select_one('img')['src']
            chapters = item.select_one('.list-story-item-wrap-chapter').text
            mangas.append({
                "title": title,
                "img": img,
                "latestChapter": chapters,
                # Add more fields as per your original code
            })

        return mangas
