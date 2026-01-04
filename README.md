# Agriculture Chatbot - Agentic RAG System

An intelligent backend application using FastAPI that helps farmers get accurate information about citrus diseases and government agricultural schemes through a conversational interface.

## Project Overview

This chatbot uses an **Agentic RAG (Retrieval Augmented Generation)** system to:

- Understand farmer queries in natural language
- Route queries to appropriate knowledge bases (Disease or Scheme)
- Retrieve relevant information using hybrid search (Semantic + BM25)
- Generate farmer-friendly responses with source citations
- Maintain conversation history for multi-turn dialogues

## Architecture

```
User Query → Intent Classification → Hybrid Retrieval → Answer Generation
                ↓                          ↓                   ↓
        MongoDB Memory            Pinecone Vector DB      Gemini LLM
```

## Tech Stack

- **Framework**: FastAPI
- **Agent Orchestration**: LangChain, LangGraph, LangSmith
- **LLM**: Google Gemini 1.5 Flash
- **Vector Database**: Pinecone
- **Memory Database**: MongoDB
- **Embeddings**: Nomic Embed Text v1.5
- **Retrieval**: Semantic Search + BM25 + RRF Fusion + Cross-Encoder Re-ranking
- **PDF Processing**: PyPDF, PDFPlumber

## 📋 Features

### Core Features

- **Intent Detection**: Classifies queries as Disease, Scheme, Hybrid, or Unclear
- **Intelligent Routing**: Routes to appropriate knowledge base(s)
- **Hybrid Search**: Combines semantic and keyword search
- **Conversation Memory**: Multi-turn dialogue support
- **Clarification**: Asks for clarification on ambiguous queries
- **Source Citations**: Provides page numbers and confidence scores

### Advanced Features

- **RRF Fusion**: Combines multiple retrieval methods
- **Cross-Encoder Re-ranking**: Improves result relevance
- **MongoDB Memory**: Stores conversation history
- **LangSmith Tracing**: Debugging and observability

## Installation

### Prerequisites

- Python 3.9+
- UV package manager
- Git

### Setup

```bash
# Clone repository
git clone https://github.com/kaushik-003/agri-chatbot.git
cd agri-chatbot

# Install dependencies with UV
uv sync

# Copy environment template
cp .env.example .env
# Edit .env with your API keys

# Setup Jupyter kernel
uv run python -m ipykernel install --user --name=agri-chatbot

# Start Jupyter for development
uv run jupyter notebook
```

## API Keys Required

1. **Google Gemini API**: https://aistudio.google.com/app/apikey
2. **Pinecone**: https://app.pinecone.io/ (Free starter tier)
3. **MongoDB Atlas**: https://www.mongodb.com/cloud/atlas (Free M0 tier)
4. **LangSmith** (Optional): https://smith.langchain.com/

## Project Structure

```
agri-chatbot/
├── notebooks/           # Jupyter notebooks for development
│   ├── 01_setup_and_data_exploration.ipynb
│   ├── 02_pinecone_index_creation.ipynb
│   ├── 03_mongodb_memory_setup.ipynb
│   ├── 04_intent_classification.ipynb
│   ├── 05_retrieval_pipeline.ipynb
│   ├── 06_answer_generation.ipynb
│   ├── 07_full_system_test.ipynb
│   └── 08_deployment_prep.ipynb
├── app/                 # Production code
│   ├── agents/          # LangGraph agents
│   ├── vectorstore/     # Pinecone operations
│   ├── database/        # MongoDB operations
│   └── utils/           # Helper functions
├── data/                # PDF documents
├── tests/               # Test suite
├── main.py              # FastAPI application
└── pyproject.toml       # Dependencies
```

## Development Workflow

1. **Phase 1-7**: Develop in Jupyter notebooks
2. **Phase 8**: Convert to production FastAPI code
3. **Testing**: Run test suite
4. **Deployment**: Deploy to Render/Railway

## 📝 Usage

### Run Jupyter Notebooks

```bash
uv run jupyter notebook
```

### Run FastAPI Server (after Phase 8)

```bash
uv run uvicorn main:app --reload
```

### API Endpoints

- `POST /query` - Main query endpoint
- `GET /conversation/{session_id}` - Get conversation history
- `DELETE /conversation/{session_id}` - Clear conversation
- `GET /health` - Health check

## Testing

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=app
```

## Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [API Documentation](docs/API.md)
- [Deployment Guide](docs/DEPLOYMENT.md)

## Contributing

This is a hackathon project. Contributions welcome after evaluation period.

## 📄 License

MIT License

## 👤 Author

**Kaushik Maram**

- GitHub: [kaushik-003](https://github.com/kaushik-003)
- Email: koushikmaram17@gmail.com

**Status**: In Development (Hackathon Project)
