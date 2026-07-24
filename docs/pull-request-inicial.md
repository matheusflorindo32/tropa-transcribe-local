# Pull request inicial

## Título

`feat: initialize Tropa Transcribe Local MVP and course foundation`

## Resumo

Cria núcleo local FFmpeg → whisper.cpp, CLI, GUI inicial, scripts Windows,
modelos, testes, CI, documentação técnica/jurídica e curso de 20 horas.

## Revisão sugerida

1. Segurança de subprocessos, downloads e desinstalação.
2. Contrato do `whisper-cli v1.9.1` e saídas.
3. Instalação em Windows limpo com FFmpeg/CMake/MSVC.
4. Licenças antes de qualquer distribuição binária.
5. Conteúdo pedagógico e campos administrativos.

## Evidências

- 48 testes em Python 3.11 e pytest 9.1.1; cobertura 84,99%.
- Ruff format/check e mypy: aprovados.
- pre-commit, Markdown e YAML: aprovados.
- wheel: construído.
- pip-audit em venv limpo: nenhuma vulnerabilidade conhecida.
- scan local: nenhum padrão de segredo e nenhum arquivo versionado >1 MiB.

## Não testado

FFmpeg, CMake e whisper-cli não existem no ambiente de desenvolvimento. Fluxo
real de áudio, compilação, GUI com PySide6, instaladores Windows e Linux/macOS
permanecem `NÃO TESTADO NESTE AMBIENTE`.
