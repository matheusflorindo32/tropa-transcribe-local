# Do áudio do WhatsApp à transcrição local

## Objetivo

Transcrever um áudio OGG/Opus autorizado, revisar criticamente o resultado e
exportar arquivos sem enviar a mídia a serviços externos.

## 1. Preparação e autorização

Confirme que você tem autorização ou base legal para tratar o áudio. Defina
finalidade, responsáveis, prazo de retenção e quem pode acessar original e
transcrição. Use uma cópia de trabalho; preserve o original quando ele tiver
valor probatório ou acadêmico.

## 2. Instalação e diagnóstico

Siga o guia Windows, abra a GUI e escolha **Diagnóstico**. Só continue quando
FFmpeg, `whisper-cli` e o modelo aparecerem íntegros. Não desative o Defender.
No gerenciador, `small` é a recomendação geral para pt-BR.

## 3. Transcrição

1. Exporte ou copie o `.ogg` do WhatsApp para uma pasta local autorizada.
2. Selecione ou arraste o arquivo para a fila.
3. Escolha idioma `pt`, modelo `small`, formatos TXT/SRT/VTT/JSON e destino.
4. Acione **Transcrever** e acompanhe o progresso do arquivo e o total.
5. Se precisar interromper, use **Cancelar** e espere a finalização segura.

## 4. Revisão e exportação

Compare a prévia com o áudio. Revise nomes, números, siglas, termos técnicos,
mudanças de falante e trechos inaudíveis. Copie o TXT somente para um destino
autorizado. SRT/VTT servem para legendas e JSON para processamento estruturado;
conteúdo automático não substitui revisão humana.

## 5. Descarte

Confirme os arquivos exportados e elimine cópias de trabalho e temporários de
acordo com a política definida. O aplicativo remove WAV temporário por padrão;
`--keep-temp` não deve ser usado sem necessidade. Excluir o modelo é opcional e
não exclui transcrições.

## Erros comuns

- **Modelo ausente/corrompido:** abra Modelos, baixe novamente e aguarde validação.
- **FFmpeg ou whisper-cli ausente:** execute o diagnóstico e siga o guia Windows.
- **OGG não abre:** confirme que a build do FFmpeg contém o codec Opus.
- **Pouco espaço:** libere espaço autorizado; o download precisa de margem para
  temporário e validação.
- **Texto incorreto:** confira idioma/modelo, qualidade do áudio e faça revisão.
- **Cancelamento:** não force o encerramento; espere a mensagem de cancelado.
