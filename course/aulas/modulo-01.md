# Módulo 1 — Fundamentos (2 h)

## Objetivos

Explicar ASR, diferenciar local/nuvem, descrever Whisper, whisper.cpp e FFmpeg e
reconhecer limitações.

## Conteúdo e roteiro

**Conceito (20 min):** áudio, fala, texto, modelo e inferência; transcrição não
é compreensão nem verdade. **Arquitetura (20 min):** mídia → FFmpeg → WAV →
Whisper → segmentos/tempos → TXT/SRT/VTT. **Implementação (40 min):** explorar
`--help`, extensões e aviso de precisão sem processar dado real. **Comparação
(20 min):** local reduz envio/depende de hardware; nuvem facilita escala/expõe
dados a terceiro. **Projeto real (20 min):** desenhar fluxo para aula
autorizada, com revisão e descarte.

## Atividade

Crie mapa com componentes, dados que entram/saem, confiança e quatro limites.

## Questionário e respostas comentadas

1. FFmpeg transcreve? **Não; decodifica e normaliza mídia.**
2. whisper.cpp é o Whisper original? **É implementação C/C++ independente,
   baseada no modelo Whisper.**
3. Local garante precisão? **Não; muda processamento, não elimina erro.**
4. SRT contém quê? **Texto, sequência e intervalos de tempo.**

## Erros comuns

Confundir contêiner com codec, IA com autoridade, modelo maior com perfeição e
“offline” com ausência de risco.

## Conclusão

Mapa correto, comparação com ao menos dois trade-offs e reconhecimento explícito
da revisão humana.

## Referências

[OpenAI Whisper](https://github.com/openai/whisper),
[whisper.cpp](https://github.com/ggml-org/whisper.cpp) e
[FFmpeg](https://ffmpeg.org/documentation.html).
