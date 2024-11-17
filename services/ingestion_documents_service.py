import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from tqdm import tqdm

from models.settings import settings
from utils.get_domain import get_main_domain


class IngestionDocumentsService:
    def __init__(self):
        self.chunk_size = settings.chunk_size
        self.chunk_overlap = settings.chunk_overlap
        self.documents_files_path = os.path.join(
            os.getcwd(),
            settings.documents_output_dir,
            get_main_domain(settings.scrape_docs_link)
        )
        self.embedding = OpenAIEmbeddings(api_key=settings.openai_api_key, model="text-embedding-3-small")
        self.vector_db_index_name = settings.index_name

        self.raw_documents = []
        self.documents = []

        os.environ['PINECONE_API_KEY'] = settings.pinecone_api_key

    def load_documents(self):
        for document_name in tqdm(os.listdir(self.documents_files_path), desc="Loading documents..."):
            try:
                loader = PyPDFLoader(os.path.join(self.documents_files_path, document_name))
                data = loader.load()
                self.raw_documents.extend(data)
            except Exception as e:
                print(f"Error loading {document_name}: {e}")

        print(f"Loaded {len(self.raw_documents)} documents.")

    def split_documents(self):
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap
        )

        self.documents = text_splitter.split_documents(self.raw_documents)

        print(f"Split documents into  {len(self.documents)} documents/chunks.")

    def ingest(self):
        if not os.path.exists(self.documents_files_path):
            raise FileNotFoundError(f"Document folder '{self.documents_files_path}' does not exist.")

        self.load_documents()
        self.split_documents()

        PineconeVectorStore.from_documents(
            self.documents,
            self.embedding,
            index_name=self.vector_db_index_name
        )

        print("Ingestion finished.")

