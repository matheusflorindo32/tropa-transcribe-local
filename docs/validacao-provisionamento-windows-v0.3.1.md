# Validação do provisionamento Windows v0.3.1-alpha

Data: 2026-07-24.

## Ambiente desta execução

- host Windows x64 build `26200`, 16 GiB RAM;
- processo sem elevação;
- Python de desenvolvimento `3.11.15`;
- Inno Setup `7.0.2` x64 instalado por usuário após validação de assinatura
  Authenticode `Pyrsys B.V.`, tamanho `17.020.192` bytes e SHA-256
  `5ad54ca3def786f8f4212552e54cc6d8d61329e2d24a1cfee0571d42c2684ff1`;
- Hyper-V/Windows Sandbox não puderam ser consultados sem elevação;
- portanto, este host **não é evidência de Windows 11 limpo**.

## Evidência upstream

- FFmpeg ZIP: tamanho `70.510.963`, SHA-256
  `8271471492f5ebe8ccf15a39fbdac4266db4832a4765ba5603b49da36aef2f36`;
- whisper.cpp ZIP: tamanho `7.982.101`, SHA-256
  `7d8be46ecd31828e1eb7a2ecdd0d6b314feafd82163038ab6092594b0a063539`;
- ambos foram baixados localmente, tiveram hash confirmado e conteúdo
  inventariado;
- `ffmpeg -version` confirmou build shared com Opus, sem `--enable-gpl` e sem
  `--enable-nonfree`;
- `whisper-cli --version` confirmou `1.9.1`.

## Resultados executados no host

```powershell
python -m ruff format --check .
python -m ruff check .
python -m mypy app tools
python -m pytest
python -m pip_audit
```

- Ruff format/check: aprovado.
- mypy estrito em `app` e `tools`: aprovado.
- pytest: `84 passed`; cobertura total `81,97%`, acima do mínimo de 80%.
- `pip-audit` dos requisitos concretos do pacote (`PySide6==6.11.1` e
  `PyInstaller==6.21.0`): nenhuma vulnerabilidade conhecida.
- A auditoria do ambiente compartilhado completo reprovou por pacotes do host
  não usados/incorporados pelo projeto; isso foi separado da auditoria do
  artefato para não apresentar falso sucesso.

A cobertura inclui download atômico, cancelamento/limpeza, manifesto adulterado,
URL insegura, redirecionamento não permitido, hash incorreto, traversal,
symlink, arquivo inesperado/DLL planting, pouco espaço e diagnóstico sem shell.

## Build e instalador local

- PyInstaller `6.21.0`, Python `3.11.15`, PySide6/Qt `6.11.1`;
- bundle `onedir`: 174 arquivos, 118.562.281 bytes;
- Inno Setup `7.0.2`: compilação aprovada;
- instalador: 33.009.457 bytes; SHA-256
  `012055a8b917fe128fc28aef29af654b4b4dcaae3fd1b607539532ac6aca4f04`;
- aplicativo instalado com desinstalador: 176 arquivos, 123.092.116 bytes;
- aplicativo + runtimes provisionados: 279.185.015 bytes;
- aplicativo + runtimes + modelo `small`: 766.786.982 bytes;
- assinatura: `NotSigned`, bloqueio de publicação;
- instalação silenciosa sem `/ACCEPTLICENSE=YES`: recusada com exit code `1`;
- instalação silenciosa controlada: exit code `0`, sem FFmpeg, whisper.cpp ou
  modelo incorporado;
- EXE instalado permaneceu aberto no smoke de inicialização;
- desinstalação silenciosa: exit code `0`, saída sintética externa preservada.

O compilador Inno Setup 7.0.2 exibe `Non-commercial use only`. Uso comercial
exige licenciamento adequado do Inno Setup ou reavaliação da ferramenta antes
da distribuição.

## Transcrição real pelo EXE empacotado

Teste local aprovado com voz sintética do Windows:

```text
EXE PyInstaller -> WAV sintético -> FFmpeg/OGG Opus ->
whisper.cpp v1.9.1 + small + CPU + pt -> TXT/SRT/VTT/JSON
```

As quatro saídas foram criadas e não vazias. O TXT resultou em:
`Este é um teste de transcrição local e privada.` O teste usa
`tests/integration/packaged-exe-smoke.ps1`.

## Defender

- antivírus e proteção em tempo real: ativos;
- definição: `1.455.328.0`;
- scans personalizados do bundle e instalador: executados;
- detecções recentes após os scans: zero;
- SmartScreen: não testado;
- Authenticode: ausente.

## Itens ainda obrigatórios em VM limpa

- instalar e abrir pelo instalador sem Python/toolchain;
- concluir o assistente e modelo `small`;
- transcrever OGG/Opus pelo EXE instalado para TXT/SRT/VTT/JSON;
- validar cancelamento, reparo, proxy, interrupção e pouco disco;
- revisar UX/acessibilidade;
- executar Microsoft Defender e registrar SmartScreen;
- testar atualização e desinstalação;
- obter/revisar assinatura Authenticode antes de qualquer publicação.
