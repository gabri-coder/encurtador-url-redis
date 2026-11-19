# ADR 002 — Utilizar HTTP 302

- Status: Aceita
- Contexto: o código curto é permanente, mas a resolução do destino é feita dinamicamente no servidor.
- Decisão: responder com 302 Found.
- Consequências: navegadores e intermediários não devem tratar o destino como redirecionamento permanente, preservando flexibilidade futura.
