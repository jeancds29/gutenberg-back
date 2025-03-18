"""
Gutenberg API - Main Application

This application provides a REST API for exploring and analyzing books from Project Gutenberg.
It allows fetching books by ID, storing them locally, and analyzing their content using Groq LLM.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import logging

from app.routers import books, analysis
from app.models.database import create_tables

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

logger.info("Initializing database...")
create_tables()

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
    return {"status": "ok"}

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