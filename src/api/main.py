from fastapi import FastAPI
from pydantic import BaseModel
from src.Rag.app import ask_edin

# 1. Initialize the API
app = FastAPI(title="EDin RAG API", description="AI Backend for NEET Advisory")

# 2. Define the Request Schema (What the user sends)
class QuestionRequest(BaseModel):
    question: str

# 3. Define the POST Route
@app.post("/ask")
def ask_question(request: QuestionRequest):
    """
    Exposes the EDin RAG logic as a web service.
    Receives a JSON question, returns the verified RAG answer.
    """
    # Calls your existing function from src/Rag/app.py
    result = ask_edin(request.question)
    return result

# 4. Root endpoint for a quick health check
@app.get("/")
def health_check():
    return {"status": "online", "system": "EDin RAG API"}