import re
from dataclasses import dataclass

from app.config import get_settings
from app.services.safety_service import SafetyService


@dataclass
class GuardResult:
    allowed: bool
    revised_prompt: str
    reason: str | None = None


IMAGE_BLOCKED_PROMPTS = [
    r"jesus.*weapon|violence.*christian|crucifixion.*gore",
    r"jesus.*(gun|rifle|machine gun|pistol)",
    r"saint.*sexual|mary.*inappropriate",
    r"demonic.*christian|satanic.*cross",
]


class ImageService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.safety = SafetyService()

    async def guard_image_prompt(self, prompt: str, denomination: str, style: str) -> GuardResult:
        moderation = await self.safety.openai_moderation_check(prompt)
        if moderation.blocked:
            return GuardResult(False, "", moderation.reason)
        lowered = prompt.lower()
        for pattern in IMAGE_BLOCKED_PROMPTS:
            if re.search(pattern, lowered, re.IGNORECASE):
                return GuardResult(
                    False,
                    "",
                    "I cannot generate irreverent, sexualized, violent, or demonic Christian imagery.",
                )
        revised = (
            "Reverent, spiritually uplifting Christian artwork depicting "
            f"{prompt}. Denominational lens: {denomination}. Style: {style}. "
            "Avoid gore, mockery, sexualization, political propaganda, or sensationalism."
        )
        return GuardResult(True, revised)

    async def generate_image(
        self, prompt: str, denomination: str, style: str
    ) -> tuple[str | None, GuardResult]:
        guard = await self.guard_image_prompt(prompt, denomination, style)
        if not guard.allowed:
            return None, guard
        if not self.settings.openai_api_key:
            return None, guard
        try:
            from openai import AsyncOpenAI

            client = AsyncOpenAI(api_key=self.settings.openai_api_key)
            image = await client.images.generate(
                model=self.settings.dalle_model,
                prompt=guard.revised_prompt,
                size="1024x1024",
                quality=image_quality_for_model(self.settings.dalle_model),
                n=1,
            )
            image_data = image.data[0]
            if image_data.url:
                return image_data.url, guard
            if image_data.b64_json:
                return f"data:image/png;base64,{image_data.b64_json}", guard
            return None, GuardResult(True, guard.revised_prompt, "Image generation returned no image.")
        except Exception as exc:
            return None, GuardResult(True, guard.revised_prompt, f"Image generation failed: {exc}")


def image_quality_for_model(model: str) -> str:
    if model.startswith("dall-e-3"):
        return "hd"
    return "high"
