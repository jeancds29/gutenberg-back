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


DATABASE_URL = os.environ.get("DATABASE_URL")


if DATABASE_URL:
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
        logger.info("Fixed PostgreSQL URL prefix from 'postgres://' to 'postgresql://'")
        
    safe_url = DATABASE_URL.replace("://", "://***:***@")
    logger.info(f"Database URL found: {safe_url}")
else:
    logger.error("DATABASE_URL environment variable is not set!")
    raise ValueError("DATABASE_URL environment variable is required")

ssl_mode = os.environ.get("PGSQL_SSL_MODE", "require")
use_ssl = os.environ.get("USE_DATABASE_SSL", "true").lower() == "true"

connect_args = {"connect_timeout": 10}

if use_ssl:
    connect_args.update({
        "sslmode": ssl_mode,
    })
    logger.info(f"Using SSL for database connection with SSL mode: {ssl_mode}")

try:
    engine = create_engine(
        DATABASE_URL,
        pool_size=5,                
        max_overflow=10,            
        pool_timeout=30,            
        pool_recycle=1800,          
        pool_pre_ping=True,         
        connect_args=connect_args    
    )
    logger.info("Database engine created successfully")
except Exception as e:
    logger.error(f"Failed to create database engine: {str(e)}")
    raise


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

def test_database_connection():
    """
    Test the database connection.
    
    Returns:
        bool: True if connection is successful, False otherwise
    """
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        logger.info("✅ Database connection test successful!")
        return True
    except Exception as e:
        logger.error(f"❌ Database connection test failed: {str(e)}")
        safe_url = DATABASE_URL.replace("://", "://***:***@") if DATABASE_URL else "None"
        logger.error(f"Connection details: {safe_url}")
        logger.error(f"SSL enabled: {use_ssl}, SSL mode: {ssl_mode}")
        
        if "could not connect to server" in str(e).lower():
            logger.error("Network connectivity issue - check if DB server is accessible from Railway")
        elif "password authentication failed" in str(e).lower():
            logger.error("Authentication failed - check username/password")
        elif "does not exist" in str(e).lower():
            logger.error("Database does not exist - check database name")
        elif "ssl" in str(e).lower():
            logger.error("SSL issue - try setting USE_DATABASE_SSL=false if your provider doesn't support SSL")
        
        return False

def create_tables():
    """Create all database tables if they don't exist."""
    try:
        if not test_database_connection():
            raise Exception("Could not connect to database, cannot create tables")
            
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