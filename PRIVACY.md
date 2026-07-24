# Política de privacidade do projeto

## Resumo

O aplicativo processa mídia no computador do usuário e não implementa upload,
conta, analytics ou telemetria. O projeto não recebe nem controla os arquivos
processados por instalações locais.

## Dados e locais

- Original: nunca é alterado.
- Temporário: WAV em `%LOCALAPPDATA%\TropaTranscribeLocal\temp` no Windows,
  diretório equivalente no Linux/macOS; removido ao final, salvo `--keep-temp`.
- Modelos: pasta local de dados do aplicativo.
- Saídas: pasta escolhida pelo usuário, padrão `transcricoes`.
- Configuração: modelo, idioma, formatos e destino; sem conteúdo ou credenciais.
- Logs: somente eventos operacionais quando habilitados; não devem conter
  transcrição.

## Responsabilidades

Processamento local reduz exposição externa, mas não garante conformidade
automática com a LGPD. Antes de transcrever, determine legitimidade da gravação,
base/finalidade, autorização quando aplicável, minimização, acesso, retenção e
exclusão. Dados pessoais sensíveis requerem salvaguardas proporcionais.

Revise backups, antivírus, indexação e sincronização automática: uma pasta
local pode estar dentro de OneDrive, iCloud, Dropbox ou solução corporativa.
Use volume protegido, controle de acesso e criptografia quando necessário.

Este documento é informativo e não constitui parecer jurídico.
