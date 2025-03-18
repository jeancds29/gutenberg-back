"""
LLM Integration Utilities

This module provides functions to perform text analysis
using the Groq LLM API, including character identification,
language detection, and plot summarization.
"""

import os
from groq import Groq
from dotenv import load_dotenv
import logging
import re
import json

logger = logging.getLogger(__name__)

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)
model = "llama3-70b-8192"  

def extract_json_from_response(content):
    """
    Extract valid JSON from LLM response which might contain introductory text.
    
    Args:
        content: The raw response text from the LLM
        
    Returns:
        Extracted JSON string
    """
    logger.debug("Extracting JSON from response")
    
    json_match = re.search(r'```(?:json)?\s*({[\s\S]*?})\s*```', content)
    if json_match:
        json_str = json_match.group(1)
        logger.debug(f"Found JSON in code block: {json_str[:100]}...")
        return json_str
    
    json_match = re.search(r'({[\s\S]*})', content)
    if json_match:
        json_str = json_match.group(1)
        logger.debug(f"Found JSON without code block: {json_str[:100]}...")
        return json_str
    
    logger.error(f"Could not extract JSON from response: {content[:200]}...")
    return content

def analyze_characters(title, author, text):
    """
    Identify the main characters in a book using LLM.
    
    Args:
        title: Book title
        author: Book author
        text: Book content
        
    Returns:
        JSON string containing character analysis
    """
    text_sample = text[:15000]  
    
    prompt = f"""
    Book: "{title}" by {author}

    Analyze the following text and identify the main characters of the book.
    For each character, provide:
    1. Character name
    2. Brief description
    3. Importance in the story (protagonist, main, secondary, etc.)

    Identify between 3 and 7 characters depending on the complexity of the text.
    Format the response in JSON with the structure:
    {{
        "characters": [
            {{
                "name": "Character Name",
                "description": "Brief description",
                "importance": "protagonist|main|secondary"
            }}
        ]
    }}

    IMPORTANT: Return ONLY the JSON data without any introduction or explanation.

    Sample text:
    {text_sample}
    """
    
    logger.info(f"Sending character analysis request to Groq API for book: {title}")
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an assistant specialized in literary analysis. Always respond with valid JSON only, no introductory text."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=1500
        )
        
        content = response.choices[0].message.content
        logger.info(f"Received response from Groq API. Response length: {len(content)}")
        logger.debug(f"Raw response content: {content[:500]}...")
        
        if not content.strip():
            logger.error("Received empty response from Groq API")
            return '{"characters": []}'
        
        json_content = extract_json_from_response(content)
        try:
            parsed = json.loads(json_content)
            return json.dumps(parsed)
        except json.JSONDecodeError as e:
            logger.error(f"Still invalid JSON after extraction: {e}")
            return '{"characters": []}'
            
    except Exception as e:
        logger.error(f"Error during Groq API call: {str(e)}")
        return '{"characters": []}'

def detect_language(text):
    """
    Detect the language of a text using LLM.
    
    Args:
        text: Text content to analyze
        
    Returns:
        JSON string containing language detection result
    """
    text_sample = text[:5000]  
    
    prompt = f"""
    Analyze the following text and identify which language it is written in.
    Provide the language name and the confidence level.
    Format the response in JSON with the structure:
    {{
        "language": "Language name",
        "confidence": value_between_0_and_1
    }}

    IMPORTANT: Return ONLY the JSON data without any introduction or explanation.

    Sample text:
    {text_sample}
    """
    
    logger.info("Sending language detection request to Groq API")
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an assistant specialized in linguistic analysis. Always respond with valid JSON only, no introductory text."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=150
        )
        
        content = response.choices[0].message.content
        logger.info(f"Received response from Groq API. Response length: {len(content)}")
        logger.debug(f"Raw response content: {content}")
        
        if not content.strip():
            logger.error("Received empty response from Groq API")
            return '{"language": "unknown", "confidence": 0}'
        
        json_content = extract_json_from_response(content)
        try:
            parsed = json.loads(json_content)
            return json.dumps(parsed)
        except json.JSONDecodeError as e:
            logger.error(f"Still invalid JSON after extraction: {e}")
            return '{"language": "unknown", "confidence": 0}'
            
    except Exception as e:
        logger.error(f"Error during Groq API call: {str(e)}")
        return '{"language": "unknown", "confidence": 0}'

def summarize_plot(title, author, text):
    """
    Generate a summary of a book's plot using LLM.
    
    Args:
        title: Book title
        author: Book author
        text: Book content
        
    Returns:
        JSON string containing plot summary and key events
    """
    text_sample = text[:20000]  
    
    prompt = f"""
    Book: "{title}" by {author}

    Read the following text and create a plot summary in up to 500 words.
    Additionally, list 3 to 5 key events from the story.
    
    Format the response in JSON with the structure:
    {{
        "summary": "Plot summary",
        "key_events": ["Event 1", "Event 2", "Event 3"]
    }}

    IMPORTANT: Return ONLY the JSON data without any introduction or explanation.

    Sample text:
    {text_sample}
    """
    
    logger.info(f"Sending plot summary request to Groq API for book: {title}")
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an assistant specialized in literary work summaries. Always respond with valid JSON only, no introductory text."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1000
        )
        
        content = response.choices[0].message.content
        logger.info(f"Received response from Groq API. Response length: {len(content)}")
        logger.debug(f"Raw response content: {content[:500]}...")
        
        if not content.strip():
            logger.error("Received empty response from Groq API")
            return '{"summary": "Could not generate summary", "key_events": []}'
        
        json_content = extract_json_from_response(content)
        try:
            parsed = json.loads(json_content)
            return json.dumps(parsed)
        except json.JSONDecodeError as e:
            logger.error(f"Still invalid JSON after extraction: {e}")
            return '{"summary": "Error generating summary", "key_events": []}'
            
    except Exception as e:
        logger.error(f"Error during Groq API call: {str(e)}")
        return '{"summary": "Error generating summary", "key_events": []}' 