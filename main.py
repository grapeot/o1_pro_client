from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
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
    api_key: str
    reasoning_effort: str = "low"

class ChatResponse(BaseModel):
    content: str
    total_tokens: int
    cost: float
    user_total_cost: float

def get_user(api_key: str, session: Session) -> User:
    """Get user by API key or raise 401."""
    user = session.query(User).filter(User.api_key == api_key).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return user

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    session = create_session()
    user = get_user(request.api_key, session)
    
    # Convert Pydantic models to dict for O1Client
    messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
    
    # Query O1
    response = o1_client.query(messages, request.reasoning_effort)
    
    # Update user statistics
    user.update_usage(response.token_usage.total_tokens, response.cost)
    session.commit()
    
    return ChatResponse(
        content=response.content,
        total_tokens=response.token_usage.total_tokens,
        cost=response.cost,
        user_total_cost=user.total_cost
    )

@app.get("/user/stats/{api_key}")
async def get_user_stats(api_key: str):
    session = create_session()
    user = get_user(api_key, session)
    
    return {
        "name": user.name,
        "total_tokens": user.total_tokens,
        "total_cost": user.total_cost,
        "last_used": user.last_used_at
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8011) 