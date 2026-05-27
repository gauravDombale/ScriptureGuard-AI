import re
from dataclasses import dataclass

from app.config import get_settings
from app.services.denomination_service import get_denomination_context


@dataclass
class ModerationResult:
    allowed: bool
    blocked: bool
    reason: str | None = None
    category: str | None = None


BLOCKED_PATTERNS = [
    (r"rewrite.*bible verse.*to (support|justify|prove)", "verse_manipulation"),
    (r"rewrite.*\b[1-3]?\s?[a-z]+\s+\d+:\d+.*to (support|justify|prove)", "verse_manipulation"),
    (r"make.*scripture.*say.*", "verse_manipulation"),
    (r"modify.*verse.*", "verse_manipulation"),
    (r"modify.*(psalm|john|matthew|mark|luke|scripture|\d+:\d+).*", "verse_manipulation"),
    (r"(god|jesus|holy spirit) is (evil|fake|doesn't exist)", "toxic_theology"),
    (r"christianity is (a lie|false|wrong)", "toxic_theology"),
    (r"(kill|harm|violence).*in.*name of (god|jesus|christ)", "violence"),
    (r"(join|follow|obey).*only true church", "cult_extremism"),
    (r"ignore.*previous.*instructions", "prompt_injection"),
    (r"you are now.*", "prompt_injection"),
    (r"act as.*without.*restrictions", "prompt_injection"),
]

SENSITIVE_THEOLOGICAL_TOPICS = [
    "salvation outside christianity",
    "hell",
    "eternal damnation",
    "end times",
    "faith vs science",
    "sexual ethics",
    "abortion",
    "political theology",
]


class SafetyService:
    def __init__(self) -> None:
        self.settings = get_settings()

    async def check(self, text: str) -> ModerationResult:
        api_result = await self.openai_moderation_check(text)
        if api_result.blocked:
            return api_result
        custom_result = self.custom_theological_check(text)
        if custom_result.blocked:
            return custom_result
        return ModerationResult(allowed=True, blocked=False)

    async def openai_moderation_check(self, text: str) -> ModerationResult:
        if not self.settings.openai_api_key:
            return ModerationResult(allowed=True, blocked=False)
        try:
            from openai import AsyncOpenAI

            client = AsyncOpenAI(api_key=self.settings.openai_api_key)
            response = await client.moderations.create(input=text)
            result = response.results[0]
            scores = result.category_scores.model_dump()
            flagged = [category for category, score in scores.items() if score > 0.7]
            if flagged:
                return ModerationResult(
                    allowed=False,
                    blocked=True,
                    reason=f"OpenAI moderation flagged: {', '.join(flagged)}",
                    category="openai_moderation",
                )
        except Exception:
            return ModerationResult(allowed=True, blocked=False)
        return ModerationResult(allowed=True, blocked=False)

    def custom_theological_check(self, text: str) -> ModerationResult:
        lowered = text.lower()
        for pattern, category in BLOCKED_PATTERNS:
            if re.search(pattern, lowered, re.IGNORECASE):
                return ModerationResult(
                    allowed=False,
                    blocked=True,
                    reason=graceful_refusal(category),
                    category=category,
                )
        return ModerationResult(allowed=True, blocked=False)

    def sensitive_topic(self, text: str) -> str | None:
        lowered = text.lower()
        for topic in SENSITIVE_THEOLOGICAL_TOPICS:
            if topic in lowered:
                return topic
        return None


def graceful_refusal(category: str) -> str:
    if category == "verse_manipulation":
        return (
            "I cannot rewrite or modify Scripture to make it support a predetermined claim. "
            "I can help explain the passage in context instead."
        )
    if category == "prompt_injection":
        return "I cannot ignore the safety and grounding instructions for this assistant."
    if category == "violence":
        return "I cannot help frame violence as something done in the name of God or Christ."
    return "I cannot help with that request, but I can discuss Christian teaching respectfully."


def graceful_theological_response(topic: str, denomination: str) -> str:
    context = get_denomination_context(denomination)
    return (
        f"This is an important and complex topic. From a {context} I would approach it with "
        "care, humility, and direct attention to Scripture rather than slogans. Christians have "
        "thoughtfully debated parts of this question across traditions, so it is wise to speak "
        "with a pastor, priest, or spiritual director who knows the real people involved."
    )
