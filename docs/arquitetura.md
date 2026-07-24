# Arquitetura

```text
CLI/GUI
  -> TranscriptionEngine
      -> valida entrada/modelo/formato
      -> FFmpeg: mídia -> WAV PCM s16le mono 16 kHz
      -> whisper-cli v1.9.1
      -> TXT/SRT/VTT/JSON na pasta escolhida
      -> remove workspace temporário
```

O núcleo não depende de PySide6. A GUI é adaptador opcional e executa o engine
em `QThread`. Serviços externos recebem sempre listas de argumentos; caminhos
não são concatenados em comandos. Modelo e executáveis são resolvidos antes do
processamento. O arquivo original é somente leitura.

## Decisões

- Python 3.11: tipos modernos e suporte estável.
- whisper.cpp: inferência local leve; versão de instalação fixada em `v1.9.1`.
- FFmpeg externo: evita redistribuição prematura e obrigações desconhecidas do
  build do usuário.
- PySide6 opcional: GUI madura e multiplataforma, com obrigações LGPL/GPL.
- stdlib no núcleo: menor superfície de dependências e instalação simples.

## Fronteiras futuras

Adaptadores permitem GPU, glossário, perfis e mecanismos alternativos sem
acoplar UI ao subprocesso. Diarização não integra o MVP: requer pesquisa,
modelos e validação de qualidade separada.
