from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import livros

app = FastAPI(title="Gutenberg API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(livros.router)

@app.get("/")
async def root():
    return {"message": "Bem-vindo à API Gutenberg"}

@app.get("/api/health")
async def health_check():
    return {"status": "ok"} 