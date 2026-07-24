# Módulo 3 — Preparação do ambiente (2 h)

## Objetivos

Inventariar CPU, RAM, disco e ferramentas; distinguir requisito, recomendação e
aceleração; produzir diagnóstico sanitizado.

## Conteúdo e roteiro

**Conceito (20 min):** CPU/GPU, memória, armazenamento, compilador e PATH.
**Arquitetura (20 min):** Python coordena, FFmpeg converte, CMake/compilador
constroem e whisper.cpp infere. **Implementação (45 min):** executar versões e
`python tools/check_environment.py`. **Comparação (20 min):** tiny/base/small
por RAM, disco, velocidade e qualidade. **Projeto real (15 min):** recomendar
modelo para dois computadores fictícios.

## Atividade

Entregue tabela sem usuário/caminho pessoal: sistema, Python, Git, CMake,
FFmpeg, compilador, RAM, disco e modelo sugerido.

## Questionário e respostas comentadas

1. CMake é compilador? **Não; gera/configura o build.**
2. GPU é obrigatória? **Não para CPU build, mas pode acelerar.**
3. Por que deixar disco livre? **Modelo, WAV temporário, saídas e build.**
4. PATH serve para quê? **Localizar executáveis por nome.**

## Erros comuns

Confundir PowerShell e Prompt, instalar sem reabrir terminal, divulgar caminho
pessoal e escolher large sem medir recursos.

## Conclusão

Diagnóstico reproduzível, sanitizado e recomendação coerente.

## Referências

[Python Windows](https://docs.python.org/3.12/using/windows.html),
[CMake](https://cmake.org/documentation/) e `docs/modelos-whisper.md`.
