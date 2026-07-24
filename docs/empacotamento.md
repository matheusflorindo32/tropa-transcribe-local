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

## Escolha do MVP

PyInstaller em modo `onedir`, como dependência opcional, pela previsibilidade e
diagnóstico mais simples. Não publicar `onefile` inicialmente: extração em
runtime e falsos positivos dificultam suporte. `pyside6-deploy` será reavaliado
quando a GUI estabilizar; Nuitka direto não traz benefício comprovado agora.

Antes de publicar: build em Windows limpo, SBOM, análise antivírus sem pedir
exclusões, assinatura Authenticode, teste sem Python instalado, avisos Qt,
origens/licenças de FFmpeg e whisper.cpp, hashes e política de atualização.
Nenhum binário foi publicado nesta entrega.
