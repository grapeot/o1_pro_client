from sqlalchemy import Column, Integer, String, Float, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    api_key = Column(String, unique=True, nullable=False)
    total_tokens = Column(Integer, default=0)
    total_cost = Column(Float, default=0.0)
    created_at = Column(DateTime, default=func.now())
    last_used_at = Column(DateTime, default=func.now(), onupdate=func.now())

    def update_usage(self, tokens: int, cost: float):
        """Update the user's token usage and cost."""
        self.total_tokens += tokens
        self.total_cost += cost
        self.last_used_at = datetime.utcnow()

# Create database
engine = create_engine('sqlite:///o1_chat.db')
Base.metadata.create_all(engine) 