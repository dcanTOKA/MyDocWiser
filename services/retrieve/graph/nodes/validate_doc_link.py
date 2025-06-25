from services.retrieve.graph.state import RAGState
from utils.get_domain import get_main_domain
from utils.log_util import get_logger
from difflib import SequenceMatcher

logger = get_logger("Validate Doc Link Node")


async def validate_doc_link_node(state: RAGState) -> RAGState:
    library = state.get("library")

    docs_link = state.get("scrape_docs_link")

    doc_domain = get_main_domain(docs_link, True)

    ratio = SequenceMatcher(None, library.lower(), doc_domain.lower()).ratio()

    if ratio < 0.6:
        warning_msg = (
            f"⚠️ Doc link mismatch: Expected link for library '{library}', "
            f"but got: {docs_link}. Please check your SCRAPE_DOCS_LINK value."
        )
        logger.warning(warning_msg)
        state["doc_link_valid"] = False
        state["doc_link_mismatch_warning"] = warning_msg
    else:
        logger.info(f"✅ Doc link matches library '{library}'")
        state["doc_link_valid"] = True

    return state
