# Checklist de teste em Windows 11 limpo

Use snapshot de VM ou máquina física sem instalação anterior do aplicativo.
Registre versões e resultados sem anexar mídia, transcrição ou caminhos
sensíveis.

## Estado inicial

- [ ] Windows 11 x64 atualizado e conta padrão sem privilégio administrativo.
- [ ] Python, Git, CMake, Visual Studio Build Tools, FFmpeg, whisper.cpp e
  modelos não estão instalados.
- [ ] Pelo menos 3 GiB livres para app, runtimes, temporários e modelo `small`.
- [ ] Defender ativo; SmartScreen na política normal do ambiente.
- [ ] Proxy/rede e data/hora registrados sem expor credenciais.

## Instalador

- [ ] Hash do instalador interno confere com o relatório de build.
- [ ] Instalação interativa por usuário não pede elevação.
- [ ] Instalação silenciosa sem `/ACCEPTLICENSE=YES` é recusada.
- [ ] Instalação silenciosa controlada instala somente app/bootstrap.
- [ ] Aplicativo abre sem Python e sem DLL/toolchain global.
- [ ] Atualização/reparo não remove configurações nem transcrições.
- [ ] Desinstalação oferece runtimes e modelos separadamente.
- [ ] Saídas/transcrições permanecem após desinstalação.

## Primeiro uso

- [ ] O assistente declara processamento local e ausência de upload/telemetria.
- [ ] Componentes, tamanhos, espaço livre, licenças e pastas estão visíveis.
- [ ] Nenhum download começa antes do consentimento.
- [ ] `small` aparece recomendado e cabe no espaço disponível.
- [ ] Cancelamento remove `.part`, staging e não informa sucesso.
- [ ] Retomar após cancelamento conclui com clareza.
- [ ] Segunda execução reutiliza componentes íntegros.
- [ ] Reparar substitui somente após download/validação completa.
- [ ] Diagnósticos de FFmpeg e whisper.cpp retornam sucesso.

## Segurança e falhas induzidas

- [ ] URL HTTP, host/redirecionamento não permitido e manifesto adulterado são
  bloqueados.
- [ ] SHA-256/tamanho incorreto, ZIP truncado, traversal, symlink e nome
  ambíguo são bloqueados.
- [ ] DLL/arquivo inesperado no runtime reprova a validação.
- [ ] Queda de rede, timeout, proxy inválido e interrupção deixam estado
  anterior utilizável.
- [ ] Espaço insuficiente é detectado antes do download.
- [ ] Caminhos graváveis não permitem carregar componente não inventariado.
- [ ] Defender não detecta ameaça; resultado e definições são registrados.
- [ ] SmartScreen é registrado sem contornar a proteção.

## Transcrição real pelo EXE instalado

- [ ] Gere áudio sintético ou use OGG/Opus autorizado sem dados sensíveis.
- [ ] Adicione mídia por seletor e drag-and-drop.
- [ ] Execute CPU/idioma `pt`/modelo `small`.
- [ ] TXT, SRT, VTT e JSON são criados e não vazios.
- [ ] Progresso, cancelamento e erros não bloqueiam a interface.
- [ ] Caminhos com espaços e Unicode funcionam.
- [ ] Revise que mídia/transcrição não aparecem em logs ou diagnóstico.

## UX, acessibilidade e evidência

- [ ] Teclado, ordem de foco, leitor de tela, contraste e escalas 100/125/150%
  são revistos.
- [ ] Estados vazio, carregando, sucesso, erro, cancelado e reparo são claros.
- [ ] Sobre mostra versões, licenças, origem e ausência de afiliação.
- [ ] SBOM, inventário, manifesto e arquivos `LICENSES` acompanham o pacote.
- [ ] Tamanho do app, instalador, runtimes e modelo são registrados.
- [ ] Limitações e resultados reprovados constam na validação.
- [ ] Nenhum executável, instalador, tag, release ou bundle é publicado antes
  de todos os itens críticos aprovarem.
