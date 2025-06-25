# services/retrieve/service.py

from services.retrieve.graph.rag_graph import graph
from services.retrieve.graph.state import RAGState


class RetrievalAgentService:
    def __init__(self):
        pass

    async def run(self, user_query: str, scrape_docs_link: str) -> str:
        initial_state: RAGState = {
            "user_query": user_query,
            "chat_history": [],
            "rephrased_query": "",
            "on_topic": True,
            "library": "",
            "scrape_done": False,
            "ingest_done": False,
            "retrieved_docs": [],
            "final_answer": "",
            "scrape_docs_link": scrape_docs_link,
            "doc_link_valid": False,
            "doc_link_mismatch_warning": ""
        }
        final_state: RAGState = await graph.ainvoke(initial_state)

        if final_state.get("on_topic") is False:
            return "This question is not related to developer documentation, APIs, or SDKs."

        return final_state.get("final_answer", "No answer was generated.")
