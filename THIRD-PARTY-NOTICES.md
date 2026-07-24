# Avisos de terceiros

O código autoral do Tropa Transcribe Local usa MIT. As dependências abaixo não
são relicenciadas por este repositório.

| Componente | Uso | Licença oficial verificada | Distribuído aqui? |
|---|---|---|---|
| OpenAI Whisper | arquitetura e pesos de origem | MIT | não |
| ggml-org whisper.cpp | inferência e modelos ggml | MIT | não |
| FFmpeg | conversão de mídia | LGPL-2.1+ ou GPL-2.0+, conforme build | não |
| Python | runtime do bundle experimental | PSF-2.0 | somente no bundle |
| PySide6/Qt for Python | GUI | LGPL-3.0/GPL-3.0 ou comercial | somente no bundle |
| PyInstaller | empacotamento | GPL-2.0 com exceção do bootloader | bootloader |
| Inno Setup | compilação do instalador | licença própria do Inno Setup | não |

FFmpeg pode incluir componentes GPL ou não redistribuíveis. Antes de publicar
binário, registre configuração, fontes correspondentes e obrigações aplicáveis.
PySide6 exige cumprimento da licença escolhida, inclusive requisitos da LGPL
quando aplicável. Consulte `docs/licencas.md`; isto não é parecer jurídico.
O manifesto legível por máquina está em `packaging/components.json` e o SBOM
CycloneDX em `sbom.cdx.json`.
