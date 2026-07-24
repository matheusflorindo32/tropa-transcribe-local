# Módulo 4 — Instalação (2 h)

## Objetivos

Obter fonte oficial, compilar versão fixada, baixar modelo com integridade,
verificar instalação e diagnosticar falhas.

## Conteúdo e roteiro

**Conceito (15 min):** versão, tag, hash, assinatura e cadeia de suprimentos.
**Arquitetura (20 min):** diretório do app separa runtime, venv, modelos e
manifesto. **Implementação (55 min):** executar `instalar.ps1`, observar cada
pré-requisito e rodar `verificar.ps1`. **Comparação (15 min):** instalação
manual versus script idempotente. **Projeto real (15 min):** registrar
procedimento de recuperação sem desativar antivírus.

## Atividade

Preencha checklist: fontes, versão `v1.9.1`, executável, modelo, teste `--help`,
espaço e licença. Use `-SkipModel` quando download for inviável.

## Questionário e respostas comentadas

1. Por que fixar tag? **Reprodutibilidade e auditoria.**
2. Script instala ferramentas globais? **Não; para com orientação.**
3. Pode desativar antivírus? **Não; investigar origem, hash e falso positivo.**
4. Reexecutar é seguro? **Deve ser idempotente e preservar componentes.**

## Erros comuns

Executar como administrador sem necessidade, clonar fork desconhecido, misturar
modelo no Git e ignorar licença do FFmpeg.

## Conclusão

Ambiente verificado ou falha documentada como `NÃO TESTADO NESTE AMBIENTE`.

## Referências

[whisper.cpp quick start](https://github.com/ggml-org/whisper.cpp),
`docs/instalacao-windows.md` e `docs/licencas.md`.
