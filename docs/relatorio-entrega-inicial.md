# Relatório da entrega inicial

## Resumo executivo

O repositório contém MVP executável em Python para validar mídia, converter com
FFmpeg, transcrever por whisper.cpp e gerar TXT/SRT/VTT/JSON. Inclui lote, modo
silencioso, cancelamento, temporários, modelos, GUI opcional, scripts Windows,
CI, documentos de privacidade/licença e curso livre de 20 horas.

Funcionam e foram testados: validações, comandos sem shell, orquestração com
mocks, limpeza, configuração, lote, códigos básicos, diagnóstico, pacote e CLI.
Não foi possível validar inferência real porque FFmpeg, CMake, whisper-cli e
modelos não estão instalados neste ambiente.

## Arquivos

- 118 arquivos versionados.
- Criados: `app`, `scripts`, `tools`, `tests`, `.github`, `docs`, `course`,
  `examples` e documentos de governança.
- Reaproveitados: nenhum; o diretório inicial estava vazio.
- Removidos: nenhum arquivo do usuário.
- Modelos, mídia, transcrições, logs, segredos e binários são ignorados.

## Testes e qualidade

Comandos executados:

```text
python -m ruff format --check .
python -m ruff check .
python -m mypy app tools
python -m pytest
python -m pre_commit run --all-files
npx markdownlint-cli2 "**/*.md"
python -m pip wheel . --no-deps
python -m pip_audit --skip-editable
```

Resultado final: 48/48 testes, cobertura 84,99%, lint/tipos/pre-commit/Markdown/
YAML/PowerShell aprovados, wheel construído e auditoria limpa em venv isolado.
O ambiente global do Codex possui vulnerabilidades não relacionadas; por isso a
decisão foi auditar venv limpo e elevar pip/setuptools na CI/instalação.

`NÃO TESTADO NESTE AMBIENTE`: transcrição real, codecs, build C++, download de
modelo grande, PySide6 visual, acessibilidade assistiva, Windows limpo, Linux e
macOS.

## Licenças

Código próprio: MIT. Whisper e whisper.cpp: MIT. FFmpeg: LGPL-2.1+ ou GPL-2.0+
conforme build. PySide6: LGPLv3/GPLv3 ou comercial. PyInstaller: GPL com
exceção. Binários de terceiros não são redistribuídos. Antes de release, revisar
build FFmpeg/Qt, fontes correspondentes, SBOM, assinatura e patentes/codecs.

## Segurança e privacidade

Implementado: processamento local, sem telemetria/API, allowlists, limites,
subprocessos por lista, download atômico, hash, temporários isolados, logs sem
conteúdo, desinstalação limitada, permissões mínimas e scans.

Riscos: cadeia de suprimentos, codecs maliciosos, backup/nuvem local, acesso
físico, erro de ASR e uso indevido. Processamento local não garante LGPD.

## Curso

Dez módulos de duas horas, plano, matriz, guias, atividades, questionários,
gabaritos, rubrica, avaliação final, feedback, checklist e certificado textual.
Pendentes: revisão pedagógica, acessibilidade, identidade e validação
administrativa do certificado/contatos.

## Próxima fase

### Bloqueadores

1. Validar instalação/transcrição em Windows limpo com fixture artificial.
2. Auditar e selecionar distribuição licenciável de FFmpeg.
3. Validar download/hash e build whisper.cpp `v1.9.1`.

### Prioridade alta

1. Testar GUI, cancelamento e acessibilidade.
2. Criar release/instalador assinado com SBOM e hashes.
3. Revisar licenças e privacidade com responsáveis institucionais.

### Prioridade média

Linux/macOS, progresso mais preciso, perfis/glossários e testes de disco cheio/
timeout.

### Futuro

Diarização pesquisada, editor de legendas, revisão assistida e site.

## Pull request

Branch: `codex/initial-mvp`. O remoto não está configurado, portanto nenhum PR
foi criado ou publicado. Use o texto em `docs/pull-request-inicial.md`, adicione
um remoto aprovado, faça push da branch e abra PR sem merge automático.
