from services.retrieve.graph.state import RAGState
from services.retrieve.graph.schemas import RephrasedQuestion
from langchain_openai import ChatOpenAI
from models.settings import settings
from utils.log_util import get_logger

structured_llm = ChatOpenAI(model_name="gpt-4.1-mini", temperature=0,
                            openai_api_key=settings.openai_api_key).with_structured_output(RephrasedQuestion)

logger = get_logger("Rephrase Question Node")


def rephrase_question_node(state: RAGState) -> RAGState:
    question = state["user_query"]
    result: RephrasedQuestion = structured_llm.invoke(question)
    state["rephrased_query"] = result.rewritten.strip()
    logger.info("Rephrased Question: {}".format(state["rephrased_query"]))
    return state
