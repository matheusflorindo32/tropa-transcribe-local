# Instalação no macOS

**NÃO TESTADO NESTE AMBIENTE.**

1. Instale Xcode Command Line Tools, Python 3.11+, Git, CMake e FFmpeg por
   fontes confiáveis.
2. Confirme as versões no Terminal.
3. Compile whisper.cpp `v1.9.1` conforme documentação oficial. Apple Silicon
   pode usar Metal; valide o build e a licença.
4. Crie venv, instale `pip install -e .` e baixe o modelo.
5. Execute a CLI com caminho explícito para `build/bin/whisper-cli`.

`scripts/macos/instalar.sh` não instala ferramentas e apenas sinaliza ausências.
