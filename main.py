"""
Gutenberg API - Main Application

This application provides a REST API for exploring and analyzing books from Project Gutenberg.
It allows fetching books by ID, storing them locally, and analyzing their content using Groq LLM.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import logging
import sys

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

database_url = os.environ.get("DATABASE_URL")
groq_api_key = os.environ.get("GROQ_API_KEY")

if not database_url:
    logger.critical("DATABASE_URL environment variable is not set! Application will likely fail.")
else:
    safe_url = database_url.replace("://", "://***:***@")
    logger.info(f"DATABASE_URL found: {safe_url}")

if not groq_api_key:
    logger.warning("GROQ_API_KEY environment variable is not set! Text analysis features will not work.")
else:
    logger.info("GROQ_API_KEY found and configured")

from app.routers import books, analysis
from app.models.database import create_tables, test_database_connection

logger.info("Testing database connection...")
if not test_database_connection():
    logger.critical("Failed to connect to the database. Exiting application.")
    sys.exit(1)

logger.info("Initializing database...")
try:
    create_tables()
    logger.info("Database initialized successfully")
except Exception as e:
    logger.critical(f"Failed to initialize database: {str(e)}")
    raise

app = FastAPI(
    title="Gutenberg API",
    description="API for exploring and analyzing books from Project Gutenberg",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(books.router)
app.include_router(analysis.router)

@app.get("/")
async def root():
    """Root endpoint returning a welcome message."""
    return {"message": "Welcome to the Gutenberg API"}

@app.get("/api/health")
async def health_check():
    """Health check endpoint for monitoring."""
    db_connected = test_database_connection()
    status = "ok" if db_connected else "database_error"
    
    return {
        "status": status,
        "database": "connected" if db_connected else "disconnected",
        "api": "ok"
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "0.0.0.0")
    
    logger.info(f"Starting server on {host}:{port}")
    uvicorn.run(
        "main:app", 
        host=host, 
        port=port, 
        reload=True,
        workers=4,
        timeout_keep_alive=120,
        limit_concurrency=100,
        limit_max_requests=10000
    ) 