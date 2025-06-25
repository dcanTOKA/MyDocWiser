import os
from typing import List, Set
from urllib.parse import urlparse, urldefrag

from playwright.async_api import async_playwright, Page
from tqdm import tqdm

from models.settings import Settings
from repositories.library_status_repository import LibraryStatusRepository
from services.ollama_model_service import OllamaPathPatternService
from utils.get_domain import get_main_domain
from utils.get_unique_document_name import get_unique_filename
from utils.log_util import get_logger

logger = get_logger("ScrapeService")


class ScrapeDocumentService:
    def __init__(self, settings_: Settings, start_url):
        self.start_url = start_url
        self.settings_ = settings_
        self.base_url = urlparse(self.start_url).netloc
        self.ignore_prefixes = settings_.ignore_prefixes
        self.main_domain = get_main_domain(self.start_url)
        self.output_dir = os.path.join(os.getcwd(), settings_.documents_output_dir, self.main_domain)

        os.makedirs(self.output_dir, exist_ok=True)

        self.checked: Set[str] = set()
        self.not_checked: Set[str] = {self.start_url}
        self.patterns: List[str] = []

        self.total_scraped: int = 0

    def is_same_domain(self, url: str) -> bool:
        return urlparse(url).netloc == self.base_url

    def should_ignore(self, url: str) -> bool:
        path = urlparse(url).path
        return any(prefix in path for prefix in self.ignore_prefixes)

    def matches_pattern(self, url: str) -> bool:
        path = urlparse(url).path
        return any(path.startswith(p.rstrip("*")) for p in self.patterns)

    def normalize_url(self, url: str) -> str:
        clean_url, _ = urldefrag(url)
        return clean_url

    async def extract_hrefs(self, page: Page) -> List[str]:
        links = await page.evaluate("""() => {
            return Array.from(document.querySelectorAll('a[href]')).map(a => a.href);
        }""")
        return [
            self.normalize_url(link)
            for link in links
            if link.startswith(('http', 'https')) and self.is_same_domain(link)
        ]

    async def fetch_and_save(self, page: Page, url: str) -> str:
        try:
            await page.goto(url)
            html = await page.content()
            filename = get_unique_filename(url, self.output_dir)
            await page.set_content(html)
            await page.add_style_tag(content='body { margin: 0; padding: 0; }')
            await page.pdf(path=filename, margin={'top': '0mm', 'bottom': '0mm', 'left': '0mm', 'right': '0mm'})
            return html
        except Exception as e:
            logger.warning(f"[❌] Failed to fetch {url}: {e}")
            return ""

    async def initialize_patterns(self):
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            try:
                page = await browser.new_page()
                await page.goto(self.start_url)

                all_links = await self.extract_hrefs(page)
                parsed_paths = [urlparse(link).path for link in all_links]

                pattern_service = OllamaPathPatternService(self.settings_)
                self.patterns = await pattern_service.extract_patterns_from_batches(
                    hrefs=parsed_paths,
                    batch_size=self.settings_.pattern_batch_size
                )
            finally:
                await browser.close()

    async def scrape(self):
        logger.info(f"🚀 Starting scrape at: {self.start_url}")
        logger.info(f"📁 Output directory: {self.output_dir}")

        await self.initialize_patterns()
        logger.info("📁 Extracted Path Patterns:")
        for pattern in self.patterns:
            logger.info(f"- {pattern}")

        async with async_playwright() as p:
            browser = await p.chromium.launch()
            try:
                page = await browser.new_page()

                depth = 0
                total_scraped = 0

                while self.not_checked and depth <= self.settings_.scrape_max_depth and total_scraped < self.settings_.scrape_max_pages:
                    current_batch = list(self.not_checked)
                    self.not_checked.clear()

                    progress = tqdm(desc=f"🌐 Depth {depth}", total=len(current_batch))

                    for url in current_batch:
                        if total_scraped >= self.settings_.scrape_max_pages:
                            break
                        url = self.normalize_url(url)

                        if url in self.checked:
                            continue

                        self.checked.add(url)
                        progress.set_description(f"🔎 Crawling: {url}")
                        progress.update(1)

                        html = await self.fetch_and_save(page, url)
                        if not html:
                            continue

                        raw_links = await self.extract_hrefs(page)
                        filtered_links = [
                            self.normalize_url(link)
                            for link in raw_links
                            if self.matches_pattern(link) and not self.should_ignore(link)
                        ]

                        self.not_checked.update({link for link in filtered_links if link not in self.checked})
                        total_scraped += 1

                    depth += 1
                    progress.close()

                self.total_scraped = total_scraped
                logger.info(f"✅ Scraping complete. Total pages visited: {total_scraped}")

                await LibraryStatusRepository.upsert_scrape_done(
                    library=get_main_domain(self.start_url, True),
                    domain=self.start_url,
                    num_pages=total_scraped
                )
            finally:
                await browser.close()
