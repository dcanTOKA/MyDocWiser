# repositories/library_status_repository.py
from datetime import datetime
from typing import Optional
from models.library import LibraryStatus


class LibraryStatusRepository:

    @staticmethod
    async def get_by_library(library: str) -> Optional[LibraryStatus]:
        return await LibraryStatus.find_one({"library": library})

    @staticmethod
    async def upsert_status(
        library: str,
        domain: str,
        update_fields: dict
    ):
        status = await LibraryStatusRepository.get_by_library(library)
        update_fields.setdefault("library", library)
        update_fields.setdefault("domain", domain)

        if status:
            for key, value in update_fields.items():
                setattr(status, key, value)
            await status.save()
        else:
            status = LibraryStatus(**update_fields)
            await status.insert()

    @staticmethod
    async def upsert_scrape_done(library: str, domain: str, num_pages: int = 0):
        await LibraryStatusRepository.upsert_status(
            library,
            domain,
            {
                "scrape_done": True,
                "last_scrape_time": datetime.utcnow(),
                "num_pages_scraped": num_pages,
            }
        )

    @staticmethod
    async def upsert_ingest_done(library: str, domain: str, embedding_size: int = 0):
        await LibraryStatusRepository.upsert_status(
            library,
            domain,
            {
                "ingest_done": True,
                "last_ingest_time": datetime.utcnow(),
                "embedding_size": embedding_size,
            }
        )

    @staticmethod
    async def is_ready_for_retrieval(library: str) -> bool:
        status = await LibraryStatusRepository.get_by_library(library)
        return bool(status and status.scrape_done and status.ingest_done)
