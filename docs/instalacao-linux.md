# Instalação no Linux

**NÃO TESTADO NESTE AMBIENTE.**

1. Instale pelos repositórios oficiais da distribuição: Python 3.11+, Git,
   CMake, compilador C++ e FFmpeg.
2. Confirme `python3 --version`, `git --version`, `cmake --version`,
   `c++ --version` e `ffmpeg -version`.
3. Clone whisper.cpp `v1.9.1`, rode `cmake -B build` e
   `cmake --build build --config Release --parallel`.
4. Crie `python3 -m venv .venv`, ative e instale `pip install -e .`.
5. Baixe `python tools/download_model.py base`.
6. Informe `--whisper-cli /caminho/build/bin/whisper-cli`.

O script `scripts/linux/instalar.sh` apenas verifica dependências nesta versão;
ele não instala pacotes globais.
