from fastapi import APIRouter

from app.config import get_settings
from app.services.bible_corpus import load_metadata

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict:
    metadata = load_metadata()
    return {"status": "ok", "bible_verses": metadata["total_verses"]}


@router.get("/ready")
async def readiness() -> dict:
    settings = get_settings()
    metadata = load_metadata()
    checks = {
        "bible_corpus": metadata["total_verses"] > 0,
        "cors_configured": bool(settings.cors_origin_list),
        "openai_configured": bool(settings.openai_api_key),
        "pinecone_configured": bool(settings.pinecone_api_key),
        "api_key_configured": bool(settings.api_key_set),
        "rate_limit_enabled": settings.rate_limit_enabled,
        "request_size_limited": settings.max_request_body_bytes > 0,
        "secret_key_changed": settings.secret_key != "change-me",
    }
    required_checks = ["bible_corpus", "cors_configured", "rate_limit_enabled", "request_size_limited"]
    if settings.is_production:
        required_checks.extend(["api_key_configured", "secret_key_changed", "openai_configured"])
    return {
        "status": "ready" if all(checks[name] for name in required_checks) else "degraded",
        "checks": checks,
    }
