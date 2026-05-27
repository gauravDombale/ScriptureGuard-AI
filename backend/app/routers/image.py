from fastapi import APIRouter, Depends

from app.dependencies import get_image_service, get_logging_service
from app.models.schemas import ChatRequest, ChatResponse, ImageRequest, ImageResponse
from app.services.image_service import ImageService
from app.services.logging_service import LoggingService

router = APIRouter(tags=["image"])


@router.post("/image/generate", response_model=ImageResponse)
async def generate_image(
    request: ImageRequest,
    image_service: ImageService = Depends(get_image_service),
    logger: LoggingService = Depends(get_logging_service),
) -> ImageResponse:
    image_url, guard = await image_service.generate_image(
        request.prompt, request.denomination, request.style
    )
    blocked = not guard.allowed
    if blocked:
        await logger.safety_block(
            str(request.session_id),
            request.prompt,
            guard.reason or "blocked",
            "image_safety",
        )
    return ImageResponse(
        image_url=image_url,
        revised_prompt=guard.revised_prompt,
        safety_blocked=blocked,
        block_reason=guard.reason,
    )


@router.post("/chat/image", response_model=ChatResponse)
async def chat_image_alias(
    request: ChatRequest,
    image_service: ImageService = Depends(get_image_service),
    logger: LoggingService = Depends(get_logging_service),
) -> ChatResponse:
    image_url, guard = await image_service.generate_image(
        request.message, request.denomination, "classical painting"
    )
    if not guard.allowed:
        await logger.safety_block(
            str(request.session_id), request.message, guard.reason or "blocked", "image_safety"
        )
    return ChatResponse(
        session_id=request.session_id,
        response=guard.reason if not guard.allowed else "Generated a guarded Christian image prompt.",
        image_url=image_url,
        safety_blocked=not guard.allowed,
        block_reason=guard.reason,
    )
