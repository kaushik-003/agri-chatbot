# app/graph.py
import json
import os
import time
from pathlib import Path
from typing import List, TypedDict

import certifi  # SSL Fix
import nltk
import pypdf
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
# Logic Imports
from langgraph.graph import END, StateGraph
from nltk.tokenize import word_tokenize
from pinecone import Pinecone
from pymongo import MongoClient
from rank_bm25 import BM25Okapi
from sentence_transformers import CrossEncoder

# Load Env
load_dotenv()

# Setup Paths
BASE_DIR = Path(__file__).resolve().parent.parent # Root of project
DATA_DIR = BASE_DIR / "data"

# Download NLTK 
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt_tab')
    nltk.download('punkt')

#  LOAD CONFIGS
# We load the JSONs created in the notebooks
def load_config(filename):
    
    path = BASE_DIR / filename 
    with open(path, 'r') as f:
        return json.load(f)

config_p2 = load_config("phase2_config.json")
config_p3 = load_config("phase3_config.json")
config_p4 = load_config("phase4_config.json")
config_p5 = load_config("phase5_config.json")

#  INITIALIZE MODELS
llm = ChatGroq(
    model_name=config_p4['llm_model'],
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0,
    max_tokens=512  # Prevent runaway generation
)
embeddings = HuggingFaceEmbeddings(model_name=config_p2['embedding_model'])
reranker = CrossEncoder(config_p5['cross_encoder'])

#  CONNECT DB 
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
disease_index = pc.Index(config_p2['disease_index'])
scheme_index = pc.Index(config_p2['scheme_index'])

# MongoDB with SSL Fix - Use env variable with graceful fallback
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
conversations_col = None

try:
    if "mongodb+srv" in MONGODB_URI or "mongodb.net" in MONGODB_URI:
        mongo_client = MongoClient(
            MONGODB_URI,
            tlsCAFile=certifi.where(),
            serverSelectionTimeoutMS=5000
        )
    else:
        mongo_client = MongoClient(MONGODB_URI)
    
    db = mongo_client[config_p3['database']]
    conversations_col = db[config_p3['collections']['conversations']]
    mongo_client.admin.command('ping')
    print(" MongoDB Connected")
except Exception as e:
    print(f" MongoDB unavailable: {e}")
    print("   Running in stateless mode (no conversation memory)")

#  BUILD BM25 INDICES (Run on Startup)
print(" Building BM25 Indices...")
def build_bm25(pdf_name):
    pdf_path = DATA_DIR / pdf_name
    reader = pypdf.PdfReader(pdf_path)
    text = "".join([p.extract_text() for p in reader.pages])
    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=150)
    chunks = splitter.split_text(text)
    docs = [{"content": c, "metadata": {"source": pdf_name}} for c in chunks]
    tokenized = [word_tokenize(d['content'].lower()) for d in docs]
    return docs, BM25Okapi(tokenized)

disease_docs, bm25_disease = build_bm25("CitrusPlantPestsAndDiseases.pdf")
scheme_docs, bm25_scheme = build_bm25("GovernmentSchemes.pdf")
print(" BM25 Ready")

#  LANGGRAPH NODES 

class AgentState(TypedDict):
    question: str
    chat_history: str
    intent: str
    documents: List[dict]
    answer: str

def intent_node(state: AgentState):
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Classify query: 'disease', 'scheme', 'hybrid', 'unclear'. Return ONLY category."),
        ("user", f"History: {state['chat_history']}\nQuery: {state['question']}")
    ])
    intent = (prompt | llm | StrOutputParser()).invoke({}).strip().lower()
    if intent not in ["disease", "scheme", "hybrid", "unclear"]: intent = "unclear"
    return {"intent": intent}

def retrieval_node(state: AgentState):
    query = state['question']
    intent = state['intent']
    docs = []

    def search(index, bm25, raw_docs):
        # Semantic
        v_res = index.query(vector=embeddings.embed_query(query), top_k=5, include_metadata=True)
        sem = [{"content": m.metadata.get('text',''), "metadata": m.metadata} for m in v_res.matches]
        # Keyword
        scores = bm25.get_scores(word_tokenize(query.lower()))
        top_n = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:5]
        kw = [raw_docs[i] for i in top_n if scores[i] > 0]
        return sem + kw

    if intent in ['disease', 'hybrid']: docs.extend(search(disease_index, bm25_disease, disease_docs))
    if intent in ['scheme', 'hybrid']: docs.extend(search(scheme_index, bm25_scheme, scheme_docs))
    
    # Deduplicate & Rerank
    unique = {d['content']: d for d in docs}.values()
    if not unique: return {"documents": []}
    
    pairs = [[query, d['content']] for d in list(unique)]
    scores = reranker.predict(pairs)
    ranked = sorted(zip(list(unique), scores), key=lambda x: x[1], reverse=True)
    return {"documents": [d[0] for d in ranked[:4]]}

def generation_node(state: AgentState):
    if not state['documents']: return {"answer": "I couldn't find relevant info."}
    ctx = "\n\n".join([f"Source: {d['metadata']['source']}\n{d['content']}" for d in state['documents']])
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert Agricultural Assistant. 
Answer the user's question concisely using ONLY the context provided.
- Give a clear, direct answer in 2-4 sentences
- If asking about amounts/subsidies, extract the specific numbers
- Cite the source document at the end
- Do NOT repeat information or generate tables"""),
        ("user", f"Context:\n{ctx}\n\nQuestion: {state['question']}")
    ])
    return {"answer": (prompt | llm | StrOutputParser()).invoke({})}

def clarification_node(state: AgentState):
    return {"answer": "Could you clarify if you mean a disease or a scheme?"}

# --- 6. COMPILE GRAPH ---
workflow = StateGraph(AgentState)
workflow.add_node("classifier", intent_node)
workflow.add_node("retriever", retrieval_node)
workflow.add_node("generator", generation_node)
workflow.add_node("clarifier", clarification_node)

workflow.set_entry_point("classifier")
workflow.add_conditional_edges("classifier", lambda x: "clarifier" if x['intent']=="unclear" else "retriever")
workflow.add_edge("retriever", "generator")
workflow.add_edge("generator", END)
workflow.add_edge("clarifier", END)

app = workflow.compile()