# Solução de problemas

## “FFmpeg não encontrado”

Rode `ffmpeg -version`. Reabra o terminal após instalar e confirme que o
executável está no `PATH`, ou passe `--ffmpeg "C:\...\ffmpeg.exe"`.

## “whisper-cli não encontrado”

Rode `.\scripts\windows\verificar.ps1`. Confira
`build\bin\Release\whisper-cli.exe`; builds não Visual Studio podem usar
`build\bin\whisper-cli.exe`.

## “Modelo não encontrado”

```powershell
python tools\download_model.py base
```

Ou passe `--model-path`. Arquivo menor que 1 KiB é rejeitado.

## Codec inválido

Use `ffmpeg -i "arquivo"` e confira se o build contém o decoder. Não renomeie
extensão para forçar suporte. Atualize FFmpeg por fonte confiável.

## Lentidão ou memória

Teste `tiny`/`base`, feche aplicações e deixe espaço livre. Modelos maiores não
garantem ganho proporcional em todo áudio.

## Acentos, espaços e OneDrive

O código suporta Unicode e lista de argumentos. Erros restantes podem vir de
permissão, sincronização, caminho longo ou componente externo. Teste pasta local
curta e protegida, sem mover o original.

## Diagnóstico

```powershell
python tools\check_environment.py --json
```

Antes de compartilhar, remova caminhos, nomes e outros dados pessoais.
