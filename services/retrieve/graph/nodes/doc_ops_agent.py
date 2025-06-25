from services.retrieve.graph.state import RAGState
from services.scrape_documents_service import ScrapeDocumentService
from services.ingestion_documents_service import IngestionDocumentsService
from models.settings import settings
from repositories.library_status_repository import LibraryStatusRepository
from utils.get_domain import get_main_domain
from utils.log_util import get_logger

logger = get_logger("DocOps Agent Node")


async def doc_ops_agent_node(state: RAGState) -> RAGState:
    library = state.get("library")
    domain = get_main_domain(state.get("scrape_docs_link"))

    logger.info(f"🚀 Node started for library: {library}, domain: {domain}")

    if not library:
        raise ValueError("Missing library name in state.")

    scrape_needed = not state.get("scrape_done", False)
    ingest_needed = not state.get("ingest_done", False)

    if scrape_needed:
        logger.info("🧲 Starting scraping operation...")
        scraper = ScrapeDocumentService(settings, state["scrape_docs_link"])
        await scraper.scrape()

        await LibraryStatusRepository.upsert_scrape_done(
            library=library,
            domain=domain,
            num_pages=scraper.total_scraped
        )
        state["scrape_done"] = True
        logger.info(f"✅ Scraping done. {scraper.total_scraped} pages scraped.")

    if ingest_needed:
        logger.info("📥 Starting ingestion...")
        ingestor = IngestionDocumentsService(state["scrape_docs_link"], library)
        await ingestor.ingest()

        await LibraryStatusRepository.upsert_ingest_done(
            library=library,
            domain=domain,
            embedding_size=ingestor.embedding_size
        )
        state["ingest_done"] = True
        logger.info(f"✅ Ingestion done. {ingestor.embedding_size} chunks embedded.")

    return state
