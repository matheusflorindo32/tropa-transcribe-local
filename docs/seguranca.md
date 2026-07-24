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

Builds desktop devem gerar SBOM e SHA-256, manter Defender/SmartScreen ativos e
ser assinadas somente por identidade protegida fora do Git. Consulte
[`antivirus-e-assinatura.md`](antivirus-e-assinatura.md). Nunca trate uma
exceção de antivírus como etapa normal de instalação.
