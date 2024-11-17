
# README for Docwiser Project

## Overview

Docwiser is a comprehensive solution for scraping, ingesting, and retrieving documents powered by the cutting-edge capabilities of LangChain and integrated with Pinecone for efficient retrieval. The project automates the process of collecting documents from specified URLs, converting them into a manageable format, and indexing them for quick retrieval using natural language queries. It is particularly useful for handling large volumes of text data and making it easily accessible through simple queries.

The project is set up to handle multiple operations:
1. **Scraping**: Automatically download documents from a specified link, with the ability to ignore certain prefixes.
2. **Ingestion**: Process and store the scraped documents into a Pinecone index for efficient search and retrieval.
3. **Retrieval**: Execute natural language queries to retrieve relevant information from the indexed documents.

These operations can be managed by altering the `MODE` in the `main.py` script.

## .env File Configuration

Create a `.env` file in the root directory of the project with the following parameters:

- `OPENAI_API_KEY`: Your OpenAI API key for accessing GPT models.
- `SCRAPE_DOCS_LINK`: The URL from where the documents should be scraped.
- `IGNORE_PREFIXES`: Prefixes of URLs to ignore during the scraping process.
- `DOCUMENTS_OUTPUT_DIR`: The directory where scraped documents will be saved.
- `PINECONE_API_KEY`: Your Pinecone API key for accessing Pinecone services.
- `INDEX_NAME`: The name of the Pinecone index where documents will be stored.
- `RETRIEVAL_QA_CHAT_PROMPT`: The prompt used for querying the document index in natural language.
- `CHUNK_SIZE`: The size of text chunks to be indexed; this controls the granularity of search.
- `CHUNK_OVERLAP`: The overlap between consecutive chunks to ensure continuity in the context.

## `main.py` Usage

The `main.py` script is the central executable for Docwiser, structured to handle three primary modes:

- `scrape`: Downloads and processes documents from the specified URL into the defined output directory.
- `ingest`: Processes and uploads the documents to a Pinecone index for later retrieval.
- `retrieve`: Retrieves answers to queries based on the content available in the Pinecone index.

To switch between these operations, update the `MODE` variable in the `main.py` file:

```python
MODE = "scrape"  # Options: "scrape", "ingest", "retrieve"
```

#### Sample Code
```python
async def main():
    if MODE == "scrape":
        scrape_service = ScrapeDocumentService(settings)
        await scrape_service.scrape()
    elif MODE == "ingest":
        ingestion_service = IngestionDocumentsService()
        ingestion_service.ingest()
    elif MODE == "retrieve":
        retrieval_service = RetrievalQAService()
        res = retrieval_service.query("How to cluster points in Point Cloud using open3d?")
        print(res)
    else:
        raise ValueError("Invalid mode operation.")
```
