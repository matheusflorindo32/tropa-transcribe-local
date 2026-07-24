# Validação Windows real

## Registro da execução de 24 de julho de 2026

Uma transcrição real foi concluída em Windows 11 antes da estabilização
`0.2.0-beta`, com o seguinte ambiente informado:

- FFmpeg 8.1.2;
- Visual Studio Build Tools 2022 e CMake;
- whisper.cpp compilado localmente;
- `whisper-cli.exe` em configuração Release;
- modelo multilíngue `ggml-small.bin`;
- áudio OGG/Opus originado do WhatsApp;
- processamento em CPU;
- idioma `pt`.

O conteúdo do áudio, a transcrição e caminhos pessoais não são registrados
neste documento. O teste comprovou a viabilidade do pipeline real, mas expôs
falhas de automação: sucesso indevido após erro, seleção de NMake fora do
Developer Shell, divergência de diretórios de modelo e descoberta manual do
executável.

## Correções introduzidas na versão 0.2.0-beta

- cada comando nativo tem seu código de saída verificado;
- o manifesto só é gravado depois de build e `whisper-cli --help` aprovados;
- `vswhere.exe` localiza uma instalação com as ferramentas C++ requeridas;
- `VsDevCmd.bat` é carregado no processo e `VSCMD_VER` é conferido;
- CMake usa `Visual Studio 17 2022`, arquitetura x64 e instância explícita;
- caches antigos de NMake são recriados apenas dentro do runtime gerenciado;
- modelos são gravados em `%LOCALAPPDATA%\TropaTranscribeLocal\models`;
- download usa arquivo temporário único e renomeação atômica;
- tamanho mínimo por modelo e SHA-256 registrado são validados;
- `whisper-cli.exe` é procurado em `build\bin\Release` e `build\bin`;
- o wrapper de transcrição só declara sucesso após código zero e saídas válidas.

## Teste de integração reproduzível

O teste gera fala artificial pela voz instalada no Windows e percorre o fluxo
completo FFmpeg → whisper.cpp → TXT/SRT/VTT:

```powershell
Set-ExecutionPolicy -Scope Process RemoteSigned
.\tests\integration\windows-real-smoke.ps1 -Model small
```

Critérios de aprovação:

1. o WAV artificial é criado;
2. `transcrever.ps1` retorna código `0`;
3. existe exatamente uma saída TXT, SRT e VTT;
4. todas as saídas são não vazias.

O texto reconhecido pode variar conforme voz, CPU e modelo; por isso o teste
não exige correspondência literal. Use `-KeepArtifacts` para investigação.

## Estado da evidência

A execução OGG/Opus real acima foi informada como aprovada no ambiente de
origem.

Em 24 de julho de 2026, a versão estabilizada também foi executada no Windows:

- Windows 11 x64, PowerShell 7.6.4 e Python 3.11.15;
- Visual Studio Build Tools 2022 17.14.37;
- CMake 3.31.6-msvc6 com gerador Visual Studio 17 2022 x64;
- FFmpeg 8.1.2 full build;
- whisper.cpp v1.9.1 e `build\bin\Release\whisper-cli.exe`;
- `ggml-small.bin` com 487.601.967 bytes;
- SHA-256 local e `X-Linked-ETag` iguais a
  `1be3a9b2063867b937e64e2ec7483364a79917e157fa98c5d94b5c1fffea987b`.

Resultados:

1. tentativa sem CMake no `PATH` falhou sem mensagem de sucesso;
2. descoberta em diretório padrão permitiu configurar e compilar;
3. ETag do CDN Xet foi corretamente descartado como hash do payload;
4. download, tamanho e SHA-256 do modelo foram aprovados;
5. segunda instalação reutilizou o modelo íntegro;
6. `verificar.ps1` foi aprovado;
7. smoke com voz artificial gerou TXT, SRT e VTT não vazios.

Ainda falta executar o checklist em uma máquina Windows realmente limpa. O
bundle PyInstaller e o instalador Inno Setup não foram construídos: havia
somente 1,7 GiB livres ao final da validação, espaço inadequado para afirmar
um teste de empacotamento confiável. Não há alegação de validação visual,
antivírus, acessibilidade, assinatura ou instalação/desinstalação nesta fase.
