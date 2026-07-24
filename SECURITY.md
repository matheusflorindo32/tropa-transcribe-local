# Política de segurança

## Versões

A versão `0.3.1-alpha` está em desenvolvimento. Não é adequada, sem avaliação
institucional adicional, para fluxo pericial, clínico, sigiloso ou crítico.

## Relato responsável

Contato privado pendente: `[INSERIR E-MAIL INSTITUCIONAL]`. Não abra issue com
exploit, mídia, transcrição, credencial, dado pessoal ou caminho sensível.

## Controles implementados

- subprocessos com lista de argumentos e sem shell;
- allowlists de extensão, formato e modelo;
- limites de tamanho, escrita atômica e temporários isolados;
- manifesto incorporado com hash próprio, origens HTTPS fixas, tamanho e
  SHA-256 obrigatórios para runtimes e modelos;
- extração ZIP por allowlist, bloqueio de traversal/symlink, staging, promoção
  atômica, rollback e rejeição de DLL inesperada;
- ausência de API, telemetria e credenciais;
- permissões mínimas na CI, lint, tipos, testes, auditoria e secret scanning;
- desinstalador limitado ao diretório padrão e preservação de transcrições.

## Ameaças restantes

Binários FFmpeg/whisper.cpp e modelos continuam sendo cadeia de suprimentos
externa. O manifesto reduz, mas não elimina, comprometimento da origem ou da
build upstream. Confira origem, hash e licença. Arquivos de mídia podem explorar
falhas de codecs: mantenha FFmpeg atualizado, processe conteúdo não confiável
em ambiente restrito e não execute com privilégios administrativos.
