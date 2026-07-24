from __future__ import annotations

from pathlib import Path

from app.utils.paths import ensure_output_dir, safe_stem, unique_output_base


def test_safe_stem_preserves_accents_and_removes_unsafe() -> None:
    assert safe_stem(Path("reunião: equipe?.mp3")) == "reunião_ equipe_"


def test_safe_stem_fallback() -> None:
    assert safe_stem(Path("...wav")) == "transcricao"


def test_output_directory_and_unique_names(tmp_path: Path) -> None:
    output = ensure_output_dir(tmp_path / "pasta com espaço")
    assert output.is_dir()
    (output / "áudio.txt").write_text("existente", encoding="utf-8")
    assert unique_output_base(output, "áudio").name == "áudio-2"
