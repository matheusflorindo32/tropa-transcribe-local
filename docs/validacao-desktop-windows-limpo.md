# Checklist de validação desktop em Windows 11 limpo

> Resultado atual: **não executado**. Não publicar instalador enquanto qualquer
> item obrigatório estiver pendente.

## Máquina e evidências

- [ ] Windows 11 atualizado, VM/snapshot novo e conta sem privilégios elevados.
- [ ] Confirmar ausência inicial de Python, Git e CMake.
- [ ] Microsoft Defender e SmartScreen ativos; registrar versões e capturas.
- [ ] Registrar CPU, RAM, espaço livre, data e hash SHA-256 do instalador.

## Instalação e primeira execução

- [ ] Instalar em pasta padrão e depois repetir em pasta com espaços e acentos.
- [ ] Confirmar que nenhuma credencial ou elevação é solicitada.
- [ ] Confirmar que nenhuma proteção é alterada e nenhuma ferramenta global é instalada.
- [ ] Abrir o `.exe` sem Python instalado e conferir versão `0.3.1-alpha`.
- [ ] Navegar somente por teclado; conferir foco, leitura e escala 100%, 150% e 200%.
- [ ] Ativar redução de movimento e confirmar ausência de animações próprias.

## Componentes e transcrição

- [ ] Assistente deve identificar FFmpeg/whisper/modelo ausentes sem falso sucesso.
- [ ] Provisionar runtimes pelo assistente e repetir diagnóstico.
- [ ] Baixar `small`; interromper uma vez e confirmar remoção do parcial.
- [ ] Repetir download, conferir tamanho, SHA-256 e espaço livre.
- [ ] Transcrever áudio OGG/Opus autorizado com nome Unicode e espaço.
- [ ] Validar TXT, SRT, VTT e JSON, prévia, cópia e abertura da pasta.
- [ ] Cancelar conversão/transcrição e confirmar ausência de falso sucesso.
- [ ] Testar fila múltipla, duplicata, arquivo ausente e modelo corrompido.

## Atualização, segurança e remoção

- [ ] Instalar uma atualização sobre versão anterior sem perder configurações ou saídas.
- [ ] Executar verificação completa do bundle e instalador no Defender.
- [ ] Registrar detecção, quarentena ou ausência de alerta sem criar exceções.
- [ ] Registrar comportamento do SmartScreen e identidade do publisher.
- [ ] Desinstalar preservando transcrições, runtimes e modelos.
- [ ] Reinstalar e testar escolhas separadas de excluir runtimes e modelos.
- [ ] Verificar arquivos remanescentes, logs de instalação e entrada de desinstalação.
