# 📚 Docwiser: Modular RAG Pipeline for Developer Documentation

**Docwiser** is a modular, orchestrated RAG (Retrieval-Augmented Generation) system designed for accurate and auditable question answering over developer documentation. It uses a LangGraph-based execution graph, LLMs for document understanding and query refinement, and vector stores like Pinecone for semantic search. The pipeline automatically scrapes, chunks, embeds, and retrieves documentation content from any developer website.

---

## 🚀 Key Features

- 🕸️ **Pattern-Aware Scraping**  
  Extracts only relevant documentation URLs using a lightweight Qwen3 model over anchor tag patterns.

- 📄 **Semantic Document Ingestion**  
  Recursive chunking and OpenAI embeddings stored in Pinecone under namespaced indices.

- 🔄 **LangGraph-Based Orchestration**  
  Dynamically determines whether to scrape, ingest, or retrieve based on current state.

- 💬 **LLM-Based Answering**  
  GPT-4.1-mini generates markdown answers grounded in retrieved sources with rephrased query logs.

- 📑 **Markdown Reporting**  
  Each query response is returned with a fully traceable markdown log for transparency and reproducibility.

---

## 📦 Prerequisites

Ensure the following services are up and running before starting the system:

| Component | Required | Description |
|----------|----------|-------------|
| 🟢 MongoDB | Yes | Running at `mongodb://localhost:27017` |
| 🟢 Ollama | Yes | Running with Qwen3 model (`ollama run qwen3:0.6b`) |
| 🟢 Pinecone | Yes | API key and an active index configured |

---

## 🛠️ Installation

```bash
# Clone and enter project
git clone https://github.com/your-org/docwiser.git
cd docwiser

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## ⚙️ Environment Configuration

Before running the system, create a `.env` file in the project root with the following contents:

```env
# OpenAI API Key
OPENAI_API_KEY=your_openai_api_key

# Pinecone Configuration
PINECONE_API_KEY=your_pinecone_key
INDEX_NAME=docwiser-index
RETRIEVAL_QA_CHAT_PROMPT=langchain-ai/retrieval-qa-chat

# Ollama Configuration (LLM for pattern discovery)
OLLAMA_MODEL=qwen3:0.6b
OLLAMA_HOST=http://localhost:11434

# MongoDB Configuration
MONGO_URL=mongodb://localhost:27017

# Scraping Behavior
IGNORE_PREFIXES=["cpp_api","c_api"]
DOCUMENTS_OUTPUT_DIR=documents
SCRAPE_MAX_DEPTH=2
SCRAPE_MAX_PAGES=100
PATTERN_BATCH_SIZE=10

# Ingestion Parameters
CHUNK_SIZE=1000
CHUNK_OVERLAP=100
```

## ▶️ Running the System

To start the Docwiser pipeline and launch the Gradio interface:

```bash
python main.py