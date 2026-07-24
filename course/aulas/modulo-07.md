# Módulo 7 — Automação (2 h)

## Objetivos

Automatizar lote com PowerShell, nomes seguros, códigos de saída e integrações
opcionais sem expor conteúdo.

## Conteúdo e roteiro

**Conceito (15 min):** automação repetível, idempotência e código de saída.
**Arquitetura (20 min):** entrada controlada → CLI → saídas → revisão → arquivo.
**Implementação (50 min):** usar `transcrever.ps1`, parâmetros e pasta de
fixtures. **Comparação (20 min):** PowerShell, Obsidian e n8n; n8n é extensão
opcional e pode introduzir rede/credenciais. **Projeto real (15 min):** fluxo
noturno local que para ao primeiro erro e nunca apaga original.

## Atividade

Crie script que recebe pasta, usa lista de argumentos, verifica `$LASTEXITCODE`
e grava somente status. Não use `Invoke-Expression`, `shell=True` ou conteúdo em
log.

## Questionário e respostas comentadas

1. Código zero indica? **Conclusão conforme contrato.**
2. Por que lista de argumentos? **Evita interpretação indevida do shell.**
3. Obsidian pode sincronizar? **Sim; revisar configuração.**
4. n8n é obrigatório? **Não; é extensão futura/opcional.**

## Erros comuns

Senha em script, glob destrutivo, nome baseado em conteúdo e automação sem
limite/critério de parada.

## Conclusão

Script seguro, erro tratado e original preservado.

## Referências

[PowerShell docs](https://learn.microsoft.com/powershell/) e `AGENTS.md`.
