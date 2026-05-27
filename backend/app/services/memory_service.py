import json
from datetime import datetime, timezone

from app.config import get_settings


class MemoryService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self._client = None
        self._local: dict[str, list[dict]] = {}

    async def _redis(self):
        if self._client is not None:
            return self._client
        try:
            from redis.asyncio import from_url

            self._client = from_url(self.settings.redis_url, decode_responses=True)
            await self._client.ping()
        except Exception:
            self._client = False
        return self._client

    async def get_context(self, session_id: str) -> list[dict]:
        turns = await self._get_turns(session_id)
        return turns[-10:]

    async def history(self, session_id: str) -> list[dict]:
        return await self._get_turns(session_id)

    async def append_turn(
        self, session_id: str, role: str, content: str, metadata: dict | None = None
    ) -> None:
        turn = {
            "role": role,
            "content": content,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **(metadata or {}),
        }
        turns = await self._get_turns(session_id)
        turns.append(turn)
        turns = turns[-20:]
        redis = await self._redis()
        key = f"session:{session_id}:history"
        if redis:
            await redis.set(key, json.dumps(turns), ex=86400)
        else:
            self._local[session_id] = turns

    async def clear_session(self, session_id: str) -> None:
        redis = await self._redis()
        if redis:
            await redis.delete(f"session:{session_id}:history")
        self._local.pop(session_id, None)

    async def _get_turns(self, session_id: str) -> list[dict]:
        redis = await self._redis()
        if redis:
            raw = await redis.get(f"session:{session_id}:history")
            return json.loads(raw) if raw else []
        return self._local.get(session_id, [])
