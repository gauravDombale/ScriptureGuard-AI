from functools import lru_cache

from app.pipelines.chat_pipeline import ChatPipeline
from app.services.image_service import ImageService
from app.services.logging_service import LoggingService
from app.services.memory_service import MemoryService


@lru_cache
def get_memory_service() -> MemoryService:
    return MemoryService()


@lru_cache
def get_chat_pipeline() -> ChatPipeline:
    return ChatPipeline(memory=get_memory_service())


@lru_cache
def get_image_service() -> ImageService:
    return ImageService()


@lru_cache
def get_logging_service() -> LoggingService:
    return LoggingService()
