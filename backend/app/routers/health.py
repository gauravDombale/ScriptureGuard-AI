from fastapi import APIRouter

from app.services.bible_corpus import load_metadata

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict:
    metadata = load_metadata()
    return {"status": "ok", "bible_verses": metadata["total_verses"]}
