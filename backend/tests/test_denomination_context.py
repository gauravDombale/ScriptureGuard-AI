from app.services.bible_retriever import VerseChunk
from app.services.bible_corpus import get_verse
from app.services.denomination_service import (
    denomination_note,
    get_denomination_context,
)
from app.services.llm_service import LLMService, SYSTEM_PROMPT


DENOMINATIONS = ["protestant", "catholic", "orthodox", "evangelical", "non_denominational"]
LEAK_MARKERS = ["canon=", "notes=", "distinctives="]


def test_denomination_contexts_are_plain_language() -> None:
    contexts = [get_denomination_context(denomination) for denomination in DENOMINATIONS]

    assert len(set(contexts)) == len(DENOMINATIONS)
    for context in contexts:
        assert context.startswith("You are responding from")
        assert "Do not expose internal metadata." in context
        assert_no_metadata_leak(context)


def test_public_denomination_notes_do_not_expose_metadata() -> None:
    for denomination in DENOMINATIONS:
        assert_no_metadata_leak(denomination_note(denomination))
    non_denom_note = denomination_note("non_denominational").lower()
    for term in ["doctrine", "theology", "tradition", "salvation", "creed"]:
        assert term not in non_denom_note


def test_system_prompt_contains_differentiation_rules() -> None:
    assert "DENOMINATION DIFFERENTIATION RULES" in SYSTEM_PROMPT
    assert "born-again experience" in SYSTEM_PROMPT
    assert "purgatory" in SYSTEM_PROMPT
    assert "theosis" in SYSTEM_PROMPT


def test_local_afterlife_responses_are_distinct_by_lens() -> None:
    service = LLMService()
    verses = [
        VerseChunk.from_verse(get_verse("John 11:25"), 0.95),
        VerseChunk.from_verse(get_verse("2 Corinthians 5:8"), 0.95),
        VerseChunk.from_verse(get_verse("Philippians 1:23"), 0.95),
    ]

    responses = {
        denomination: service._generate_local_response(
            "What happens to believers after death?", denomination, verses
        )
        for denomination in DENOMINATIONS
    }

    assert len(set(responses.values())) == len(DENOMINATIONS)
    assert "born-again" in responses["evangelical"]
    assert "purgatory" in responses["catholic"]
    assert "theosis" in responses["orthodox"]
    assert "faith alone" in responses["protestant"]
    assert_non_denominational_afterlife_shape(responses["non_denominational"])
    for response in responses.values():
        assert_no_metadata_leak(response)


def assert_non_denominational_afterlife_shape(response: str) -> None:
    lowered = response.lower()
    banned_terms = ["doctrine", "theology", "tradition", "salvation", "creed", "denomination"]
    for term in banned_terms:
        assert term not in lowered
    assert response.count("[") >= 2
    assert response.rstrip().endswith("To depart and be with Christ is far better.")


def assert_no_metadata_leak(text: str) -> None:
    for marker in LEAK_MARKERS:
        assert marker not in text
