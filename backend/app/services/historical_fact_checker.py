from dataclasses import dataclass

from app.config import get_settings


@dataclass
class FactCheckResult:
    text: str
    flagged: bool = False


class HistoricalFactChecker:
    def __init__(self) -> None:
        self.settings = get_settings()

    async def check(self, text: str) -> FactCheckResult:
        if not self.settings.openai_api_key:
            return FactCheckResult(text=text)
        # In production this can be expanded into an LLM-as-judge pass. The pipeline keeps it
        # as a dedicated node so historical checking remains separable from scripture validation.
        return FactCheckResult(text=text)
