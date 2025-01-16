from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import QueuePool

DATABASE_URL = "sqlite:///o1_chat.db"

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=5,  # Base number of connections
    max_overflow=10,  # Maximum number of connections above pool_size
    pool_timeout=30,  # Timeout in seconds for getting a connection from the pool
    pool_recycle=1800,  # Recycle connections after 30 minutes
    pool_pre_ping=True  # Enable connection health checks
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def init_db():
    """Initialize the database, creating all tables."""
    Base.metadata.create_all(bind=engine)

def get_session() -> Session:
    """Get a new database session."""
    return SessionLocal() 