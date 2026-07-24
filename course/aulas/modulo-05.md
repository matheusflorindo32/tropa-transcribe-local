# Módulo 5 — Transcrição prática (2 h)

## Objetivos

Transcrever mídia autorizada, escolher idioma/modelo, gerar TXT/SRT/VTT e usar
lote preservando originais.

## Conteúdo e roteiro

**Conceito (15 min):** segmentos, timestamps, idioma e formato de saída.
**Arquitetura (15 min):** validação → conversão → inferência → verificação →
limpeza. **Implementação (60 min):** executar um arquivo de WhatsApp exportado
com autorização ou fixture artificial; gerar TXT/SRT/VTT; processar pasta de
fixtures. **Comparação (15 min):** base versus small e idioma pt versus auto.
**Projeto real (15 min):** organizar pasta de projeto sem sincronização.

## Atividade

```powershell
tropa-transcribe "fixture.ogg" --language pt --output txt srt vtt
```

Revise cinco trechos e registre saída, tempo percebido e erros sem colar fala.

## Questionário e respostas comentadas

1. `--batch` faz o quê? **Processa arquivos compatíveis da pasta.**
2. Original é alterado? **Não.**
3. `--keep-temp` serve para? **Diagnóstico; aumenta risco/retenção.**
4. JSON é obrigatório? **Não; apenas quando selecionado/suportado.**

## Erros comuns

Processar pasta errada, sobrescrever manualmente resultados, usar auto sem
comparar e compartilhar transcrição bruta.

## Conclusão

TXT e SRT válidos, original intacto e revisão registrada.

## Referências

`README.md`, `docs/formatos-suportados.md` e ajuda `tropa-transcribe --help`.
