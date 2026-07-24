# Componentes fixados do runtime Windows x64

Fonte de verdade legível por máquina:
`app/resources/runtime-windows-x64.json`. O aplicativo verifica o SHA-256 desse
manifesto antes de usá-lo.

## Runtimes

| Componente | Versão/build | Download | Instalado | Licença declarada |
|---|---|---:|---:|---|
| FFmpeg | `n8.1.2-31-g8c9502e9b0`, build shared LGPL de 2026-07-24 | 70.510.963 B | 143.244.259 B | LGPL-3.0-or-later |
| whisper.cpp | `v1.9.1`, binário oficial x64 | 7.982.101 B | 12.848.640 B | MIT |

URLs e SHA-256:

- FFmpeg:
  `https://github.com/BtbN/FFmpeg-Builds/releases/download/autobuild-2026-07-24-13-32/ffmpeg-n8.1.2-31-g8c9502e9b0-win64-lgpl-shared-8.1.zip`;
  SHA-256
  `8271471492f5ebe8ccf15a39fbdac4266db4832a4765ba5603b49da36aef2f36`.
- whisper.cpp:
  `https://github.com/ggml-org/whisper.cpp/releases/download/v1.9.1/whisper-bin-x64.zip`;
  SHA-256
  `7d8be46ecd31828e1eb7a2ecdd0d6b314feafd82163038ab6092594b0a063539`.

A build FFmpeg é produzida pelo projeto de terceiros FFmpeg-Builds, não pelo
site ffmpeg.org. A linha de configuração foi conferida: `--enable-shared`,
`--disable-static`, `--enable-version3`, sem `--enable-gpl` e sem
`--enable-nonfree`. O `LICENSE.txt` contido no ZIP é LGPL v3. Isso reduz risco
de licença, mas não substitui auditoria jurídica ou de patentes/codecs.

## Modelos

Os doze modelos do catálogo estão presos à revisão imutável
`5359861c739e955e79d9a303bcbc70fb988958b1` de
`ggerganov/whisper.cpp` no Hugging Face. Cada entrada contém tamanho exato e
SHA-256; não é usado `main`, `latest` nem ETag opcional.

O modelo recomendado `small`:

- arquivo: `ggml-small.bin`;
- download/instalação: 487.601.967 bytes;
- SHA-256:
  `1be3a9b2063867b937e64e2ec7483364a79917e157fa98c5d94b5c1fffea987b`;
- licença declarada na origem: MIT.

## Validação e arquivos instalados

O provisionador:

1. aceita somente HTTPS e hosts explicitamente permitidos;
2. usa arquivo `.part` aleatório e timeout;
3. confere tamanho exato e SHA-256 antes da promoção;
4. rejeita caminhos absolutos, `..`, nomes ambíguos, ZIP criptografado e
   symlink;
5. extrai somente arquivos enumerados, com tamanho e hash individuais;
6. promove o staging atomicamente e restaura a versão anterior em falha;
7. rejeita arquivo inesperado no diretório, inclusive DLL plantada;
8. executa diagnóstico com lista de argumentos, `shell=False`, diretório de
   trabalho confiável e `PATH` reduzido.

Diretórios:

```text
%LOCALAPPDATA%\TropaTranscribeLocal\runtime-v2
%LOCALAPPDATA%\TropaTranscribeLocal\models
```

Não há alteração do `PATH` global, instalação de compilador, elevação,
desativação do Defender, telemetria ou atualização automática.
