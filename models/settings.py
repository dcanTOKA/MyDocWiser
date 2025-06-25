from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    openai_api_key: str
    pinecone_api_key: str
    index_name: str
    ignore_prefixes: list[str]
    documents_output_dir: str
    chunk_size: int
    chunk_overlap: int
    retrieval_qa_chat_prompt: str

    ollama_model: str
    ollama_host: str
    pattern_batch_size: int
    scrape_max_depth: int
    scrape_max_pages: int

    mongo_url: str

    class Config:
        env_file = ".env"


settings = Settings()
