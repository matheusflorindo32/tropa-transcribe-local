# Checklist de teste em Windows limpo

Use uma VM ou máquina sem instalação anterior do Tropa Transcribe Local.
Registre versões e resultados sem anexar mídia, transcrição ou caminhos
sensíveis.

## Preparação

- [ ] Windows 11 x64 atualizado, conta sem privilégios administrativos.
- [ ] Git, CMake, Python 3.11/3.12 e FFmpeg obtidos de fontes confiáveis.
- [ ] Visual Studio Build Tools 2022 com **Desktop development with C++**.
- [ ] Pelo menos 10 GiB livres e 8 GiB de RAM para testar o modelo `small`.
- [ ] Repositório em caminho local com espaços, por exemplo
  `C:\Projetos de teste\tropa-transcribe-local`.

## Instalação e idempotência

- [ ] `instalar.ps1 -Model small` retorna `0`.
- [ ] O CMake registra `Visual Studio 17 2022`, nunca NMake.
- [ ] `installation.json` contém versão, ambiente e caminhos existentes.
- [ ] `ggml-small.bin` está somente no diretório `models` configurado.
- [ ] O SHA-256 do modelo corresponde ao arquivo.
- [ ] Uma segunda execução reutiliza clone, venv, build e modelo íntegros.
- [ ] Uma falha induzida de CMake retorna código diferente de zero e não exibe
  sucesso.
- [ ] Um download interrompido não deixa `ggml-small.bin` parcial.

## Funcional

- [ ] `verificar.ps1` retorna `0`.
- [ ] `windows-real-smoke.ps1 -Model small` retorna `0`.
- [ ] OGG/Opus do WhatsApp autorizado gera TXT, SRT e VTT.
- [ ] Caminhos com espaços, acentos e arquivo grande plausível funcionam.
- [ ] Erro do `whisper-cli` é propagado sem mensagem de conclusão.
- [ ] Temporários são removidos por padrão e preservados com `-KeepTemp`.

## GUI e pacote

- [ ] Bundle PyInstaller `onedir` abre sem Python global.
- [ ] Loading, sucesso, vazio, erro e cancelamento são testados.
- [ ] Teclado, foco, contraste, leitor de tela e escala de 125/150% são revistos.
- [ ] Inno Setup instala por usuário, atualiza, repara e desinstala.
- [ ] Nenhum modelo, FFmpeg ou whisper.cpp foi incorporado acidentalmente.
- [ ] Defender e serviço antivírus institucional não detectam ameaça.
- [ ] SBOM, hashes, assinatura Authenticode e licenças foram revistos.

## Evidência final

- [ ] Versões e data registradas em `docs/validacao-windows-real.md`.
- [ ] Limitações e resultados reprovados permanecem explícitos.
- [ ] Nenhum binário é publicado antes de todos os itens críticos aprovarem.
