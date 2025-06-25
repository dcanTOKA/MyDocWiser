from typing import TypedDict, List, Optional
from langchain_core.messages import BaseMessage, HumanMessage
from langchain.schema import Document


class RAGState(TypedDict):
    user_query: str
    scrape_docs_link: str
    rephrased_query: Optional[str]
    on_topic: Optional[bool]
    library: Optional[str]
    chat_history: List[BaseMessage]
    retrieved_docs: List[Document]
    final_answer: Optional[str]
    scrape_done: Optional[bool]
    ingest_done: Optional[bool]
    doc_link_valid: Optional[bool]
    doc_link_mismatch_warning: Optional[str]