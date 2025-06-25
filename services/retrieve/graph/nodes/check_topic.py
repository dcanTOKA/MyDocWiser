from services.retrieve.graph.state import RAGState
from services.retrieve.graph.schemas import GradeQuestion
from langchain_openai import ChatOpenAI
from models.settings import settings
from utils.log_util import get_logger

structured_llm = ChatOpenAI(model_name="gpt-4.1-mini", temperature=0,
                            openai_api_key=settings.openai_api_key).with_structured_output(GradeQuestion)

logger = get_logger("Check Topic Node")


def check_topic_node(state: RAGState) -> RAGState:
    question = state["user_query"]
    result: GradeQuestion = structured_llm.invoke(question)
    state["on_topic"] = result.score.strip().lower() == "yes"
    logger.info(f"Checking topic relevance: {question} -> {state['on_topic']}")
    return state
