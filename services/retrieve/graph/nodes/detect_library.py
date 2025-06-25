from services.retrieve.graph.state import RAGState
from services.retrieve.graph.schemas import DetectedLibrary
from langchain_openai import ChatOpenAI
from models.settings import settings
from utils.log_util import get_logger

structured_llm = ChatOpenAI(model_name="gpt-4.1-mini", temperature=0, openai_api_key=settings.openai_api_key).with_structured_output(DetectedLibrary)

logger = get_logger("Detect Library Node")


def detect_library_node(state: RAGState) -> RAGState:
    question = state.get("rephrased_query") or state.get("user_query")
    result: DetectedLibrary = structured_llm.invoke(question)

    lib = result.library.strip().lower()
    if lib == "none" or not lib:
        state["library"] = None
    else:
        state["library"] = lib
    logger.info("Detected Library: {}".format(state["library"]))
    return state
