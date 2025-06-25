import os

from services.retrieve.graph.state import RAGState
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_pinecone import PineconeVectorStore
from langchain.chains import ConversationalRetrievalChain
from models.settings import settings

os.environ['PINECONE_API_KEY'] = settings.pinecone_api_key


async def retrieval_chat_node(state: RAGState) -> RAGState:
    if not state.get("rephrased_query"):
        raise ValueError("Missing rephrased query.")

    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small",
        openai_api_key=settings.openai_api_key
    )

    vectorstore = PineconeVectorStore(
        index_name=settings.index_name,
        embedding=embeddings,
        namespace=state["library"]
    )

    retriever = vectorstore.as_retriever()

    llm = ChatOpenAI(
        model_name="gpt-4.1-mini",
        openai_api_key=settings.openai_api_key
    )

    chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        return_source_documents=True
    )

    result = await chain.ainvoke({
        "question": state["rephrased_query"],
        "chat_history": state.get("chat_history", [])
    })

    state["final_answer"] = result["answer"]
    state["retrieved_docs"] = result.get("source_documents", [])
    state["chat_history"] = state.get("chat_history", []) + [
        {"role": "user", "content": state["rephrased_query"]},
        {"role": "assistant", "content": result["answer"]}
    ]

    return state
