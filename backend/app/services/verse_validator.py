import re
from dataclasses import dataclass, field
from difflib import SequenceMatcher

from app.models.schemas import VerseCitation
from app.services.bible_corpus import Verse, book_names, get_verse, load_metadata, normalize_reference


@dataclass
class ValidationResult:
    valid_citations: list[VerseCitation] = field(default_factory=list)
    hallucinated_citations: list[str] = field(default_factory=list)
    cleaned_response: str = ""


class VerseValidator:
    def __init__(self) -> None:
        escaped_books = sorted((re.escape(book) for book in book_names()), key=len, reverse=True)
        self.reference_pattern = re.compile(
            rf"\b({'|'.join(escaped_books)})\s+(\d+):(\d+)(?:-(\d+))?\b",
            re.IGNORECASE,
        )
        self.metadata = load_metadata()
        self.chapter_map = {
            book["name"].lower(): {int(ch): count for ch, count in book["chapters"].items()}
            for book in self.metadata["books"]
        }

    def validate_citations(self, response_text: str) -> ValidationResult:
        result = ValidationResult(cleaned_response=response_text)
        seen_valid: set[str] = set()

        for match in self.reference_pattern.finditer(response_text):
            raw_reference = match.group(0)
            book = normalize_reference(match.group(1))
            chapter = int(match.group(2))
            start_verse = int(match.group(3))
            end_verse = int(match.group(4) or start_verse)

            verses = self._resolve_range(book, chapter, start_verse, end_verse)
            if not verses:
                result.hallucinated_citations.append(raw_reference)
                result.cleaned_response = result.cleaned_response.replace(raw_reference, "").strip()
                continue

            for verse in verses:
                if not self._quoted_text_matches(response_text, verse):
                    result.hallucinated_citations.append(verse.reference)
                    continue
                if verse.reference not in seen_valid:
                    result.valid_citations.append(
                        VerseCitation(reference=verse.reference, text=verse.text, verified=True)
                    )
                    seen_valid.add(verse.reference)

        if result.hallucinated_citations:
            result.cleaned_response = (
                result.cleaned_response.rstrip()
                + "\n\nNote: I could not verify one or more references, so I removed or flagged them. "
                "Please consult your Bible directly."
            )
        return result

    def citation_from_reference(self, reference: str) -> VerseCitation | None:
        verse = get_verse(reference)
        if not verse:
            return None
        return VerseCitation(reference=verse.reference, text=verse.text, verified=True)

    def explain_missing_reference(self, reference: str) -> str | None:
        match = self.reference_pattern.search(reference)
        if not match:
            book_match = re.search(r"\b([1-3]?\s?[A-Za-z][A-Za-z ]+?)\s+\d+:\d+\b", reference.strip())
            if book_match:
                candidate = normalize_reference(book_match.group(1))
                if candidate.lower() not in self.chapter_map:
                    return f"I cannot find the book '{candidate}' in the KJV Bible corpus."
            return None

        book = normalize_reference(match.group(1))
        chapter = int(match.group(2))
        verse_num = int(match.group(3))
        chapters = self.chapter_map.get(book.lower())
        if not chapters:
            return f"I cannot find the book '{book}' in the KJV Bible corpus."
        if chapter not in chapters:
            max_chapter = max(chapters)
            return f"{book} only has {max_chapter} chapters. I cannot find {book} {chapter}:{verse_num}."
        max_verse = chapters[chapter]
        if verse_num > max_verse:
            return (
                f"{book} {chapter} only has {max_verse} verses. "
                f"I cannot find {book} {chapter}:{verse_num}."
            )
        return None

    def _resolve_range(
        self, book: str, chapter: int, start_verse: int, end_verse: int
    ) -> list[Verse]:
        if end_verse < start_verse:
            return []
        verses: list[Verse] = []
        for verse_num in range(start_verse, end_verse + 1):
            verse = get_verse(f"{book} {chapter}:{verse_num}")
            if not verse:
                return []
            verses.append(verse)
        return verses

    def _quoted_text_matches(self, response_text: str, verse: Verse) -> bool:
        quoted_segments = re.findall(r'"([^"]+)"', response_text)
        if not quoted_segments:
            return True
        reference_index = response_text.lower().find(verse.reference.lower())
        if reference_index == -1:
            return True
        nearby = response_text[max(0, reference_index - 300) : reference_index + 500]
        nearby_quotes = re.findall(r'"([^"]+)"', nearby)
        if not nearby_quotes:
            return True
        return any(self._similarity(segment, verse.text) >= 0.85 for segment in nearby_quotes)

    @staticmethod
    def _similarity(left: str, right: str) -> float:
        clean = lambda value: re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()
        return SequenceMatcher(None, clean(left), clean(right)).ratio()
