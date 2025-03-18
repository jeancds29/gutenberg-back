from fastapi import APIRouter, HTTPException

router = APIRouter(
    prefix="/api/livros",
    tags=["livros"],
    responses={404: {"description": "Não encontrado"}},
)

livros = [
    {"id": 1, "titulo": "Dom Casmurro", "autor": "Machado de Assis", "ano": 1899},
    {"id": 2, "titulo": "O Cortiço", "autor": "Aluísio Azevedo", "ano": 1890},
    {"id": 3, "titulo": "Grande Sertão: Veredas", "autor": "João Guimarães Rosa", "ano": 1956},
]

@router.get("/")
async def listar_livros():
    return livros

@router.get("/{livro_id}")
async def obter_livro(livro_id: int):
    for livro in livros:
        if livro["id"] == livro_id:
            return livro
    raise HTTPException(status_code=404, detail="Livro não encontrado") 