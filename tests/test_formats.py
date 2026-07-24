from __future__ import annotations

import pytest

from app.transcription.formats import output_flags, validate_output_formats


def test_formats_are_normalized_and_deduplicated() -> None:
    assert validate_output_formats(["TXT", "srt", "txt"]) == ("txt", "srt")


def test_all_output_flags() -> None:
    assert output_flags(["txt", "srt", "vtt", "json"]) == [
        "--output-txt",
        "--output-srt",
        "--output-vtt",
        "--output-json",
    ]


@pytest.mark.parametrize("formats", [[], ["pdf"], ["txt", "docx"]])
def test_invalid_formats_raise(formats: list[str]) -> None:
    with pytest.raises(ValueError):
        validate_output_formats(formats)
