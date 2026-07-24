# Pull request — estabilização Windows v0.2.0-beta

## Contexto

A primeira transcrição OGG/Opus real funcionou, mas revelou falso sucesso,
ambiente C++ não carregado, seleção indevida do NMake, divergência no diretório
do modelo, validação fraca de integridade e descoberta manual do executável.

## Alterações

- adiciona camada PowerShell compartilhada para processos nativos, Visual
  Studio, manifesto atômico e descoberta do `whisper-cli`;
- torna instalação e download de modelo idempotentes e verificáveis;
- reforça tamanho mínimo e SHA-256 do modelo;
- propaga falhas reais da transcrição;
- adiciona smoke test com fala artificial e checklist de Windows limpo;
- registra validação real e prepara a release de código-fonte;
- prepara, sem publicar, PyInstaller `onedir` e Inno Setup.

## Validação

- [x] Ruff format/check
- [x] mypy estrito
- [x] pytest e cobertura mínima
- [x] pip-audit e verificações do repositório
- [x] sintaxe PowerShell
- [x] smoke real pós-correção no computador com modelo `small`
- [ ] pacote GUI e Inno Setup em Windows limpo

## Segurança, privacidade e licenças

Não há telemetria ou upload. Modelos, mídia, transcrições e binários continuam
fora do Git. Downloads usam origem fixa, SHA-256 quando exposto pelo LFS e
gravação atômica. O pacote não incorpora dependências externas nesta fase.

## Limitações

O teste automatizado de unidade não substitui a repetição do pipeline real. A
GUI empacotada ainda exige validação visual, acessível, antivírus, licença,
SBOM e assinatura antes de qualquer distribuição.
