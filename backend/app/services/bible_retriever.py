import math
import re
from dataclasses import dataclass
from functools import lru_cache

from app.config import get_settings
from app.services.bible_corpus import Verse, get_verse, load_bible


@dataclass
class VerseChunk:
    reference: str
    text: str
    book: str
    chapter: int
    verse: int
    testament: str
    genre: str
    score: float

    @classmethod
    def from_verse(cls, verse: Verse, score: float) -> "VerseChunk":
        return cls(
            reference=verse.reference,
            text=verse.text,
            book=verse.book,
            chapter=verse.chapter,
            verse=verse.verse,
            testament=verse.testament,
            genre=verse.genre,
            score=score,
        )


REFERENCE_HINTS = {
    "john 3:16": ["John 3:16"],
    "love your enemies": ["Matthew 5:44", "Luke 6:27"],
    "grief": ["Psalms 34:18", "John 11:25", "2 Corinthians 1:3", "2 Corinthians 1:4"],
    "comfort": ["Psalms 34:18", "2 Corinthians 1:3", "2 Corinthians 1:4"],
    "anxiety": ["Philippians 4:6", "Philippians 4:7", "1 Peter 5:7"],
    "forgiveness": ["Ephesians 4:32", "Matthew 6:14", "1 John 1:9"],
    "faith": ["Hebrews 11:1", "Romans 10:17", "Ephesians 2:8"],
    "god helps those who help themselves": ["Psalms 46:1", "Isaiah 41:10"],
    "cleanliness is next to godliness": ["Psalms 51:10", "James 4:8"],
    "god is refuge": ["Psalms 46:1"],
    "genesis": ["Genesis 1:1", "Genesis 1:27"],
    "creation": ["Genesis 1:1", "John 1:3"],
    "romans": ["Romans 3:24", "Romans 5:1"],
    "grace": ["Ephesians 2:8", "Romans 3:24"],
    "james": ["James 1:5"],
    "wisdom": ["James 1:5", "Proverbs 9:10"],
}


class BibleRetriever:
    def __init__(self) -> None:
        self.settings = get_settings()

    async def retrieve_verses(
        self, query: str, denomination: str, top_k: int = 5
    ) -> list[VerseChunk]:
        if self.settings.openai_api_key and self.settings.pinecone_api_key:
            pinecone_results = await self._retrieve_from_pinecone(query, denomination, top_k)
            if pinecone_results:
                return pinecone_results
        return self._retrieve_locally(query, top_k)

    async def _retrieve_from_pinecone(
        self, query: str, denomination: str, top_k: int
    ) -> list[VerseChunk]:
        try:
            from openai import AsyncOpenAI
            from pinecone import Pinecone

            openai_client = AsyncOpenAI(api_key=self.settings.openai_api_key)
            embedding = await openai_client.embeddings.create(
                model=self.settings.openai_embedding_model, input=query
            )
            pc = Pinecone(api_key=self.settings.pinecone_api_key)
            index = pc.Index(self.settings.pinecone_index_name)
            response = index.query(
                vector=embedding.data[0].embedding,
                top_k=top_k,
                include_metadata=True,
                filter=self._denomination_filter(denomination),
            )
        except Exception:
            return []

        chunks: list[VerseChunk] = []
        for match in response.matches:
            if match.score < 0.75:
                continue
            metadata = match.metadata
            chunks.append(
                VerseChunk(
                    reference=f"{metadata['book']} {metadata['chapter']}:{metadata['verse']}",
                    text=metadata["text"],
                    book=metadata["book"],
                    chapter=int(metadata["chapter"]),
                    verse=int(metadata["verse"]),
                    testament=metadata["testament"],
                    genre=metadata["genre"],
                    score=float(match.score),
                )
            )
        return chunks

    def _retrieve_locally(self, query: str, top_k: int) -> list[VerseChunk]:
        lowered = query.lower()
        hinted: list[VerseChunk] = []
        for phrase, references in REFERENCE_HINTS.items():
            if phrase in lowered:
                for reference in references:
                    verse = get_verse(reference)
                    if verse:
                        hinted.append(VerseChunk.from_verse(verse, 0.95))
        if hinted:
            return hinted[:top_k]

        query_tokens = tokenize(query)
        scored: list[VerseChunk] = []
        for verse in load_bible():
            score = bm25_like_score(query_tokens, tokenize(verse.text), verse.reference.lower(), lowered)
            if score >= 0.18:
                scored.append(VerseChunk.from_verse(verse, min(0.99, score)))
        scored.sort(key=lambda chunk: chunk.score, reverse=True)
        return scored[:top_k]

    @staticmethod
    def _denomination_filter(denomination: str) -> dict | None:
        # Current corpus is KJV 66-book canon. Deuterocanonical handling is documented in
        # denomination_service and can be extended with a second corpus.
        return None


@lru_cache(maxsize=50_000)
def tokenize(text: str) -> tuple[str, ...]:
    stop_words = {
        "the",
        "and",
        "a",
        "an",
        "of",
        "to",
        "in",
        "for",
        "with",
        "what",
        "does",
        "bible",
        "scripture",
        "offer",
        "during",
    }
    return tuple(
        token
        for token in re.findall(r"[a-z0-9]+", text.lower())
        if token not in stop_words and len(token) > 2
    )


def bm25_like_score(
    query_tokens: tuple[str, ...], verse_tokens: tuple[str, ...], reference: str, lowered_query: str
) -> float:
    if not query_tokens:
        return 0.0
    verse_set = set(verse_tokens)
    overlap = sum(1 for token in query_tokens if token in verse_set)
    if overlap == 0:
        return 0.0
    density = overlap / math.sqrt(max(len(verse_tokens), 1))
    reference_bonus = 0.25 if any(token in reference for token in query_tokens) else 0.0
    phrase_bonus = 0.2 if " ".join(query_tokens[:2]) in " ".join(verse_tokens) else 0.0
    return density + reference_bonus + phrase_bonus
