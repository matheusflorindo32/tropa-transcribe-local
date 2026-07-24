"""Interface de linha de comando em português brasileiro."""

from __future__ import annotations

import argparse
import os
import sys
from collections.abc import Callable
from pathlib import Path

from app import __version__
from app.config import AppConfig, load_config, save_config
from app.transcription.engine import TranscriptionEngine, TranscriptionRequest
from app.transcription.progress import ProgressEvent
from app.transcription.validators import collect_batch_files
from app.utils.logging import configure_logging

EXIT_OK = 0
EXIT_ARGUMENT = 2
EXIT_DEPENDENCY = 3
EXIT_PROCESSING = 4
EXIT_INTERRUPTED = 130

ACCURACY_NOTICE = (
    "A transcrição é gerada automaticamente e pode conter erros. Revise nomes, números, "
    "termos técnicos e informações críticas antes de utilizar ou publicar o conteúdo."
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tropa-transcribe",
        description="Transcrição local e privada com FFmpeg e whisper.cpp.",
        epilog=ACCURACY_NOTICE,
    )
    parser.add_argument("entrada", type=Path, help="Arquivo ou pasta (com --batch).")
    parser.add_argument("--batch", action="store_true", help="Processa arquivos de uma pasta.")
    parser.add_argument("--model", help="Modelo ggml (padrão salvo: base).")
    parser.add_argument("--model-path", type=Path, help="Caminho explícito para o modelo.")
    parser.add_argument("--language", help="Idioma, por exemplo pt, en ou auto.")
    parser.add_argument(
        "--output",
        nargs="+",
        choices=("txt", "srt", "vtt", "json"),
        help="Formatos de saída.",
    )
    parser.add_argument("--output-dir", type=Path, help="Pasta das transcrições.")
    parser.add_argument("--ffmpeg", default=os.environ.get("TROPA_FFMPEG", "ffmpeg"))
    parser.add_argument("--whisper-cli", default=os.environ.get("TROPA_WHISPER_CLI", "whisper-cli"))
    parser.add_argument("--keep-temp", action="store_true", help="Preserva WAV temporário.")
    parser.add_argument("--quiet", action="store_true", help="Modo silencioso para automações.")
    parser.add_argument("--verbose", action="store_true", help="Exibe logs operacionais.")
    parser.add_argument(
        "--save-defaults", action="store_true", help="Salva preferências não sensíveis."
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def _progress(quiet: bool) -> Callable[[ProgressEvent], None]:
    def callback(event: ProgressEvent) -> None:
        if not quiet:
            print(f"[{event.percent:3d}%] {event.message}", file=sys.stderr)

    return callback


def run(arguments: list[str] | None = None) -> int:
    args = build_parser().parse_args(arguments)
    try:
        config = load_config()
        model = args.model or config.model
        language = args.language or config.language
        formats = tuple(args.output or config.outputs)
        output_dir = args.output_dir or (
            Path(config.output_dir) if config.output_dir else Path.cwd() / "transcricoes"
        )
        if args.save_defaults:
            save_config(
                AppConfig(
                    model=model,
                    language=language,
                    outputs=formats,
                    output_dir=str(output_dir),
                    max_file_size_mb=config.max_file_size_mb,
                )
            )
        inputs = collect_batch_files(args.entrada) if args.batch else [args.entrada]
        if not args.batch and args.entrada.is_dir():
            raise ValueError("Para processar uma pasta, informe --batch.")
        if not inputs:
            raise ValueError("Nenhum arquivo compatível foi encontrado.")

        logger = configure_logging(args.verbose)
        engine = TranscriptionEngine(args.ffmpeg, args.whisper_cli, logger)
        failures = 0
        for item in inputs:
            request = TranscriptionRequest(
                input_file=item,
                output_dir=output_dir,
                model=model,
                language=language,
                formats=formats,
                model_path=args.model_path,
                keep_temp=args.keep_temp,
                quiet=args.quiet,
                max_file_size_mb=config.max_file_size_mb,
            )
            try:
                generated = engine.transcribe(request, _progress(args.quiet))
                if not args.quiet:
                    for path in generated:
                        print(path)
            except (FileNotFoundError, ValueError) as exc:
                print(f"Erro: {exc}", file=sys.stderr)
                failures += 1
            except RuntimeError as exc:
                print(f"Falha no processamento: {exc}", file=sys.stderr)
                failures += 1
        return EXIT_PROCESSING if failures else EXIT_OK
    except (FileNotFoundError, ValueError, NotADirectoryError) as exc:
        print(f"Erro: {exc}", file=sys.stderr)
        return EXIT_ARGUMENT
    except KeyboardInterrupt:
        print("Operação interrompida pelo usuário.", file=sys.stderr)
        return EXIT_INTERRUPTED


def main() -> None:
    raise SystemExit(run())


if __name__ == "__main__":
    main()
