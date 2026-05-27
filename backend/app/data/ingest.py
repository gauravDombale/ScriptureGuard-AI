"""Normalize KJV JSON and optionally upsert one-vector-per-verse to Pinecone."""

from __future__ import annotations

import argparse
import json
import re
import urllib.request
from collections import OrderedDict, defaultdict
from pathlib import Path

SOURCE_URL = "https://raw.githubusercontent.com/farskipper/kjv/master/json/verses-1769.json"
DATA_DIR = Path(__file__).resolve().parent
SOURCE_PATH = DATA_DIR / "bible_kjv_source.json"
BIBLE_PATH = DATA_DIR / "bible_kjv.json"
METADATA_PATH = DATA_DIR / "bible_metadata.json"

OLD_TESTAMENT = {
    "Genesis",
    "Exodus",
    "Leviticus",
    "Numbers",
    "Deuteronomy",
    "Joshua",
    "Judges",
    "Ruth",
    "1 Samuel",
    "2 Samuel",
    "1 Kings",
    "2 Kings",
    "1 Chronicles",
    "2 Chronicles",
    "Ezra",
    "Nehemiah",
    "Esther",
    "Job",
    "Psalms",
    "Proverbs",
    "Ecclesiastes",
    "Song of Solomon",
    "Isaiah",
    "Jeremiah",
    "Lamentations",
    "Ezekiel",
    "Daniel",
    "Hosea",
    "Joel",
    "Amos",
    "Obadiah",
    "Jonah",
    "Micah",
    "Nahum",
    "Habakkuk",
    "Zephaniah",
    "Haggai",
    "Zechariah",
    "Malachi",
}

GENRES = {
    "Psalms": "poetry",
    "Proverbs": "wisdom",
    "Ecclesiastes": "wisdom",
    "Song of Solomon": "wisdom",
    "Matthew": "gospel",
    "Mark": "gospel",
    "Luke": "gospel",
    "John": "gospel",
    "Romans": "epistle",
    "1 Corinthians": "epistle",
    "2 Corinthians": "epistle",
    "Galatians": "epistle",
    "Ephesians": "epistle",
    "Philippians": "epistle",
    "Colossians": "epistle",
    "1 Thessalonians": "epistle",
    "2 Thessalonians": "epistle",
    "1 Timothy": "epistle",
    "2 Timothy": "epistle",
    "Titus": "epistle",
    "Philemon": "epistle",
    "Hebrews": "epistle",
    "James": "epistle",
    "1 Peter": "epistle",
    "2 Peter": "epistle",
    "1 John": "epistle",
    "2 John": "epistle",
    "3 John": "epistle",
    "Jude": "epistle",
    "Revelation": "apocalyptic",
}


def download_source() -> None:
    if SOURCE_PATH.exists():
        return
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(SOURCE_URL, SOURCE_PATH)


def normalize_source() -> tuple[list[dict], dict]:
    with SOURCE_PATH.open() as file:
        source = json.load(file)

    pattern = re.compile(r"^(.+) (\d+):(\d+)$")
    verses: list[dict] = []
    metadata: OrderedDict[str, dict] = OrderedDict()

    for reference, text in source.items():
        match = pattern.match(reference)
        if not match:
            raise ValueError(f"Unexpected reference format: {reference}")
        book, chapter, verse_num = match.group(1), int(match.group(2)), int(match.group(3))
        testament = "OT" if book in OLD_TESTAMENT else "NT"
        genre = GENRES.get(
            book,
            "law"
            if book in {"Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy"}
            else "history"
            if testament == "OT"
            else "narrative",
        )
        clean_text = text.replace("# ", "").replace("#", "").strip()
        verses.append(
            {
                "book": book,
                "chapter": chapter,
                "verse": verse_num,
                "text": clean_text,
                "testament": testament,
                "genre": genre,
            }
        )
        metadata.setdefault(
            book, {"chapters": defaultdict(int), "testament": testament, "genre": genre}
        )
        metadata[book]["chapters"][str(chapter)] = max(
            metadata[book]["chapters"][str(chapter)], verse_num
        )

    bible_metadata = {
        "total_verses": len(verses),
        "books": [
            {
                "name": book,
                "testament": value["testament"],
                "genre": value["genre"],
                "chapter_count": len(value["chapters"]),
                "chapters": dict(value["chapters"]),
            }
            for book, value in metadata.items()
        ],
    }
    return verses, bible_metadata


def write_normalized_files() -> None:
    verses, metadata = normalize_source()
    BIBLE_PATH.write_text(json.dumps(verses, indent=2))
    METADATA_PATH.write_text(json.dumps(metadata, indent=2))
    if len(verses) != 31_102:
        raise RuntimeError(f"Expected 31,102 KJV verses, got {len(verses)}")


async def upsert_to_pinecone() -> None:
    from app.config import get_settings

    settings = get_settings()
    if not settings.openai_api_key or not settings.pinecone_api_key:
        print("Skipping Pinecone upsert: OPENAI_API_KEY and PINECONE_API_KEY are required.")
        return

    from openai import AsyncOpenAI
    from pinecone import Pinecone

    verses, _ = normalize_source()
    openai_client = AsyncOpenAI(api_key=settings.openai_api_key)
    pc = Pinecone(api_key=settings.pinecone_api_key)
    index = pc.Index(settings.pinecone_index_name)

    batch_size = 100
    for offset in range(0, len(verses), batch_size):
        batch = verses[offset : offset + batch_size]
        inputs = [
            f"{row['book']} {row['chapter']}:{row['verse']} - {row['text']}" for row in batch
        ]
        embeddings = await openai_client.embeddings.create(
            model=settings.openai_embedding_model, input=inputs
        )
        vectors = []
        for row, embedding in zip(batch, embeddings.data, strict=True):
            vector_id = f"{row['book']}-{row['chapter']}-{row['verse']}".replace(" ", "-")
            vectors.append(
                {
                    "id": vector_id,
                    "values": embedding.embedding,
                    "metadata": {
                        "book": row["book"],
                        "chapter": row["chapter"],
                        "verse": row["verse"],
                        "testament": row["testament"],
                        "genre": row["genre"],
                        "text": row["text"],
                    },
                }
            )
        index.upsert(vectors=vectors)
        print(f"Upserted {min(offset + batch_size, len(verses))}/{len(verses)} verses")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--download", action="store_true")
    parser.add_argument("--upsert", action="store_true")
    args = parser.parse_args()

    if args.download:
        download_source()
    write_normalized_files()
    print("Wrote bible_kjv.json and bible_metadata.json with 31,102 verses.")

    if args.upsert:
        import asyncio

        asyncio.run(upsert_to_pinecone())


if __name__ == "__main__":
    main()
