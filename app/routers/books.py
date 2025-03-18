"""
Books Router

This module provides endpoints for fetching and managing books from Project Gutenberg.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.models.database import Book, get_db
from app.schemas.book import BookResponse, BookDetail
from app.utils.gutenberg import get_book_data

router = APIRouter(
    prefix="/api/books",
    tags=["books"],
    responses={404: {"description": "Not found"}},
)

@router.get("/", response_model=List[BookResponse])
async def list_books(db: Session = Depends(get_db)):
    """
    List all saved books.
    
    Returns a list of all books that have been previously fetched and saved,
    ordered by most recently added first.
    """
    books = db.query(Book).order_by(Book.created_at.desc()).all()
    return books

@router.get("/{book_id}", response_model=BookDetail)
async def get_book(book_id: str, db: Session = Depends(get_db)):
    """
    Get a specific book by Project Gutenberg ID.
    
    If the book exists in the database, it is returned directly.
    If not, it's fetched from Project Gutenberg, saved to the database, and then returned.
    
    Args:
        book_id: The Project Gutenberg ID of the book
        
    Returns:
        Book details including content
        
    Raises:
        404: If book cannot be found on Project Gutenberg
    """
    book = db.query(Book).filter(Book.book_id == book_id).first()
    
    if not book:
        book_data = get_book_data(book_id)
        if not book_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Book with ID {book_id} not found in Project Gutenberg"
            )
        
        book = Book(
            book_id=book_id,
            title=book_data.get('title'),
            author=book_data.get('author'),
            language=book_data.get('language'),
            download_count=book_data.get('download_count'),
            content=book_data.get('content')
        )
        db.add(book)
        db.commit()
        db.refresh(book)
    
    return book 