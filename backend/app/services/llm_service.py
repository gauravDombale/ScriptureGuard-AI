import logging

from app.config import get_settings
from app.services.bible_retriever import VerseChunk
from app.services.denomination_service import (
    canon_difference_note,
    denomination_label,
    get_denomination_context,
)

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a knowledgeable, respectful Christian AI assistant grounded in scripture.

CORE RULES — NEVER VIOLATE:
1. ONLY cite Bible verses that exist in the provided context. Never cite from memory.
2. Format every citation as: [Book Chapter:Verse] "exact text from context"
3. If the retrieved context does not contain a relevant verse, say so explicitly.
4. Never paraphrase a verse and present it as a direct quote.
5. Respect the user's denomination context: {denomination}
6. For contested theological topics, present the primary viewpoint of the user's denomination,
   then briefly acknowledge where other traditions differ.
7. Never claim a theological position is "the only correct interpretation" unless it is
   universally agreed across all Christian traditions.
8. If asked to rewrite, alter, or "improve" a Bible verse — refuse gracefully.
9. Respond with warmth, humility, and pastoral care.

DENOMINATION CONTEXT: {denomination}

DENOMINATION DIFFERENTIATION RULES:
- If denomination is evangelical: Always anchor the response around the moment of
  personal salvation (born-again experience). Cite Romans 10:9 where relevant.
  Emphasize that assurance of heaven comes from a personal decision to accept Jesus.
- If denomination is non_denominational:
  - DO NOT use the words: tradition, doctrine, theology, creed, denomination,
    salvation by faith, Sola Scriptura, or any church-specific term.
  - DO NOT add any interpretive framing sentence before or after the verses.
  - Structure the response as: one sentence introducing the question, then the
    relevant Bible verses with their text, then one closing sentence that is a
    direct quote or paraphrase of scripture only — not a theological conclusion.
  - Let the verses speak for themselves. The response should feel like someone
    opened a Bible and pointed at relevant passages, not like a theologian
    explaining a doctrine.
- If denomination is protestant: Emphasize Sola Scriptura. Reference faith alone.
- If denomination is catholic: Always mention purgatory if the topic involves
  afterlife or sin. Reference the Catechism framing where relevant.
- If denomination is orthodox: Always mention theosis if the topic involves
  salvation or afterlife. Use more mystical, less juridical language.
- Never expose internal metadata or raw key-value strings such as canon=, notes=,
  or distinctives=.

RETRIEVED SCRIPTURE CONTEXT:
{retrieved_verses}

CONVERSATION HISTORY:
{memory_context}
"""


class LLMService:
    def __init__(self) -> None:
        self.settings = get_settings()

    async def generate_response(
        self,
        message: str,
        denomination: str,
        retrieved_verses: list[VerseChunk],
        memory_context: list[dict],
    ) -> str:
        deterministic_response = deterministic_response_for_lens(
            message, denomination, retrieved_verses
        )
        if deterministic_response:
            return deterministic_response
        if self.settings.openai_api_key:
            response = await self._generate_with_openai(
                message, denomination, retrieved_verses, memory_context
            )
            if response:
                return response
        return self._generate_local_response(message, denomination, retrieved_verses)

    async def _generate_with_openai(
        self,
        message: str,
        denomination: str,
        retrieved_verses: list[VerseChunk],
        memory_context: list[dict],
    ) -> str | None:
        try:
            from openai import AsyncOpenAI

            client = AsyncOpenAI(
                api_key=self.settings.openai_api_key,
                timeout=self.settings.external_request_timeout_seconds,
                max_retries=self.settings.openai_max_retries,
            )
            completion = await client.chat.completions.create(
                model=self.settings.openai_model,
                messages=[
                    {
                        "role": "system",
                        "content": SYSTEM_PROMPT.format(
                            denomination=get_denomination_context(denomination),
                            retrieved_verses=format_retrieved_verses(retrieved_verses),
                            memory_context=format_memory(memory_context),
                        ),
                    },
                    {"role": "user", "content": message},
                ],
                temperature=0.2,
            )
            return completion.choices[0].message.content or None
        except Exception:
            logger.exception("OpenAI chat completion failed; using local fallback")
            return None

    async def stream_response(
        self,
        message: str,
        denomination: str,
        retrieved_verses: list[VerseChunk],
        memory_context: list[dict],
    ):
        deterministic_response = deterministic_response_for_lens(
            message, denomination, retrieved_verses
        )
        if deterministic_response:
            for chunk in chunk_text(deterministic_response):
                yield chunk
            return
        if not self.settings.openai_api_key:
            local_response = self._generate_local_response(message, denomination, retrieved_verses)
            for chunk in chunk_text(local_response):
                yield chunk
            return

        try:
            from openai import AsyncOpenAI

            client = AsyncOpenAI(
                api_key=self.settings.openai_api_key,
                timeout=self.settings.external_request_timeout_seconds,
                max_retries=self.settings.openai_max_retries,
            )
            stream = await client.chat.completions.create(
                model=self.settings.openai_model,
                messages=[
                    {
                        "role": "system",
                        "content": SYSTEM_PROMPT.format(
                            denomination=get_denomination_context(denomination),
                            retrieved_verses=format_retrieved_verses(retrieved_verses),
                            memory_context=format_memory(memory_context),
                        ),
                    },
                    {"role": "user", "content": message},
                ],
                temperature=0.2,
                stream=True,
                stream_options={"include_usage": False},
            )
            async for event in stream:
                if not event.choices:
                    continue
                delta = event.choices[0].delta.content
                if delta:
                    yield delta
        except Exception:
            logger.exception("OpenAI chat stream failed; using local fallback")
            local_response = self._generate_local_response(message, denomination, retrieved_verses)
            for chunk in chunk_text(local_response):
                yield chunk

    def _generate_local_response(
        self, message: str, denomination: str, retrieved_verses: list[VerseChunk]
    ) -> str:
        lowered = message.lower()
        canon_note = canon_difference_note(message, denomination)

        if "god helps those who help themselves" in lowered:
            verses = format_inline_citations(retrieved_verses)
            return (
                "That phrase is not a Bible verse; it is commonly associated with Benjamin "
                f"Franklin. A more biblical way to speak about God's help is: {verses}"
            )
        if "cleanliness is next to godliness" in lowered:
            verses = format_inline_citations(retrieved_verses)
            return (
                "That phrase is not a Bible verse. It is a common proverb, not a verified "
                f"biblical quotation. Related passages about cleansing and wisdom include: {verses}"
            )

        if not retrieved_verses:
            note = (
                f"\n\n{canon_note}"
                if canon_note
                else "\n\nI do not have a relevant verified verse in the retrieved context."
            )
            return (
                "I cannot cite a verse for this from memory. I only cite Scripture that was "
                f"retrieved from the local KJV corpus.{note}"
            )

        verses = format_inline_citations(retrieved_verses)
        denom = denomination_label(denomination)
        prefix = f"{canon_note}\n\n" if canon_note else ""
        afterlife_response = local_afterlife_response(lowered, denomination, verses)
        if afterlife_response:
            return f"{prefix}{afterlife_response}"
        if any(term in lowered for term in ["mean", "meaning", "explain"]):
            return (
                f"{prefix}From a {denom} perspective, this passage should be read from the verified "
                f"scripture context first: {verses}\n\n"
                "In plain terms, the passage points to God's initiative, the call to trust him, "
                "and the need to respond with humility rather than using the verse as a slogan."
            )
        return (
            f"{prefix}Here are verified KJV passages from the local corpus: {verses}\n\n"
            f"From a {denom} perspective, these verses should be applied with humility and care."
        )


def format_retrieved_verses(verses: list[VerseChunk]) -> str:
    if not verses:
        return "No verified scripture context retrieved."
    return "\n".join(f"[{verse.reference}] \"{verse.text}\"" for verse in verses)


def format_memory(turns: list[dict]) -> str:
    if not turns:
        return "No prior conversation."
    return "\n".join(f"{turn['role']}: {turn['content']}" for turn in turns[-10:])


def format_inline_citations(verses: list[VerseChunk]) -> str:
    return " ".join(f'[{verse.reference}] "{verse.text}"' for verse in verses)


def chunk_text(text: str, size: int = 16):
    for index in range(0, len(text), size):
        yield text[index : index + size]


def local_afterlife_response(lowered: str, denomination: str, verses: str) -> str | None:
    if not any(term in lowered for term in ["after death", "afterlife", "heaven", "believers die"]):
        return None
    if denomination == "evangelical":
        return (
            "From an Evangelical perspective, assurance after death is anchored in personal "
            "saving faith and the born-again response to Jesus. Romans 10:9 is especially "
            f"relevant where available, and the verified scripture context here is: {verses}"
        )
    if denomination == "non_denominational":
        return non_denominational_afterlife_response(verses)
    if denomination == "catholic":
        return (
            "From a Catholic perspective, believers who die in God's grace are destined for "
            "communion with God, while purification after death is understood through the "
            f"Catechism's framing of purgatory. Verified scripture context: {verses}"
        )
    if denomination == "orthodox":
        return (
            "From an Eastern Orthodox perspective, the hope after death is described less as a "
            "legal status and more as growing communion with God, theosis, and participation "
            f"in divine life. Verified scripture context: {verses}"
        )
    return (
        "From a Protestant perspective, Scripture is the final authority, and the believer's "
        f"hope after death rests on faith alone in Christ. Verified scripture context: {verses}"
    )


def deterministic_response_for_lens(
    message: str, denomination: str, retrieved_verses: list[VerseChunk]
) -> str | None:
    lowered = message.lower()
    if denomination != "non_denominational":
        return None
    if not is_afterlife_question(lowered) or len(retrieved_verses) < 2:
        return None
    return non_denominational_afterlife_response(format_inline_citations(retrieved_verses[:3]))


def is_afterlife_question(lowered: str) -> bool:
    return any(term in lowered for term in ["after death", "afterlife", "heaven", "believers die"])


def non_denominational_afterlife_response(verses: str) -> str:
    return (
        "The Bible speaks about what happens to believers after death in these passages.\n\n"
        f"{verses}\n\n"
        "To depart and be with Christ is far better."
    )
