# Especificação — política de cache

## Identificação
- Chave: `url:<short_code>`
- Valor: URL original (string)
- TTL inicial: `15.552.000` segundos (180 dias)

## Fluxo de leitura
1. Consultar Redis.
2. Se houver valor: renovar TTL para 180 dias e responder 302 com `X-Cache: HIT`.
3. Se não houver: consultar SQLAlchemy pelo código.
4. Se não existir: responder 404.
5. Se existir: gravar no Redis com TTL de 180 dias e responder 302 com `X-Cache: MISS`.

## Invariante
A base SQL é a fonte persistente. A expiração do cache não apaga a URL cadastrada.
