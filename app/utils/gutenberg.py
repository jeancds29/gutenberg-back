"""
Project Gutenberg Utilities

This module provides functions to fetch book content and metadata
from Project Gutenberg's website.
"""

import requests
from bs4 import BeautifulSoup
import re
import logging

logger = logging.getLogger(__name__)

MAX_CONTENT_SIZE = 8 * 1024 * 1024  # 8MB

def fetch_book_content(book_id):
    """
    Fetch book content by ID from Project Gutenberg.
    
    Args:
        book_id: The Project Gutenberg book ID
        
    Returns:
        The book content as text, or None if not found
    """
    urls = [
        f"https://www.gutenberg.org/files/{book_id}/{book_id}-0.txt",
        f"https://www.gutenberg.org/files/{book_id}/{book_id}.txt",
        f"https://www.gutenberg.org/cache/epub/{book_id}/pg{book_id}.txt"
    ]
    
    for url in urls:
        try:
            logger.info(f"Attempting to fetch book content from {url}")
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                content = response.text
                
                if len(content.encode('utf-8')) > MAX_CONTENT_SIZE:
                    logger.warning(f"Book {book_id} content exceeds maximum size. Truncating.")
                    content = content[:7500000]
                
                return content
        except requests.RequestException as e:
            logger.error(f"Error fetching from {url}: {str(e)}")
    
    logger.error(f"Failed to fetch content for book ID {book_id}")
    return None

def fetch_book_metadata(book_id):
    """
    Fetch book metadata by ID from Project Gutenberg.
    
    Args:
        book_id: The Project Gutenberg book ID
        
    Returns:
        Dictionary containing metadata (title, author, language, download_count)
        or None if not found
    """
    url = f"https://www.gutenberg.org/ebooks/{book_id}"
    
    try:
        logger.info(f"Fetching metadata from {url}")
        response = requests.get(url, timeout=30)
        
        if response.status_code != 200:
            logger.error(f"Failed to fetch metadata for book ID {book_id}: Status {response.status_code}")
            return None
        
        soup = BeautifulSoup(response.text, 'lxml')
        metadata = {}
        
        title_elem = soup.select_one('h1')
        if title_elem:
            metadata['title'] = title_elem.text.strip()
        
        author_elem = soup.select_one('a[itemprop="creator"]')
        if author_elem:
            metadata['author'] = author_elem.text.strip()
        
        language_elem = soup.select_one('tr:has(th:-soup-contains("Language")) td')
        if language_elem:
            metadata['language'] = language_elem.text.strip()
        
        downloads_elem = soup.select_one('td[itemprop="interactionCount"]')
        if downloads_elem:
            downloads_text = downloads_elem.text.strip()
            downloads_match = re.search(r'\d+', downloads_text)
            if downloads_match:
                metadata['download_count'] = int(downloads_match.group())
        
        return metadata
    except requests.RequestException as e:
        logger.error(f"Error fetching metadata for book ID {book_id}: {str(e)}")
        return None

def get_book_data(book_id):
    """
    Fetch both content and metadata for a book from Project Gutenberg.
    
    Args:
        book_id: The Project Gutenberg book ID
        
    Returns:
        Dictionary containing book data (title, author, language, download_count, content)
        or None if either content or metadata couldn't be fetched
    """
    content = fetch_book_content(book_id)
    metadata = fetch_book_metadata(book_id)
    
    if content is None or metadata is None:
        return None
    
    return {**metadata, 'content': content, 'book_id': book_id} 