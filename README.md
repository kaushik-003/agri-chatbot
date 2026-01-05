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
        MongoDB Memory            Pinecone Vector DB        GROQ LLM
```

## Tech Stack

- **Framework**: FastAPI
- **Agent Orchestration**: LangChain, LangGraph
- **LLM**: Groq (Llama 3.3 70B Versatile)
- **Vector Database**: Pinecone (Serverless)
- **Memory Database**: MongoDB Atlas
- **Embeddings**: sentence-transformers/all-MiniLM-L6-v2
- **Re-ranking**: cross-encoder/ms-marco-MiniLM-L-6-v2
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

## Development Workflow

1. **Phase 1-7**: Develop in Jupyter notebooks
2. **Phase 8**: Convert to production FastAPI code
3. **Deployment**: Deploy to Render/Railway

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

## API Documentation

### `POST /chat`

Primary endpoint for user interaction.

**Request Body:**

```json
{
  "query": "How do I control citrus canker?",
  "session_id": "user_123"
}
```

**Response:**

```json
{
  "answer": "To control Citrus Canker, prune infected twigs and apply Copper Oxychloride (0.3%)...\n\nSource: CitrusPlantPestsAndDiseases.pdf",
  "intent": "disease",
  "processing_time": 2.15
}
```

### `GET /health`

Health check endpoint.

**Response:**

```json
{
  "status": "active",
  "mongodb": "connected"
}
```

## Design Decisions

### 1. Vector Database Choice: Pinecone

We chose Pinecone for its serverless architecture and low latency. It allows us to manage separate namespaces for disease and scheme data effectively without managing infrastructure.

### 2. Chunking Strategy

| Parameter   | Value                        |
| ----------- | ---------------------------- |
| **Method**  | Recursive Character Splitter |
| **Size**    | 800 characters               |
| **Overlap** | 150 characters               |

**Reasoning:** This size captures full paragraphs of technical advice (e.g., a full treatment protocol) while keeping the context window focused for the LLM. The overlap prevents cutting sentences in half.

### 3. Hybrid Search Implementation

Pure vector search often fails on specific agricultural terms (e.g., chemical names like "Thiamethoxam"). We implemented **Hybrid Search**:

- **BM25**: Captures exact keyword matches
- **Cosine Similarity**: Captures conceptual meaning
- **Reciprocal Rank Fusion (RRF)**: Combines both scores to surface the best documents

## Deployment (Render)

1. Push code to GitHub
2. Create a new **Web Service** on [Render.com](https://render.com)
3. Connect your GitHub repo
4. Configure build settings:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port 10000`
5. Add **Environment Variables** in the Render dashboard:
   - `GROQ_API_KEY`
   - `PINECONE_API_KEY`
   - `MONGODB_URI`
6. Deploy! 

## Contributing

This is a hackathon project. Contributions welcome after evaluation period.

## License

MIT License

## Author

**Kaushik Maram**

- GitHub: [kaushik-003](https://github.com/kaushik-003)
- Email: koushikmaram17@gmail.com

**Status**: In Development (Hackathon Project)
