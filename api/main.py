import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.capstone_agent import chat, clear_session, list_sessions

app = FastAPI(
    title="TechFlow AI Support Agent",
    description="RAG-powered AI agent with conversation memory, "
                "tool use, and LangGraph orchestration.",
    version="1.0.0"
)


# ── REQUEST / RESPONSE MODELS ──────────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"


class ChatResponse(BaseModel):
    response: str
    session_id: str


class SessionInfo(BaseModel):
    active_sessions: list[str]
    count: int


# ── ENDPOINTS ──────────────────────────────────────────────────────────────────

@app.get("/health")
def health_check():
    """Confirm the API is running."""
    return {"status": "ok", "service": "TechFlow AI Support Agent"}


@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    """
    Send a message to the AI agent.
    The agent maintains conversation history per session_id.
    Omit session_id to use the default session.
    """
    try:
        response = chat(
            message=request.message,
            session_id=request.session_id
        )
        return ChatResponse(
            response=response,
            session_id=request.session_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/session/{session_id}")
def clear_session_endpoint(session_id: str):
    """
    Clear conversation history for a specific session.
    Use this to start a fresh conversation without creating a new session_id.
    """
    cleared = clear_session(session_id)
    if cleared:
        return {"cleared": True, "session_id": session_id}
    raise HTTPException(
        status_code=404,
        detail=f"Session '{session_id}' not found."
    )


@app.get("/sessions", response_model=SessionInfo)
def list_sessions_endpoint():
    """List all active session IDs and count."""
    active = list_sessions()
    return SessionInfo(active_sessions=active, count=len(active))