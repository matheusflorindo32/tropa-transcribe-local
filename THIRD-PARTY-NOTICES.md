# Avisos de terceiros

O código autoral do Tropa Transcribe Local usa MIT. As dependências abaixo não
são relicenciadas por este repositório.

| Componente | Uso | Licença oficial verificada | Distribuído aqui? |
|---|---|---|---|
| OpenAI Whisper | arquitetura e pesos de origem | MIT | não |
| ggml-org whisper.cpp | inferência local | MIT | download opcional |
| FFmpeg-Builds / FFmpeg | conversão de mídia | LGPL-3.0-or-later na build fixada | download opcional |
| Python | runtime do bundle experimental | PSF-2.0 | somente no bundle |
| PySide6/Qt for Python | GUI | LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only na wheel | somente no bundle |
| PyInstaller | empacotamento | GPL-2.0-or-later com exceção do bootloader | bootloader |
| Pesos Whisper ggml | inferência | MIT na origem selecionada | download opcional |
| Inno Setup 7.0.2 | compilação do instalador | licença própria do Inno Setup | não |

O FFmpeg pode ser compilado sob outras condições. A build selecionada é
`n8.1.2-31-g8c9502e9b0` shared, inclui `--enable-version3`, não inclui
`--enable-gpl` nem `--enable-nonfree` e traz `LICENSE.txt` LGPL v3. Antes de
publicar, revise configuração, fontes correspondentes, patentes/codecs e
obrigações aplicáveis.
PySide6 exige cumprimento da licença escolhida, inclusive requisitos da LGPL
quando aplicável. Consulte `docs/licencas.md`; isto não é parecer jurídico.
O manifesto legível por máquina está em `packaging/components.json` e o SBOM
CycloneDX em `sbom.cdx.json`. Cópias e referências adicionais estão em
`LICENSES/`.
