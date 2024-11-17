import os
from langchain_core.prompts import PromptTemplate
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_pinecone import PineconeVectorStore
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from langchain import hub
from models.settings import settings


class RetrievalQAService:
    def __init__(self):
        self.embedding = OpenAIEmbeddings(
            api_key=settings.openai_api_key,
            model="text-embedding-3-small"
        )

        self.llm = ChatOpenAI(
            api_key=settings.openai_api_key,
            model="gpt-3.5-turbo"
        )

        os.environ['PINECONE_API_KEY'] = settings.pinecone_api_key

        self.vector_store = PineconeVectorStore(
            index_name=settings.index_name,
            embedding=self.embedding
        )

        self.retrieval_qa_chat_prompt = hub.pull(settings.retrieval_qa_chat_prompt)

        self.combine_docs_chain = create_stuff_documents_chain(
            llm=self.llm,
            prompt=self.retrieval_qa_chat_prompt
        )

        self.retriever = self.vector_store.as_retriever()

        self.retriever_chain = create_retrieval_chain(
            retriever=self.retriever,
            combine_docs_chain=self.combine_docs_chain
        )

    def query(self, user_query: str):
        result = self.retriever_chain.invoke(input={"input": user_query})
        return result
