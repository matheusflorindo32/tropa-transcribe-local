# Licenças

MIT é compatível para o código autoral porque integra executáveis externos e
não incorpora código de terceiros. Cada componente preserva sua licença.

FFmpeg é LGPL-2.1+ por padrão, mas opções GPL alteram a licença; builds
`--enable-nonfree` podem não ser redistribuíveis. O MVP exige instalação externa
e não publica FFmpeg. PySide6 Community é LGPLv3/GPLv3; distribuição futura
deve permitir substituição/relink conforme a LGPL e incluir avisos/fontes
aplicáveis, ou usar licença comercial.

PyInstaller usa GPL-2.0 com exceção para bundles. Nuitka é AGPL-3.0 e adiciona
complexidade de compilação. A licença final de um binário depende de tudo que
ele contém. Antes de release: gerar inventário, registrar versões, obter fontes
correspondentes, revisar plugins Qt/FFmpeg e buscar revisão jurídica quando o
risco justificar.
