from .base_scraper import BaseScraper
from bs4 import BeautifulSoup

class MangaScraper(BaseScraper):
    async def scrape(self, genre: str = 'genre-45'):
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
