# ADR 001 — Redis como cache de redirecionamento

- Status: Aceita
- Contexto: redirecionar links frequentemente usados sem consultar o banco em todos os acessos.
- Decisão: guardar `url:<short_code> -> original_url` no Redis com TTL deslizante de 180 dias.
- Consequências: cache hit não acessa SQL; cache miss consulta a fonte persistente e repopula o cache. Redis pode ser descartado sem perda dos registros.
