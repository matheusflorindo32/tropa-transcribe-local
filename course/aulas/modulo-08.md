# Módulo 8 — Interface gráfica (2 h)

## Objetivos

Operar GUI, explicar worker thread, lidar com erro/cancelamento e avaliar
acessibilidade e privacidade.

## Conteúdo e roteiro

**Conceito (15 min):** evento, estado e feedback. **Arquitetura (20 min):** main
thread renderiza; worker executa engine; sinais atualizam progresso.
**Implementação (45 min):** selecionar/arrastar fixture, modelo, idioma, saídas
e destino; cancelar uma simulação. **Comparação (20 min):** CLI é melhor para
automação; GUI para descoberta e operação assistida. **Projeto real (20 min):**
teste de teclado, escala, contraste e redução de movimento.

## Atividade

Percorra sem mouse: selecionar, configurar, iniciar, cancelar e abrir saída.
Registre barreiras; não declare acessibilidade aprovada sem tecnologia assistiva.

## Questionário e respostas comentadas

1. Por que worker? **Evita congelar UI.**
2. Cancelar é instantâneo? **Depende do subprocesso; é solicitação controlada.**
3. GUI envia arquivo? **Não; usa o mesmo engine local.**
4. Progresso é exato? **É aproximado no MVP.**

## Erros comuns

Botão sem foco, mensagem técnica crua, fechar durante processo sem política e
assumir que aparência moderna equivale a acessibilidade.

## Conclusão

Fluxo completo e relatório de acessibilidade com evidência/limites.

## Referências

[Qt for Python](https://doc.qt.io/qtforpython-6/) e código `app/ui`.
