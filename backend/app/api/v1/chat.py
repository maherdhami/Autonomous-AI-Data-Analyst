import time
import uuid
from typing import Optional
from fastapi import APIRouter, Depends
from app.schemas.chat import ChatRequest, ChatResponse, ChatMessage
from app.schemas.auth import UserResponse
from app.schemas.common import ResponseModel
from app.middleware.auth_middleware import get_current_user
from app.services.chat_service import chat_service
from app.api.v1.analysis import get_dataframe
from app.utils.data_processing import extract_summary

router = APIRouter()

# In-memory chat history: session_id -> list of messages
_chat_memory: dict = {}


@router.post("", response_model=ResponseModel[ChatResponse])
@router.post("/", response_model=ResponseModel[ChatResponse])
@router.post("/query", response_model=ResponseModel[ChatResponse])
async def chat_with_analyst(req: ChatRequest, current_user: UserResponse = Depends(get_current_user)):
    """AI Copilot Chat."""
    session_id = req.session_id or f"ses_{uuid.uuid4().hex[:12]}"
    now = int(time.time())

    # Load dataset if file_id provided
    df = get_dataframe(req.file_id) if req.file_id else get_dataframe()

    # Get dataset summary
    summary = extract_summary(df) if df is not None else {}

    # Generate answer
    if req.mode == "code" and df is not None:
        code, result = chat_service.run_code(df, req.question)
        reply = f"**Result:** `{result}`\n\n**Code:**\n```python\n{code}\n```"
        code_out = code
        exec_res = str(result)
    else:
        reply = chat_service.answer_question(summary, df, req.question)
        code_out = None
        exec_res = None

    # Save to in-memory history
    if session_id not in _chat_memory:
        _chat_memory[session_id] = []
    _chat_memory[session_id].append({"role": "user", "content": req.question, "timestamp": now - 1})
    _chat_memory[session_id].append({"role": "assistant", "content": reply, "timestamp": now})

    msg = ChatMessage(role="assistant", content=reply, code=code_out, execution_result=exec_res, timestamp=now)
    return ResponseModel(success=True, message="OK", data=ChatResponse(session_id=session_id, message=msg))


@router.get("/messages", response_model=ResponseModel[list])
@router.get("/history", response_model=ResponseModel[list])
async def get_chat_history(session_id: Optional[str] = None, current_user: UserResponse = Depends(get_current_user)):
    """Get chat history for a session."""
    if session_id:
        msgs = _chat_memory.get(session_id, [])
    else:
        msgs = [m for session in _chat_memory.values() for m in session]
        msgs = sorted(msgs, key=lambda x: x.get("timestamp", 0))

    result = [ChatMessage(
        role=m["role"],
        content=m["content"],
        code=m.get("code"),
        execution_result=m.get("execution_result"),
        timestamp=m["timestamp"]
    ) for m in msgs]

    return ResponseModel(success=True, message="OK", data=result)


@router.delete("/messages", response_model=ResponseModel[bool])
@router.delete("/history", response_model=ResponseModel[bool])
async def clear_chat_history(session_id: Optional[str] = None, current_user: UserResponse = Depends(get_current_user)):
    """Clear chat history."""
    if session_id:
        _chat_memory.pop(session_id, None)
    else:
        _chat_memory.clear()
    return ResponseModel(success=True, message="Chat cleared", data=True)