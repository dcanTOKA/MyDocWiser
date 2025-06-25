from datetime import datetime

from beanie import Document, Indexed


class LibraryStatus(Document):
    library: Indexed(str, unique=True)  # ex: "open3d"
    domain: str  # ex: "docs.open3d.org"

    scrape_done: bool = False
    ingest_done: bool = False

    last_scrape_time: datetime | None = None
    last_ingest_time: datetime | None = None

    num_pages_scraped: int | None = None
    embedding_size: int | None = None

    class Settings:
        name = "library_status"
