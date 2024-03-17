from .base_scraper import BaseScraper
from bs4 import BeautifulSoup
from typing import Optional
 
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
        url = f"{self.base_url}/manga/{manga_id}"  # Adjust URL based on actual path structure
        html = await self.fetch_html(url)
        soup = BeautifulSoup(html, 'html.parser')

        title = soup.select_one('.story-info-right h1').text
        img = soup.select_one('.info-image img')['src']
        description = soup.select_one('#panel-story-info-description').text.strip()

        # Extracting authors and genres
        all_elements = [elem.text.strip() for elem in soup.select('.table-value a')]
        if all_elements:
            authors = [all_elements[0]]
            genres = all_elements[1:] 
        else:
            authors = []
            genres = [] 
            
        rating_element = soup.select_one('[property="v:average"]')
        rating = rating_element.text if rating_element else 'N/A'  # Default to 'N/A' if not found
        
        # Extracting last updated date and views
        lastUpdatedElement = soup.select_one(".story-info-right-extent .stre-value:nth-of-type(1)")
        lastUpdated = lastUpdatedElement.text.strip() if lastUpdatedElement else "Unknown"

        viewsElement = soup.select_one(".story-info-right-extent .stre-value:nth-of-type(2)")
        views = viewsElement.text.strip() if viewsElement else "Unknown"

        chapters = [{
            "src": c['href'],
            "chapterId": c['href'].split('/')[-1],
            "chapterTitle": c.text
        } for c in soup.select('.chapter-name')]

        return {
            "title": title,
            "img": img,
            "description": description,
            "authors": authors,
            "rating": rating,
            "genres": genres,
            "lastUpdated": lastUpdated,
            "views": views,
            "episodes": chapters,
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