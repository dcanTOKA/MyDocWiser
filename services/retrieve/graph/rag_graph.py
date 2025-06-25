from typing import Literal

from langgraph.graph import StateGraph, END

from services.retrieve.graph.nodes.check_status import check_status_node
from services.retrieve.graph.nodes.check_topic import check_topic_node
from services.retrieve.graph.nodes.detect_library import detect_library_node
from services.retrieve.graph.nodes.doc_ops_agent import doc_ops_agent_node
from services.retrieve.graph.nodes.rephrase_question import rephrase_question_node
from services.retrieve.graph.nodes.retrieval_chat import retrieval_chat_node
from services.retrieve.graph.nodes.validate_doc_link import validate_doc_link_node
from services.retrieve.graph.state import RAGState


def topic_router(state: RAGState) -> Literal["rephrase_question", END]:
    return "rephrase_question" if state.get("on_topic") else END


def needs_doc_ops(state: RAGState) -> Literal["retrieval_chat", "doc_ops_agent"]:
    if state.get("scrape_done") and state.get("ingest_done"):
        return "retrieval_chat"
    return "doc_ops_agent"


def validate_router(state: RAGState) -> Literal["check_status", END]:
    return "check_status" if state.get("doc_link_valid", False) else END


def build_rag_graph() -> StateGraph:
    builder = StateGraph(RAGState)

    builder.add_node("check_topic", check_topic_node)
    builder.add_node("rephrase_question", rephrase_question_node)
    builder.add_node("detect_library", detect_library_node)
    builder.add_node("validate_doc_link", validate_doc_link_node)
    builder.add_node("check_status", check_status_node)
    builder.add_node("doc_ops_agent", doc_ops_agent_node)
    builder.add_node("retrieval_chat", retrieval_chat_node)

    builder.set_entry_point("check_topic")
    builder.add_conditional_edges("check_topic", topic_router)
    builder.add_edge("rephrase_question", "detect_library")
    builder.add_edge("detect_library", "validate_doc_link")  # düzeltildi
    builder.add_conditional_edges("validate_doc_link", validate_router)  # düzeltildi
    builder.add_conditional_edges("check_status", needs_doc_ops)
    builder.add_edge("doc_ops_agent", "retrieval_chat")
    builder.add_edge("retrieval_chat", END)

    return builder
