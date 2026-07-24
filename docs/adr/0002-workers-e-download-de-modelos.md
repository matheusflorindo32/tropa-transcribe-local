# ADR 0002 — Workers e download de modelos

- Status: aceito
- Data: 2026-07-24

## Decisão

Transcrição e download rodam em `QThread`, com sinais para atualizar a GUI e
`threading.Event` para cancelamento cooperativo. A interface nunca espera o
processo pesado no event loop.

Modelos são gravados em arquivo temporário exclusivo, validados por tamanho e
SHA-256 quando o ETag LFS confiável está disponível, e promovidos por renomeação
atômica. Uma interrupção remove o parcial.

Retomada fica desabilitada até que origem e cliente validem conjuntamente
`Range`, `Content-Range`, ETag imutável e tamanho final. Concatenar bytes sem
essas garantias poderia produzir modelo silenciosamente corrompido.
