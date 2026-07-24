# Segurança operacional

1. Baixe ferramentas de fontes oficiais e verifique assinatura/hash.
2. Mantenha sistema, Python e FFmpeg atualizados.
3. Não execute como administrador, salvo etapa explicitamente necessária.
4. Processe mídia desconhecida em conta/VM restrita.
5. Use volume criptografado e acesso mínimo para material sensível.
6. Desative sincronização em nuvem da pasta quando incompatível com a política.
7. Não anexe mídia ou transcrição a issues.
8. Exclua logs, temporários e saídas conforme retenção.

O código evita shell, valida allowlists e limita downloads. Isso não elimina
vulnerabilidades de codecs, cadeia de suprimentos, sistema ou acesso físico.
