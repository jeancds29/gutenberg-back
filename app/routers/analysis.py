"""
Analysis Router

This module provides endpoints for performing LLM-based text analysis
on books fetched from Project Gutenberg, including character identification,
language detection, and plot summarization.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import json
import logging

from app.models.database import Book, Analysis, get_db
from app.schemas.book import AnalysisRequest, CharacterAnalysis, LanguageAnalysis, PlotAnalysis
from app.utils.llm import analyze_characters, detect_language, summarize_plot

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/analysis",
    tags=["analysis"],
    responses={404: {"description": "Not found"}},
)

@router.post("/characters", response_model=CharacterAnalysis)
async def get_characters_analysis(request: AnalysisRequest, db: Session = Depends(get_db)):
    """
    Analyze the main characters of a book.
    
    Uses LLM to identify main characters, their descriptions and importance in the story.
    Results are cached in the database to avoid redundant API calls.
    
    Args:
        request: AnalysisRequest containing book_id
        
    Returns:
        CharacterAnalysis with list of characters
        
    Raises:
        404: If book not found
        500: If analysis fails
    """
    book = db.query(Book).filter(Book.book_id == request.book_id).first()
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with ID {request.book_id} not found. Download it first."
        )
    
    cached_analysis = db.query(Analysis).filter(
        Analysis.book_id == book.id,
        Analysis.analysis_type == "characters"
    ).first()
    
    if cached_analysis:
        logger.info(f"Using cached character analysis for book {book.id}")
        return cached_analysis.result
    
    logger.info(f"Performing character analysis for book {book.id}")
    try:
        result = analyze_characters(book.title, book.author, book.content)
        try:
            result_json = json.loads(result)
            
            new_analysis = Analysis(
                book_id=book.id,
                analysis_type="characters",
                result=result_json
            )
            db.add(new_analysis)
            db.commit()
            
            return result_json
        except json.JSONDecodeError as e:
            logger.error(f"JSONDecodeError in character analysis: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error processing character analysis: Invalid JSON response"
            )
    except Exception as e:
        logger.error(f"Error in character analysis: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing character analysis: {str(e)}"
        )

@router.post("/language", response_model=LanguageAnalysis)
async def get_language_analysis(request: AnalysisRequest, db: Session = Depends(get_db)):
    """
    Detect the main language of the book.
    
    Uses LLM to determine the language of the book text and confidence level.
    Results are cached in the database to avoid redundant API calls.
    
    Args:
        request: AnalysisRequest containing book_id
        
    Returns:
        LanguageAnalysis with language name and confidence score
        
    Raises:
        404: If book not found
        500: If analysis fails
    """
    book = db.query(Book).filter(Book.book_id == request.book_id).first()
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with ID {request.book_id} not found. Download it first."
        )
    
    cached_analysis = db.query(Analysis).filter(
        Analysis.book_id == book.id,
        Analysis.analysis_type == "language"
    ).first()
    
    if cached_analysis:
        logger.info(f"Using cached language analysis for book {book.id}")
        return cached_analysis.result
    
    logger.info(f"Performing language analysis for book {book.id}")
    try:
        result = detect_language(book.content)
        try:
            result_json = json.loads(result)
            
            new_analysis = Analysis(
                book_id=book.id,
                analysis_type="language",
                result=result_json
            )
            db.add(new_analysis)
            db.commit()
            
            return result_json
        except json.JSONDecodeError as e:
            logger.error(f"JSONDecodeError in language analysis: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error processing language analysis: Invalid JSON response"
            )
    except Exception as e:
        logger.error(f"Error in language analysis: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing language analysis: {str(e)}"
        )

@router.post("/plot", response_model=PlotAnalysis)
async def get_plot_analysis(request: AnalysisRequest, db: Session = Depends(get_db)):
    """
    Generate a plot summary of the book.
    
    Uses LLM to create a summary of the book's plot and identify key events.
    Results are cached in the database to avoid redundant API calls.
    
    Args:
        request: AnalysisRequest containing book_id
        
    Returns:
        PlotAnalysis with summary text and list of key events
        
    Raises:
        404: If book not found
        500: If analysis fails
    """
    book = db.query(Book).filter(Book.book_id == request.book_id).first()
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with ID {request.book_id} not found. Download it first."
        )
    
    cached_analysis = db.query(Analysis).filter(
        Analysis.book_id == book.id,
        Analysis.analysis_type == "plot"
    ).first()
    
    if cached_analysis:
        logger.info(f"Using cached plot analysis for book {book.id}")
        return cached_analysis.result
    
    logger.info(f"Performing plot analysis for book {book.id}")
    try:
        result = summarize_plot(book.title, book.author, book.content)
        try:
            result_json = json.loads(result)
            
            new_analysis = Analysis(
                book_id=book.id,
                analysis_type="plot",
                result=result_json
            )
            db.add(new_analysis)
            db.commit()
            
            return result_json
        except json.JSONDecodeError as e:
            logger.error(f"JSONDecodeError in plot analysis: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error processing plot summary: Invalid JSON response"
            )
    except Exception as e:
        logger.error(f"Error in plot analysis: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing plot summary: {str(e)}"
        ) 