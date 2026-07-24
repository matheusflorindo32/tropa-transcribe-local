# Validação local do build desktop

- Data: 2026-07-24
- Escopo: estação de desenvolvimento Windows; **não é Windows limpo**
- Versão: `0.3.0-alpha`
- Python da build: 3.11.15
- PyInstaller: 6.21.0
- PySide6/Qt: 6.11.1

## Resultados

- Bundle PyInstaller `onedir`: aprovado.
- Inicialização do `.exe` sem processo Python externo: aprovada em smoke de 3 segundos.
- Arquivos: 168.
- Tamanho: 118.504.745 bytes (113,01 MiB).
- SHA-256 do `TropaTranscribeLocal.exe`:
  `82441027a774ff75c501a8d86fd005799a7d23dd18c7d079132dbe031307a6d8`.
- SHA-256 do manifesto de 168 arquivos:
  `6eb5855776275c6a33cb0f25bedbb0a4d378fd949902e7dd8a65c709de61d8c5`.
- SBOM e manifesto de hashes: gerados em `dist/manifest` (não versionados).
- Microsoft Defender: antivírus e proteção em tempo real ativos; assinatura
  `1.455.328.0`; varredura personalizada concluída, zero detecções associadas
  ao bundle.
- Inno Setup: não instalado; instalador não foi construído.
- SmartScreen, Authenticode, atualização e desinstalação: não testados.
- Transcrição pelo `.exe`: não validada nesta rodada.

O bundle local e seu hash são efêmeros: uma nova build altera componentes e
hashes. Nenhum artefato foi publicado ou adicionado ao Git.
