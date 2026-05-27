from app.config import get_settings
from app.models.db_models import Base, ConversationLog, SafetyBlockLog


class LoggingService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self._sessionmaker = None

    async def _session_factory(self):
        if self._sessionmaker is not None:
            return self._sessionmaker
        try:
            from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

            engine = create_async_engine(self.settings.database_url)
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            self._sessionmaker = async_sessionmaker(engine, expire_on_commit=False)
        except Exception:
            self._sessionmaker = False
        return self._sessionmaker

    async def safety_block(
        self, session_id: str, input_text: str, block_reason: str, block_category: str
    ) -> None:
        factory = await self._session_factory()
        if not factory:
            return
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

    async def conversation(self, session_id: str, role: str, content: str, payload: dict) -> None:
        factory = await self._session_factory()
        if not factory:
            return
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
