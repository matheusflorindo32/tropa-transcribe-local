# Preparação da release v0.3.1-alpha

Estado: **código e artefatos experimentais locais; publicação bloqueada**.

## Escopo

- provisionamento Windows x64 sem Python, Git, CMake, Visual Studio Build Tools
  ou FFmpeg previamente instalados;
- manifesto imutável com URLs, versões, arquiteturas, tamanhos, hashes,
  licenças, origens, arquivos instalados e comandos de diagnóstico;
- assistente visual de primeiro uso com consentimento, estimativa de disco,
  progresso, cancelamento, reparo e mensagem final verificável;
- instalador Inno Setup por usuário contendo apenas app/bootstrap;
- inventário, SBOM, avisos e instruções de substituição das bibliotecas Qt;
- testes adversariais de download, manifesto, ZIP e DLL inesperada.

## Bloqueios mantidos

Não publicar executável, instalador, tag, release ou bundle público. Antes de
remover o bloqueio são necessárias, no mínimo:

- execução completa em Windows 11 limpo sem toolchain;
- transcrição real pelo EXE instalado de OGG/Opus autorizado ou sintético;
- confirmação de TXT, SRT, VTT e JSON;
- revisão visual/acessível e de cancelamento/reparo;
- Microsoft Defender e SmartScreen;
- assinatura Authenticode confiável;
- revisão de licenças e cadeia de suprimentos da build concreta.

Não fazem parte desta versão: diarização, resumo, nuvem, conta, telemetria,
auto-update ou integrações externas.
