# Fontes técnicas verificadas

Consulta realizada em 24 de julho de 2026. Revalidar antes de atualizar
dependências ou publicar binários.

- [OpenAI Whisper](https://github.com/openai/whisper): instalação, modelos,
  FFmpeg e licença MIT.
- [whisper.cpp](https://github.com/ggml-org/whisper.cpp): build CMake,
  `whisper-cli`, WAV PCM 16-bit, modelos e memória.
- [CLI do whisper.cpp](https://github.com/ggml-org/whisper.cpp/tree/master/examples/cli):
  flags `--output-txt`, `--output-srt`, `--output-vtt`, `--output-json`,
  `--output-file`, `--language`, `--model` e `--file`.
- [Release v1.9.1](https://github.com/ggml-org/whisper.cpp/releases/tag/v1.9.1):
  referência fixada pelo instalador.
- [Licença do whisper.cpp](https://github.com/ggml-org/whisper.cpp/blob/master/LICENSE):
  MIT.
- [FFmpeg Legal](https://ffmpeg.org/legal.html): LGPL/GPL e checklist.
- [Python no Windows](https://docs.python.org/3.12/using/windows.html) e
  [venv](https://docs.python.org/3.12/tutorial/venv.html).
- [CMake](https://cmake.org/cmake/help/latest/guide/user-interaction/index.html).
- [GitHub Actions](https://docs.github.com/en/actions/reference/workflows-and-actions)
  e [permissões](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax).
- [Qt for Python](https://doc.qt.io/qtforpython-6/), sua
  [licença](https://doc.qt.io/qt-6/licensing.html) e
  [deployment](https://doc.qt.io/qtforpython-6.8/deployment/index.html).
- [PyInstaller](https://pyinstaller.org/en/stable/) e
  [licença](https://pyinstaller.org/en/stable/license.html).
- [Nuitka](https://nuitka.net/user-documentation/user-manual.html) e
  [download/licença](https://nuitka.net/doc/download.html).

Não há uso da API da OpenAI nem necessidade de chave. Whisper e whisper.cpp
são projetos distintos; este software integra o segundo.
