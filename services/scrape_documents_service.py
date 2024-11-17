from playwright.async_api import async_playwright
import os
from tqdm.asyncio import tqdm
from urllib.parse import urlparse

from models.settings import Settings
from utils.get_unique_document_name import get_unique_filename
from utils.get_domain import get_main_domain


class ScrapeDocumentService:
    def __init__(self, settings: Settings):
        self.start_url = settings.scrape_docs_link
        self.base_url = urlparse(self.start_url).netloc
        self.documents_reference_path = urlparse(self.start_url).path
        self.personalized_folder_name = get_main_domain(self.start_url)
        self.checked = set()
        self.not_checked = {self.start_url}
        self.ignore_prefixes = settings.ignore_prefixes
        self.output_dir = os.path.join(os.getcwd(), settings.documents_output_dir, self.personalized_folder_name)

        os.makedirs(self.output_dir, exist_ok=True)

    def is_same_domain(self, url) -> bool:
        return self.base_url == urlparse(url).netloc

    @staticmethod
    async def fetch_page(page, url: str) -> str:
        await page.goto(url)
        return await page.content()

    @staticmethod
    async def save_document(page, content: str, filename: str):
        await page.set_content(content)
        await page.add_style_tag(content='body { margin: 0; padding: 0; }')
        await page.pdf(path=filename, margin={'top': '0mm', 'bottom': '0mm', 'left': '0mm', 'right': '0mm'})

    @staticmethod
    def should_ignore(url, ignore_prefixes) -> bool:
        path = urlparse(url).path
        return any(prefix in path for prefix in ignore_prefixes)

    async def get_links(self, page) -> set:
        links = set(await page.evaluate("""() => {
            return Array.from(document.querySelectorAll('a[href]')).map(a => a.href);
        }"""))

        filtered_links = {link for link in links
                          if link.startswith(('http', 'https')) and link.endswith('.html') and
                          self.is_same_domain(link)}

        return {link for link in filtered_links if not self.should_ignore(link, self.ignore_prefixes)}

    async def scrape(self):
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()

            progress = tqdm(total=1, desc="Total URLs to check", leave=True)

            while self.not_checked:
                current_url = self.not_checked.pop()
                self.checked.add(current_url)
                progress.set_description(f"Scraping: {current_url}")
                progress.update(1)
                try:
                    html_content = await self.fetch_page(page, current_url)
                    output_filename = get_unique_filename(current_url, self.output_dir)
                    await self.save_document(page, html_content, output_filename)
                    new_links = await self.get_links(page)
                    # Add only new and not already checked links
                    new_not_checked = new_links - self.checked - self.not_checked
                    self.not_checked.update(new_not_checked)
                    progress.total += len(new_not_checked)
                except Exception as e:
                    print(f"Failed to fetch {current_url}: {e}")

            progress.close()
            await browser.close()
