# Licenças

O código autoral é oferecido sob MIT. Isso não relicencia componentes de
terceiros nem determina, sozinho, a licença de um pacote concreto.

A build FFmpeg fixada em `v0.3.1-alpha` é shared,
`n8.1.2-31-g8c9502e9b0`, compilada com `--enable-version3`, sem
`--enable-gpl` e sem `--enable-nonfree`. Ela inclui `LICENSE.txt` LGPL v3 e é
baixada somente após consentimento. Outras builds podem ser GPL ou conter
componentes não redistribuíveis; não as trate como equivalentes.

PySide6/Qt for Python Community declara
`LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only` na wheel; a alternativa
comercial é um regime separado. O bundle `onedir` conserva DLLs compartilhadas e não
impede substituição por bibliotecas compatíveis. Instruções, fontes e ressalvas
estão em `LICENSES/README.md`.

PyInstaller declara GPL-2.0-or-later com exceção para bundles. Nuitka é
AGPL-3.0 e adiciona
complexidade de compilação. A licença final de um binário depende de tudo que
ele contém. Antes de release: gerar inventário, registrar versões, obter fontes
correspondentes, revisar plugins Qt/FFmpeg e buscar revisão jurídica quando o
risco justificar.

Na alpha, o bundle incorpora Python, PySide6/Qt e o bootloader do PyInstaller.
FFmpeg, `whisper.cpp` e pesos permanecem downloads externos conforme
[`adr/0001-limite-de-binarios-externos.md`](adr/0001-limite-de-binarios-externos.md).
Consulte `packaging/components.json`, `sbom.cdx.json` e
`THIRD-PARTY-NOTICES.md`. A existência do inventário não substitui revisão
jurídica da distribuição concreta. Não se afirma conformidade absoluta antes
da revisão do artefato final e do contexto de distribuição.

O Inno Setup 7.0.2 usado no build local informa `Non-commercial use only`.
Antes de uso comercial, obtenha a licença apropriada do fornecedor ou
reavalie/valide outra ferramenta. O compilador não é incorporado ao instalador,
mas seus termos ainda se aplicam ao uso da ferramenta de build.
