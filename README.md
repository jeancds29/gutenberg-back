# Project Gutenberg API

REST API developed with FastAPI for exploring and analyzing books from Project Gutenberg.

## Features

- Fetch and display books from Project Gutenberg by ID
- Store texts and metadata for future access
- Text analysis using LLM (Groq):
  - Identification of main characters
  - Language detection
  - Plot summarization
- Caching system for LLM analyses
- Error handling and logging
- Content size management for large books

## Requirements

- Python 3.8+
- FastAPI
- SQLAlchemy
- PostgreSQL
- Groq (for LLM text analysis)

## Setup

1. Clone the repository
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create an `.env` file from `.env.example`:

```bash
cp .env.example .env
```

4. Edit the `.env` file and add your Groq API key:

```
GROQ_API_KEY=your_groq_api_key_here
```

5. Configure the PostgreSQL database:

The application is configured to use PostgreSQL. Make sure your `.env` file has the correct PostgreSQL connection string:

```
DATABASE_URL=your_postgresql_connection_string
```

## Advanced Configuration

### Server Performance

The application includes advanced server configurations in `main.py`:

- Multiple workers for handling concurrent requests
- Connection timeout settings
- Concurrency limits
- Request limits for worker recycling

These settings can be adjusted based on your deployment environment.

### Content Management

For very large books, the system will automatically truncate content to 7.5MB to prevent database issues.

### Analysis Caching

All LLM analyses are cached in the database to improve performance and reduce API costs when requesting the same analysis multiple times.

## Running the project

To start the development server:

```bash
uvicorn main:app --reload
```

The server will be available at `http://localhost:8000`

For production deployment:

```bash
python main.py
```

This will use the optimized server configuration with multiple workers.

## API Documentation

Interactive API documentation is available at:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Available Endpoints

### Books

- GET `/api/books`: List all saved books
- GET `/api/books/{book_id}`: Get a specific book by Project Gutenberg ID

### Text Analysis

- POST `/api/analysis/characters`: Identify main characters in the book
- POST `/api/analysis/language`: Detect the book's language
- POST `/api/analysis/plot`: Generate a plot summary

## Integrating with Frontend

To connect a frontend to this API, configure CORS in the `main.py` file with the allowed domains to access the API. 