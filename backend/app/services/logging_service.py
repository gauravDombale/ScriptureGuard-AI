import logging

from app.config import get_settings
from app.models.db_models import Base, ConversationLog, SafetyBlockLog

logger = logging.getLogger(__name__)


class LoggingService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self._sessionmaker = None

    async def _session_factory(self):
        if self._sessionmaker is not None:
            return self._sessionmaker
        try:
            from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

            engine = create_async_engine(self.settings.database_url, pool_pre_ping=True)
            if self.settings.auto_create_tables:
                async with engine.begin() as conn:
                    await conn.run_sync(Base.metadata.create_all)
            self._sessionmaker = async_sessionmaker(engine, expire_on_commit=False)
        except Exception:
            logger.exception("Database logging initialization failed; continuing without DB logs")
            self._sessionmaker = False
        return self._sessionmaker

    async def safety_block(
        self, session_id: str, input_text: str, block_reason: str, block_category: str
    ) -> None:
        factory = await self._session_factory()
        if not factory:
            return
        try:
            async with factory() as session:
                session.add(
                    SafetyBlockLog(
                        session_id=session_id,
                        input_text=input_text,
                        block_reason=block_reason,
                        block_category=block_category,
                    )
                )
                await session.commit()
        except Exception:
            logger.exception("Failed to persist safety block log")

    async def conversation(self, session_id: str, role: str, content: str, payload: dict) -> None:
        factory = await self._session_factory()
        if not factory:
            return
        try:
            async with factory() as session:
                session.add(
                    ConversationLog(
                        session_id=session_id,
                        role=role,
                        content=content,
                        payload=payload,
                    )
                )
                await session.commit()
        except Exception:
            logger.exception("Failed to persist conversation log")
