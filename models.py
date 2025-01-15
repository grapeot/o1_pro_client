from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.sql import func
from datetime import datetime, timedelta

from database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    token = Column(String(8), unique=True, nullable=False)  # 8-char token
    is_active = Column(Boolean, default=True)
    total_tokens = Column(Integer, default=0)
    total_cost = Column(Float, default=0.0)
    created_at = Column(DateTime, default=func.now())
    last_used_at = Column(DateTime, default=func.now(), onupdate=func.now())
    last_ip = Column(String)
    daily_request_count = Column(Integer, default=0)
    last_request_date = Column(DateTime)
    usage_limit = Column(Float, default=1000.0)  # Default $1000 limit

    def update_usage(self, tokens: int, cost: float, ip: str = None):
        """Update the user's token usage and cost."""
        self.total_tokens += tokens
        self.total_cost += cost
        self.last_used_at = datetime.utcnow()
        if ip:
            self.last_ip = ip

    def update_request_count(self):
        """Update daily request count. Returns True if rate limit not exceeded."""
        now = datetime.utcnow()
        
        # Reset counter if it's a new day
        if not self.last_request_date or self.last_request_date.date() != now.date():
            self.daily_request_count = 0
            self.last_request_date = now
        
        # Increment counter
        self.daily_request_count += 1
        
        # Check if we're within rate limit (100 requests per day)
        return self.daily_request_count <= 100

    def check_limits(self) -> tuple[bool, str]:
        """Check if user can make requests. Returns (can_proceed, message)."""
        if not self.is_active:
            return False, "User account is inactive"
        
        if self.total_cost >= self.usage_limit:
            return False, f"Usage limit (${self.usage_limit:.2f}) exceeded"
            
        if not self.update_request_count():
            return False, "Daily request limit (100) exceeded"
            
        return True, "OK" 