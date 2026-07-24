#!/usr/bin/env bash
set -euo pipefail
command -v git >/dev/null || { echo "Git não encontrado."; exit 1; }
command -v cmake >/dev/null || { echo "CMake não encontrado."; exit 1; }
command -v ffmpeg >/dev/null || { echo "FFmpeg não encontrado."; exit 1; }
command -v python3 >/dev/null || { echo "Python 3 não encontrado."; exit 1; }
echo "Instalação macOS automatizada ainda é experimental."
echo "Siga docs/instalacao-macos.md. Nenhuma ferramenta global foi instalada."
