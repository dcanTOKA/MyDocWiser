from services.retrieve.graph.state import RAGState
from repositories.library_status_repository import LibraryStatusRepository
from utils.log_util import get_logger

logger = get_logger("Check Status Node")


async def check_status_node(state: RAGState) -> RAGState:
    library = state.get("library")
    if not library:
        state["scrape_done"] = False
        state["ingest_done"] = False
        return state

    status = await LibraryStatusRepository.get_by_library(library)

    if status:
        logger.info(f"[Check Status Node] scrape_done status: {status.scrape_done}")
        logger.info(f"[Check Status Node] ingest_done status: {status.ingest_done}")
        state["scrape_done"] = status.scrape_done
        state["ingest_done"] = status.ingest_done
    else:
        logger.warning(f"[Check Status Node] ⚠️ No status found for library: {library}")
        state["scrape_done"] = False
        state["ingest_done"] = False

    return state
