import asyncio
import os
from typing import List

from langchain_community.document_loaders import PyPDFLoader
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from tqdm import tqdm

from models.settings import settings, Settings
from repositories.library_status_repository import LibraryStatusRepository
from utils.get_domain import get_main_domain
from utils.log_util import get_logger


class IngestionDocumentsService:
    def __init__(self, scrape_docs_link, library_for_namespace):
        self.scrape_docs_link = scrape_docs_link
        self.library_for_namespace = library_for_namespace
        self.logger = get_logger("IngestionService")
        self.settings: Settings = settings

        self.chunk_size = self.settings.chunk_size
        self.chunk_overlap = self.settings.chunk_overlap
        self.library = get_main_domain(self.scrape_docs_link, True)
        self.domain = get_main_domain(self.scrape_docs_link)

        self.documents_files_path = os.path.join(
            os.getcwd(),
            self.settings.documents_output_dir,
            self.domain
        )

        self.raw_documents: List = []
        self.documents: List = []

        os.environ['PINECONE_API_KEY'] = self.settings.pinecone_api_key

        self.embedding = OpenAIEmbeddings(model="text-embedding-3-small", openai_api_key=self.settings.openai_api_key)
        self.vector_db_index_name = self.settings.index_name

        self.embedding_size: int = 0

    def load_documents(self):
        if not os.path.exists(self.documents_files_path):
            raise FileNotFoundError(f"📁 Document folder '{self.documents_files_path}' does not exist.")

        file_list = os.listdir(self.documents_files_path)
        if not file_list:
            self.logger.warning("⚠️ No files found in the document directory.")
            return

        self.logger.info(f"📥 Loading PDF files from: {self.documents_files_path}")
        for document_name in tqdm(file_list, desc="📄 Loading PDFs..."):
            if not document_name.endswith(".pdf"):
                continue
            file_path = os.path.join(self.documents_files_path, document_name)
            try:
                loader = PyPDFLoader(file_path)
                data = loader.load()
                self.raw_documents.extend(data)
            except Exception as e:
                self.logger.warning(f"⚠️ Error loading '{document_name}': {e}")

        self.logger.info(f"✅ Loaded {len(self.raw_documents)} raw documents.")

    def split_documents(self):
        if not self.raw_documents:
            self.logger.warning("⚠️ No raw documents to split.")
            return

        self.logger.info("🔗 Splitting documents into chunks...")
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap
        )
        self.documents = text_splitter.split_documents(self.raw_documents)
        self.logger.info(f"✅ Split into {len(self.documents)} document chunks.")

    def send_to_vector_db(self):
        if not self.documents:
            self.logger.warning("⚠️ No document chunks to send to vector DB.")
            return

        self.logger.info("📡 Sending vectors to Pinecone...")
        try:
            vectorstore = PineconeVectorStore.from_existing_index(
                index_name=self.vector_db_index_name,
                embedding=self.embedding,
                namespace=self.library_for_namespace
            )
            vectorstore.add_documents(self.documents)
            self.logger.info("✅ Ingestion to Pinecone completed.")
        except Exception as e:
            self.logger.error(f"❌ Failed to ingest documents into Pinecone: {e}")
            raise

    async def ingest(self):
        self.logger.info("🚀 Starting ingestion pipeline...")

        try:
            self.load_documents()
            self.split_documents()
            self.send_to_vector_db()
            self.embedding_size = len(self.documents)
            await LibraryStatusRepository.upsert_ingest_done(
                library=self.library,
                domain=self.domain,
                embedding_size=self.embedding_size
            )
            self.logger.info("📊 Ingestion status recorded in MongoDB.")
            await asyncio.sleep(10)
        except Exception as e:
            self.logger.error(f"❌ Ingestion pipeline failed: {e}")
            raise
