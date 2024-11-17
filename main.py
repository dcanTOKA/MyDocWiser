from services.retrieve_service import RetrievalQAService
from services.scrape_documents_service import ScrapeDocumentService
from services.ingestion_documents_service import IngestionDocumentsService
from models.settings import settings
import asyncio

MODE = "scrape"


async def main():
    if MODE == "scrape":
        scrape_service = ScrapeDocumentService(settings)
        await scrape_service.scrape()
    elif MODE == "ingest":
        ingestion_service = IngestionDocumentsService()
        ingestion_service.ingest()
    elif MODE == "retrieve":
        ingestion_service = RetrievalQAService()
        res = ingestion_service.query("How to cluster points in Point Cloud using open3d?")
        print(res)
    else:
        raise ValueError("Invalid mode operation.")

if __name__ == "__main__":
    asyncio.run(main())
