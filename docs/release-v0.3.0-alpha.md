# Preparação da release v0.3.0-alpha

Esta release está preparada em código, mas **não está autorizada para publicação
binária**.

## Critérios

- [x] GUI com fila, formatos, progresso, cancelamento, prévia e mensagens fail-fast.
- [x] Executável `onedir` e instalador Inno configurados.
- [x] SBOM CycloneDX, manifesto de componentes e geração de SHA-256.
- [x] Nenhum modelo, mídia, transcrição ou binário adicionado ao Git.
- [ ] Bundle construído e aberto sem Python em Windows limpo.
- [ ] Runtime FFmpeg/whisper.cpp provisionado sem dependência de Python/Git/CMake.
- [ ] Transcrição real pelo executável em Windows limpo.
- [ ] Defender, SmartScreen, atualização e desinstalação testados.
- [ ] Licenças da build concreta e arquivos LGPL correspondentes revisados.
- [ ] Authenticode e timestamp configurados.

Qualquer item pendente bloqueia a promoção para beta pública. Não anexar
artefatos a uma release ou ao Git antes da aprovação técnica, jurídica e de
segurança.
