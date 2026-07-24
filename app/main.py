"""Ponto de entrada da interface gráfica opcional."""

from __future__ import annotations

import sys


def _run_headless_if_requested() -> None:
    """Expõe o mesmo núcleo no EXE para smoke controlado e automação local."""
    marker = "--headless-transcribe"
    if marker not in sys.argv:
        return
    arguments = [value for value in sys.argv[1:] if value != marker]
    from app.cli import run

    raise SystemExit(run(arguments))


def main() -> None:
    _run_headless_if_requested()
    try:
        from PySide6.QtWidgets import QApplication
    except ImportError:
        print("Interface não instalada. Execute: pip install -e .[gui]", file=sys.stderr)
        raise SystemExit(3) from None
    from app.ui.main_window import MainWindow

    application = QApplication(sys.argv)
    application.setApplicationName("Tropa Transcribe Local")
    application.setApplicationVersion("0.3.1-alpha")
    application.setOrganizationName("Tropa Científica")
    # Qt 6 usa Per-Monitor DPI Aware V2 no Windows e os widgets padrão
    # herdam preferências de contraste/escala. A interface não usa animações.
    window = MainWindow()
    window.show()
    raise SystemExit(application.exec())


if __name__ == "__main__":
    main()
