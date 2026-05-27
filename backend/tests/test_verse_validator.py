from app.services.verse_validator import VerseValidator


def test_validates_real_verse() -> None:
    validator = VerseValidator()
    result = validator.validate_citations(
        '[John 3:16] "For God so loved the world, that he gave his only begotten Son, '
        'that whosoever believeth in him should not perish, but have everlasting life."'
    )
    assert result.valid_citations[0].reference == "John 3:16"
    assert result.valid_citations[0].verified is True


def test_explains_missing_verse() -> None:
    validator = VerseValidator()
    assert "only has" in validator.explain_missing_reference("Quote Ezekiel 48:99")


def test_rejects_fake_book() -> None:
    validator = VerseValidator()
    assert "cannot find the book" in validator.explain_missing_reference("2 Hesitations 3:12")
