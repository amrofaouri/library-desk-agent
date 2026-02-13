from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import uuid
from server.agent import chat, get_sessions, load_chat_history

router = APIRouter()


class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    message: str


class ChatResponse(BaseModel):
    session_id: str
    response: str
    tool_calls: list


@router.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    session_id = req.session_id or str(uuid.uuid4())
    
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    try:
        result = await chat(session_id, req.message)
        return ChatResponse(
            session_id=session_id,
            response=result["response"],
            tool_calls=result["tool_calls"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/sessions")
async def list_sessions():
    return get_sessions()


@router.get("/api/sessions/{session_id}/messages")
async def get_session_messages(session_id: str):
    import sqlite3
    from server.tools import DB_PATH
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            "SELECT id, role, content, created_at FROM messages WHERE session_id = ? ORDER BY created_at ASC",
            (session_id,)
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


@router.get("/api/sessions/{session_id}/tool_calls")
async def get_session_tool_calls(session_id: str):
    import sqlite3
    from server.tools import DB_PATH
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            "SELECT id, name, args_json, result_json, created_at FROM tool_calls WHERE session_id = ? ORDER BY created_at ASC",
            (session_id,)
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()