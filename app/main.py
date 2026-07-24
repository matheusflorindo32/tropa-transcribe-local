"""Ponto de entrada da interface gráfica opcional."""

from __future__ import annotations

import sys


def main() -> None:
    try:
        from PySide6.QtWidgets import QApplication
    except ImportError:
        print("Interface não instalada. Execute: pip install -e .[gui]", file=sys.stderr)
        raise SystemExit(3) from None
    from app.ui.main_window import MainWindow

    application = QApplication(sys.argv)
    application.setApplicationName("Tropa Transcribe Local")
    window = MainWindow()
    window.show()
    raise SystemExit(application.exec())


if __name__ == "__main__":
    main()
