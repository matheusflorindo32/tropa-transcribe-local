"""Orquestração FFmpeg → whisper.cpp."""

from __future__ import annotations

import logging
import threading
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from app.config import default_data_dir
from app.services.ffmpeg import convert_to_wav, resolve_ffmpeg
from app.services.files import TemporaryWorkspace
from app.services.models import resolve_model
from app.transcription.formats import validate_output_formats
from app.transcription.progress import ProgressEvent, Stage
from app.transcription.validators import validate_input_file, validate_model_name
from app.transcription.whisper_cpp import (
    build_whisper_command,
    resolve_whisper_cli,
    run_whisper,
)
from app.utils.paths import ensure_output_dir, safe_stem, unique_output_base

ProgressCallback = Callable[[ProgressEvent], None]


@dataclass(frozen=True, slots=True)
class TranscriptionRequest:
    input_file: Path
    output_dir: Path
    model: str = "base"
    language: str = "pt"
    formats: tuple[str, ...] = ("txt", "srt", "vtt")
    model_path: Path | None = None
    keep_temp: bool = False
    quiet: bool = False
    max_file_size_mb: int = 20_480


class TranscriptionEngine:
    def __init__(
        self,
        ffmpeg: str | Path = "ffmpeg",
        whisper_cli: str | Path = "whisper-cli",
        logger: logging.Logger | None = None,
    ) -> None:
        self.ffmpeg_candidate = ffmpeg
        self.whisper_candidate = whisper_cli
        self.logger = logger or logging.getLogger("tropa_transcribe")

    def transcribe(
        self,
        request: TranscriptionRequest,
        progress: ProgressCallback | None = None,
        cancel_event: threading.Event | None = None,
    ) -> list[Path]:
        notify = progress or (lambda event: None)
        notify(ProgressEvent(Stage.VALIDATING, 5, "Validando arquivo e componentes..."))
        source = validate_input_file(request.input_file, request.max_file_size_mb)
        model_name = validate_model_name(request.model)
        formats = validate_output_formats(request.formats)
        destination = ensure_output_dir(request.output_dir)
        ffmpeg = resolve_ffmpeg(self.ffmpeg_candidate)
        whisper = resolve_whisper_cli(self.whisper_candidate)
        model = resolve_model(model_name, request.model_path)
        output_base = unique_output_base(destination, safe_stem(source))

        temp_root = default_data_dir() / "temp"
        with TemporaryWorkspace(temp_root, request.keep_temp) as workspace:
            wav_file = workspace.path / "entrada.wav"
            notify(ProgressEvent(Stage.CONVERTING, 15, "Convertendo mídia para WAV compatível..."))
            self.logger.info("Conversão iniciada para arquivo '%s'.", source.name)
            convert_to_wav(ffmpeg, source, wav_file, cancel_event)
            notify(ProgressEvent(Stage.TRANSCRIBING, 35, "Transcrevendo localmente..."))
            command = build_whisper_command(
                whisper,
                model,
                wav_file,
                output_base,
                request.language,
                formats,
                request.quiet,
            )
            run_whisper(command, cancel_event)
            notify(ProgressEvent(Stage.FINALIZING, 95, "Verificando arquivos gerados..."))

        generated = [output_base.with_suffix(f".{item}") for item in formats]
        missing = [path.suffix for path in generated if not path.is_file()]
        if missing:
            raise RuntimeError(f"Saída(s) esperada(s) não gerada(s): {', '.join(missing)}")
        notify(ProgressEvent(Stage.COMPLETED, 100, "Transcrição concluída."))
        self.logger.info("Transcrição concluída; %d arquivo(s) gerado(s).", len(generated))
        return generated
