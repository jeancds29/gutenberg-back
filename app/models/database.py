"""
Database models and connection configuration.

This module defines the SQLAlchemy models and database connection setup
for the Gutenberg API project using PostgreSQL.
"""

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, JSON, ForeignKey, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import datetime
import os
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

load_dotenv()

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

logger.info("Connecting to database...")
engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Book(Base):
    """
    Book model representing a book from Project Gutenberg.
    
    Stores book metadata and content fetched from Project Gutenberg.
    """
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(String, unique=True, index=True)
    title = Column(String)
    author = Column(String)
    language = Column(String)
    download_count = Column(Integer)
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    analyses = relationship("Analysis", back_populates="book", cascade="all, delete-orphan")

class Analysis(Base):
    """
    Analysis model for caching LLM analysis results.
    
    Each analysis is linked to a book and has a specific type
    (characters, language, plot) and stores the result as JSON.
    """
    __tablename__ = "analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id"))
    analysis_type = Column(String, index=True)  
    result = Column(JSON)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    book = relationship("Book", back_populates="analyses")
    
    __table_args__ = (
        UniqueConstraint('book_id', 'analysis_type', name='uix_analysis_book_type'),
    )

def create_tables():
    """Create all database tables if they don't exist."""
    try:
        logger.info("Creating database tables if they don't exist...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables successfully created/verified")
    except Exception as e:
        logger.error(f"Error creating database tables: {str(e)}")
        raise

def get_db():
    """
    Dependency for FastAPI endpoints to get a database session.
    
    Yields a session and ensures it's closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 