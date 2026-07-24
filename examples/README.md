# Exemplos

Arquivos deste diretório são configurações textuais, sem mídia real. Gere uma
fixture artificial localmente para testes. Não envie gravações, modelos ou
transcrições ao repositório.

```powershell
tropa-transcribe "C:\fixtures\voz-sintetica.wav" `
  --model base --language pt --output txt srt vtt
```
