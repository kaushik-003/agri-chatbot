# main.py
import time

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.graph import app as agent_app
from app.graph import conversations_col

#  Setup App
app = FastAPI(
    title="Agri-Chatbot API",
    description="Agentic RAG for Citrus Diseases & Schemes",
    version="1.0.0"
)

#  Pydantic Models (Input/Output format)
class ChatRequest(BaseModel):
    query: str
    session_id: str = "default_user"

class ChatResponse(BaseModel):
    answer: str
    intent: str
    processing_time: float

# 3. API Endpoint
@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    start_time = time.time()
    
    # Get History (if MongoDB available)
    history = ""
    if conversations_col is not None:
        try:
            hist_doc = conversations_col.find_one({"session_id": request.session_id})
            if hist_doc:
                history = "\n".join([f"{m['role']}: {m['content']}" for m in hist_doc['messages'][-4:]])
        except Exception:
            pass
    
    # Run Agent
    try:
        inputs = {
            "question": request.query,
            "chat_history": history,
            "intent": "", "documents": [], "answer": ""
        }
        result = agent_app.invoke(inputs)
        
        # Save Interaction (if MongoDB available)
        if conversations_col is not None:
            try:
                conversations_col.update_one(
                    {"session_id": request.session_id},
                    {"$push": {"messages": {"$each": [
                        {"role": "user", "content": request.query, "timestamp": time.time()},
                        {"role": "assistant", "content": result['answer'], "timestamp": time.time()}
                    ]}}},
                    upsert=True
                )
            except Exception:
                pass
        
        return ChatResponse(
            answer=result['answer'],
            intent=result.get('intent', 'unknown'),
            processing_time=time.time() - start_time
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    mongo_status = "connected" if conversations_col is not None else "unavailable (stateless)"
    return {"status": "active", "mongodb": mongo_status}

#  Run Server (If run directly)
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)