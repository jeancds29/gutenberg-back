"""
Book and Analysis Schemas

This module defines Pydantic models for request and response validation
for book data and analysis results.
"""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class BookBase(BaseModel):
    """Base schema with common book fields."""
    book_id: str
    
class BookCreate(BookBase):
    """Schema for creating a new book (currently unused)."""
    pass

class BookResponse(BookBase):
    """Schema for book responses in list view."""
    id: int
    title: Optional[str] = None
    author: Optional[str] = None
    language: Optional[str] = None
    download_count: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class BookDetail(BookResponse):
    """Schema for detailed book view including content."""
    content: Optional[str] = None
    
    class Config:
        from_attributes = True

class AnalysisRequest(BaseModel):
    """Schema for requesting a text analysis."""
    book_id: str
    analysis_type: str  

class Character(BaseModel):
    """Schema for a book character."""
    name: str
    description: str
    importance: str 

class CharacterAnalysis(BaseModel):
    """Schema for character analysis results."""
    characters: List[Character]

class LanguageAnalysis(BaseModel):
    """Schema for language detection results."""
    language: str
    confidence: float

class PlotAnalysis(BaseModel):
    """Schema for plot summary results."""
    summary: str
    key_events: List[str] 