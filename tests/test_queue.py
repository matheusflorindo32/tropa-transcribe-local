from __future__ import annotations

from pathlib import Path

from app.services.queue import QueueStatus, TranscriptionQueue


def test_queue_accepts_unicode_spaces_and_rejects_duplicates(tmp_path: Path) -> None:
    media = tmp_path / "áudio autorizado com espaço.ogg"
    media.write_bytes(b"audio")
    queue = TranscriptionQueue()

    added, rejected = queue.add([media, media])

    assert added == 1
    assert len(rejected) == 1
    assert queue.items[0].path == media.resolve()


def test_queue_rejects_missing_and_unsupported_files(tmp_path: Path) -> None:
    unsupported = tmp_path / "documento.txt"
    unsupported.write_text("x", encoding="utf-8")
    queue = TranscriptionQueue()

    added, rejected = queue.add([tmp_path / "ausente.ogg", unsupported])

    assert added == 0
    assert len(rejected) == 2


def test_queue_remove_clear_and_progress(tmp_path: Path) -> None:
    first = tmp_path / "a.wav"
    second = tmp_path / "b.mp3"
    first.write_bytes(b"a")
    second.write_bytes(b"b")
    queue = TranscriptionQueue()
    queue.add([first, second])

    queue.update(0, status=QueueStatus.RUNNING, progress=120, detail="teste")
    assert queue.items[0].progress == 100
    queue.remove([0])
    assert queue.items[0].path == second.resolve()
    queue.clear()
    assert not queue.items
