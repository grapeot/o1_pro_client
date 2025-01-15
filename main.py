from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import uvicorn
from pydantic import BaseModel

from models import User
from o1_client import O1Client
from manage import create_session

app = FastAPI()
o1_client = O1Client()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    token: str
    reasoning_effort: str = "low"

class ChatResponse(BaseModel):
    content: str
    total_tokens: int
    cost: float
    user_total_cost: float
    daily_requests: int

class UserStats(BaseModel):
    name: str
    total_tokens: int
    total_cost: float
    daily_requests: int
    usage_limit: float
    is_active: bool
    last_used: Optional[str]
    last_ip: Optional[str]

def get_user(token: str, session: Session, request: Request) -> User:
    """Get user by token or raise 401."""
    user = session.query(User).filter(User.token == token).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Check user limits
    can_proceed, message = user.check_limits()
    if not can_proceed:
        raise HTTPException(status_code=429, detail=message)
    
    return user

@app.post("/chat", response_model=ChatResponse)
async def chat(request: Request, chat_request: ChatRequest):
    session = create_session()
    user = get_user(chat_request.token, session, request)
    
    # Convert Pydantic models to dict for O1Client
    messages = [{"role": msg.role, "content": msg.content} for msg in chat_request.messages]
    
    # Query O1
    response = o1_client.query(messages, chat_request.reasoning_effort)
    
    # Update user statistics
    user.update_usage(
        tokens=response.token_usage.total_tokens,
        cost=response.cost,
        ip=request.client.host
    )
    session.commit()
    
    return ChatResponse(
        content=response.content,
        total_tokens=response.token_usage.total_tokens,
        cost=response.cost,
        user_total_cost=user.total_cost,
        daily_requests=user.daily_request_count
    )

@app.get("/user/stats/{token}", response_model=UserStats)
async def get_user_stats(token: str, request: Request):
    session = create_session()
    user = get_user(token, session, request)
    
    return UserStats(
        name=user.name,
        total_tokens=user.total_tokens,
        total_cost=user.total_cost,
        daily_requests=user.daily_request_count,
        usage_limit=user.usage_limit,
        is_active=user.is_active,
        last_used=user.last_used_at.isoformat() if user.last_used_at else None,
        last_ip=user.last_ip
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8011) 