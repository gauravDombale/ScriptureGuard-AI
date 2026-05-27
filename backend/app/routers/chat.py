import json
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.dependencies import get_chat_pipeline, get_logging_service, get_memory_service
from app.models.schemas import ChatRequest, ChatResponse, HistoryResponse, HistoryTurn
from app.pipelines.chat_pipeline import ChatPipeline
from app.services.logging_service import LoggingService
from app.services.memory_service import MemoryService

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    pipeline: ChatPipeline = Depends(get_chat_pipeline),
    logger: LoggingService = Depends(get_logging_service),
) -> ChatResponse:
    response = await pipeline.run(request.session_id, request.message, request.denomination)
    await logger.conversation(
        str(request.session_id),
        "user",
        request.message,
        {"denomination": request.denomination, "mode": request.mode},
    )
    await logger.conversation(
        str(request.session_id),
        "assistant",
        response.response,
        response.model_dump(mode="json"),
    )
    if response.safety_blocked:
        await logger.safety_block(
            str(request.session_id),
            request.message,
            response.block_reason or "blocked",
            "chat_safety",
        )
    return response


@router.post("/chat/stream")
async def chat_stream(
    request: ChatRequest,
    pipeline: ChatPipeline = Depends(get_chat_pipeline),
    logger: LoggingService = Depends(get_logging_service),
) -> StreamingResponse:
    async def events():
        final_event: dict | None = None
        async for event in pipeline.stream(
            request.session_id, request.message, request.denomination
        ):
            if event.get("type") == "final":
                final_event = event
            yield f"event: {event['type']}\ndata: {json.dumps(event)}\n\n"

        if final_event:
            await logger.conversation(
                str(request.session_id),
                "user",
                request.message,
                {"denomination": request.denomination, "mode": request.mode, "stream": True},
            )
            await logger.conversation(
                str(request.session_id),
                "assistant",
                str(final_event.get("response") or ""),
                final_event,
            )
            if final_event.get("safety_blocked"):
                await logger.safety_block(
                    str(request.session_id),
                    request.message,
                    str(final_event.get("block_reason") or "blocked"),
                    "chat_safety",
                )

    return StreamingResponse(
        events(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-transform",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/chat/history/{session_id}", response_model=HistoryResponse)
async def history(
    session_id: UUID, memory: MemoryService = Depends(get_memory_service)
) -> HistoryResponse:
    turns = await memory.history(str(session_id))
    normalized = [
        HistoryTurn(
            role=turn["role"],
            content=turn["content"],
            timestamp=turn["timestamp"],
            citations=turn.get("citations", []),
        )
        for turn in turns
    ]
    return HistoryResponse(session_id=session_id, turns=normalized)
