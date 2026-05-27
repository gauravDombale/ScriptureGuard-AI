import json
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
BIBLE_PATH = DATA_DIR / "bible_kjv.json"
METADATA_PATH = DATA_DIR / "bible_metadata.json"


@dataclass(frozen=True)
class Verse:
    book: str
    chapter: int
    verse: int
    text: str
    testament: str
    genre: str

    @property
    def reference(self) -> str:
        return f"{self.book} {self.chapter}:{self.verse}"


@lru_cache
def load_bible() -> list[Verse]:
    with BIBLE_PATH.open() as file:
        rows = json.load(file)
    return [Verse(**row) for row in rows]


@lru_cache
def load_metadata() -> dict:
    with METADATA_PATH.open() as file:
        return json.load(file)


@lru_cache
def verse_lookup() -> dict[str, Verse]:
    return {verse.reference.lower(): verse for verse in load_bible()}


@lru_cache
def book_names() -> list[str]:
    return [book["name"] for book in load_metadata()["books"]]


def normalize_reference(reference: str) -> str:
    reference = re.sub(r"\s+", " ", reference.strip())
    reference = reference.replace("Psalm ", "Psalms ")
    for book in book_names():
        pattern = re.compile(rf"^{re.escape(book)}\b", re.IGNORECASE)
        if pattern.search(reference):
            return pattern.sub(book, reference, count=1)
    return reference


def get_verse(reference: str) -> Verse | None:
    return verse_lookup().get(normalize_reference(reference).lower())
