# Licenças incorporadas e substituição

Este diretório complementa `THIRD-PARTY-NOTICES.md`, `packaging/components.json`
e `sbom.cdx.json`. Ele não altera nem resume juridicamente as licenças originais.

- O código do Tropa Transcribe Local usa MIT (`../LICENSE`).
- Python é distribuído sob PSF License Version 2 e licenças históricas
  compatíveis. A cópia oficial acompanha a distribuição do Python e está em
  <https://docs.python.org/3/license.html>.
- A wheel PySide6/Qt for Python usada declara
  `LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only`; a Qt também oferece
  licenciamento comercial em outro regime. Consulte
  <https://doc.qt.io/qtforpython-6/licenses.html>.
- PyInstaller declara GPL-2.0-or-later com a exceção específica do bootloader para os
  bundles produzidos. Consulte
  <https://github.com/pyinstaller/pyinstaller/blob/v6.21.0/COPYING.txt>.
- whisper.cpp e os pesos Whisper selecionados usam MIT. As cópias de aviso
  estão neste diretório.
- A build FFmpeg selecionada é compartilhada e informa
  `LGPL-3.0-or-later` por ter sido compilada com `--enable-version3`. O próprio
  download contém `LICENSE.txt`, que é instalado ao lado do runtime.
- Inno Setup é ferramenta de build e não é incorporado ao instalador produzido.
  Consulte <https://jrsoftware.org/files/is/license.txt>.

## Substituição das bibliotecas Qt

O pacote Windows é `onedir`: as DLLs Qt permanecem bibliotecas compartilhadas,
sem modificação deliberada pelo projeto. Um usuário tecnicamente habilitado
pode substituir as DLLs compatíveis no diretório `_internal/PySide6` e os
plugins correspondentes em `_internal/PySide6/plugins`, mantendo nome,
arquitetura e ABI da mesma série Qt. Faça backup e valide o aplicativo depois
da troca. O instalador não impede essa substituição.

O código-fonte correspondente do PySide6/Qt usado na build pode ser obtido pelo
índice oficial da Qt for Python e pelos repositórios indicados em:
<https://code.qt.io/cgit/pyside/pyside-setup.git/>. A versão exata fica
registrada no inventário do artefato local.

Estas informações são uma trilha técnica de conformidade, não parecer jurídico
nem afirmação absoluta de suficiência para toda forma de distribuição.
