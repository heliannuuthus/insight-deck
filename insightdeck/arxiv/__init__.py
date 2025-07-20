from arxiv import Client
from fastapi import APIRouter

client = Client()

router = APIRouter(prefix="/arxiv", tags=["arxiv"])


@router.get("/search")
async def search_arxiv(query: str):
    return
