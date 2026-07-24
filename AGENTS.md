# AGENTS.md

## Objetivo

Manter o Tropa Transcribe Local como sistema local, privado, educacional e
reproduzível. Priorize segurança, correção, compatibilidade e clareza.

## Arquitetura

- `app/transcription`: validação, formatos, orquestração e adaptador whisper.cpp.
- `app/services`: FFmpeg, arquivos temporários e modelos.
- `app/ui`: PySide6 opcional; nunca bloquear a UI.
- `scripts`: instalação e wrappers por sistema.
- `tools`: download, diagnóstico e inventário.
- `tests`, `docs` e `course`: QA, documentação e formação.

## Comandos obrigatórios

```bash
python -m pip install -e ".[dev]"
python -m ruff format --check .
python -m ruff check .
python -m mypy app tools
python -m pytest
python -m pip_audit
```

## Padrões

- Python 3.11+, tipos estritos, funções pequenas e mensagens em pt-BR.
- Nunca usar `shell=True`; argumentos externos devem ser listas.
- Validar caminhos, extensões, tamanho, modelos e formatos antes de executar.
- Não registrar transcrição, mídia, prompt, credencial ou caminho desnecessário.
- Preservar original; temporários são isolados e removidos por padrão.
- Novos fluxos exigem estados de sucesso, vazio, erro e cancelamento.

## Privacidade, segurança e licenças

Não adicionar telemetria, upload, API obrigatória ou coleta de conteúdo.
Modelos, binários, mídia, transcrições, `.env`, chaves e logs não podem ser
enviados. Consulte fontes oficiais atuais antes de alterar dependências,
downloads, flags, licenças ou versões. Preserve avisos de terceiros.

## Procedimento

1. Leia README, pyproject, docs de arquitetura/segurança/licenças e Git status.
2. Faça alteração pequena, reversível e compatível.
3. Atualize testes e documentação.
4. Execute os comandos obrigatórios e verifique segredos/arquivos grandes.
5. Registre como `NÃO TESTADO NESTE AMBIENTE` qualquer validação não executada.

## Definição de pronto

Código funcional, testes e cobertura aprovados, lint/tipos verdes, docs
atualizadas, sem segredos ou arquivos grandes e revisão explícita de
privacidade, segurança, acessibilidade e licença.
