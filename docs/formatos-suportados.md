# Formatos suportados

O validador aceita OGG, OPUS, MP3, WAV, M4A, AAC, FLAC, MP4, MOV, MKV e WEBM.
O FFmpeg local deve conseguir decodificar o codec contido no arquivo. Contêiner
e codec não são a mesma coisa; dois arquivos `.mp4` podem exigir decodificadores
diferentes.

O fluxo normaliza tudo para WAV PCM 16-bit, mono, 16 kHz, formato documentado
pelo `whisper-cli`. Rode `ffmpeg -formats` e `ffmpeg -codecs` para investigar.
Suporte real a cada combinação permanece dependente do build instalado.
