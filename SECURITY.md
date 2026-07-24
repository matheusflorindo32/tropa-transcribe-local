# Política de segurança

## Versões

A versão `0.1.x` está em desenvolvimento. Não é adequada, sem avaliação
institucional adicional, para fluxo pericial, clínico, sigiloso ou crítico.

## Relato responsável

Contato privado pendente: `[INSERIR E-MAIL INSTITUCIONAL]`. Não abra issue com
exploit, mídia, transcrição, credencial, dado pessoal ou caminho sensível.

## Controles implementados

- subprocessos com lista de argumentos e sem shell;
- allowlists de extensão, formato e modelo;
- limites de tamanho, escrita atômica e temporários isolados;
- origem fixa de modelo e hash local, com validação de ETag LFS quando presente;
- ausência de API, telemetria e credenciais;
- permissões mínimas na CI, lint, tipos, testes, auditoria e secret scanning;
- desinstalador limitado ao diretório padrão e preservação de transcrições.

## Ameaças restantes

Binários FFmpeg/CMake/compilador e modelos são cadeia de suprimentos externa.
Confira origem, assinatura/hash e licença. Arquivos de mídia podem explorar
falhas de codecs: mantenha FFmpeg atualizado, processe conteúdo não confiável
em ambiente restrito e não execute com privilégios administrativos.
