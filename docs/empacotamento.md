# Decisão de empacotamento Windows

## Comparação

| Critério | PyInstaller | Nuitka | pyside6-deploy |
|---|---|---|---|
| Licença | GPL-2.0 com exceção | AGPL-3.0 | ferramenta Qt sobre Nuitka |
| Build | simples | compilação C, mais lenta | integrada ao PySide6 |
| Tamanho/startup | maior/normal | pode otimizar | otimizado para Qt |
| Antivírus | falsos positivos possíveis | também possíveis | depende do bundle |
| Manutenção | comunidade ampla | complexidade maior | alinhado ao Qt |
| Cross-build | não | não recomendado | por plataforma |

## Escolha da alpha

PyInstaller em modo `onedir`, como dependência opcional, pela previsibilidade e
diagnóstico mais simples. Não publicar `onefile` inicialmente: extração em
runtime e falsos positivos dificultam suporte. `pyside6-deploy` será reavaliado
quando a GUI estabilizar; Nuitka direto não traz benefício comprovado agora.

Antes de publicar: build em Windows limpo, SBOM, análise antivírus sem pedir
exclusões, assinatura Authenticode, teste sem Python instalado, avisos Qt,
origens/licenças de FFmpeg e whisper.cpp, hashes e política de atualização.
Nenhum binário foi publicado nesta entrega.

## Estrutura preparada

- `packaging/windows/tropa-transcribe-local.spec`: bundle PyInstaller `onedir`;
- `scripts/windows/build-gui.ps1`: build com códigos de saída verificados;
- `packaging/windows/installer.iss`: instalação por usuário com Inno Setup;
- `packaging/windows/PRE-RELEASE-NOTICE.txt`: aviso obrigatório de alpha;
- `packaging/components.json`: componentes incorporados e externos;
- `tools/generate_supply_chain.py`: SBOM e hashes do artefato.

Para gerar artefatos exclusivamente locais:

```powershell
.\scripts\windows\build-gui.ps1
.\scripts\windows\build-gui.ps1 -PythonPath ".\.venv\Scripts\python.exe"
.\scripts\windows\build-gui.ps1 -BuildInstaller
```

O bundle atual contém a GUI e avisos autorais, mas não inclui FFmpeg,
whisper.cpp nem modelos. PyInstaller precisa ser executado no Windows para
produzir um pacote Windows. `ISCC.exe` deve retornar `0`; códigos `1` e `2` são
tratados como falha.

## Bloqueios para distribuição

Uma build local de 113,01 MiB foi produzida e abriu em smoke; consulte
[`validacao-desktop-build-local.md`](validacao-desktop-build-local.md). O pacote
ainda não foi validado em Windows limpo. Permanecem obrigatórios:
teste visual/acessível da GUI, teste sem Python, antivírus, SBOM, hashes,
SmartScreen, instalador/desinstalação, assinatura Authenticode, política de atualização e revisão das obrigações de
Qt/PySide6 e de cada binário incorporado futuramente.
