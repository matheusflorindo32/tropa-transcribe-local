from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.config import AppConfig, load_config, save_config


def test_default_config_when_missing(tmp_path: Path) -> None:
    assert load_config(tmp_path / "missing.json") == AppConfig()


def test_config_round_trip_utf8(tmp_path: Path) -> None:
    path = tmp_path / "configuração.json"
    expected = AppConfig(model="small", output_dir="C:/Transcrições")
    assert save_config(expected, path) == path
    assert load_config(path) == expected


def test_invalid_json_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "config.json"
    path.write_text("{", encoding="utf-8")
    with pytest.raises(ValueError, match="Configuração inválida"):
        load_config(path)


def test_invalid_values_are_rejected(tmp_path: Path) -> None:
    path = tmp_path / "config.json"
    path.write_text(json.dumps({"model": "gigante"}), encoding="utf-8")
    with pytest.raises(ValueError):
        load_config(path)
