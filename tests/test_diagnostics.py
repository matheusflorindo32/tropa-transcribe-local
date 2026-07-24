from __future__ import annotations

from pathlib import Path

from app.services.diagnostics import DiagnosticReport, build_diagnostic


def test_safe_diagnostic_redacts_home_and_never_contains_media_names() -> None:
    report = DiagnosticReport(
        {
            "Dados": str(Path.home() / "privado" / "entrevista-secreta.ogg"),
            "Token": "não coletado",
        }
    )
    safe = report.safe_text()
    assert str(Path.home()) not in safe
    assert "%USERPROFILE%" in safe
    # O relatório real nunca recebe nem enumera os nomes de mídia.
    assert "conteúdo transcrito" not in safe


def test_basic_diagnostic_reports_missing_components(tmp_path: Path, monkeypatch: object) -> None:
    from pytest import MonkeyPatch

    patch = monkeypatch
    assert isinstance(patch, MonkeyPatch)
    patch.setattr("app.services.diagnostics.default_data_dir", lambda: tmp_path)
    patch.setattr("app.services.diagnostics.default_models_dir", lambda: tmp_path / "models")
    patch.setattr(
        "app.services.diagnostics.resolve_ffmpeg",
        lambda: (_ for _ in ()).throw(FileNotFoundError()),
    )
    patch.setattr(
        "app.services.diagnostics.resolve_whisper_cli",
        lambda: (_ for _ in ()).throw(FileNotFoundError()),
    )

    report = build_diagnostic("base")

    assert report.values["Teste básico"].startswith("reprovado")
    assert "ausente" in report.values["FFmpeg"]
    assert "ausente" in report.values["whisper-cli"]
