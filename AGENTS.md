# Regras para agentes e colaboradores

## Stack e organização
- Backend: Python 3.12, FastAPI, SQLAlchemy 2.
- Cache: Redis; a chave de redirecionamento é `url:<short_code>`.
- Frontend: React + Vite.
- Mantenha backend e frontend separados.
- Não introduza outra tecnologia obrigatória sem decisão documentada.

## Regras de negócio
- Cada URL curta pertence a exatamente um usuário.
- Usuários só podem listar seus próprios links.
- Senhas nunca podem ser armazenadas em texto puro.
- A expiração do cache é deslizante: 180 dias desde o último acesso.
- Cache hit deve redirecionar sem executar consulta SQL.
- Cache miss consulta o banco e repovoa o Redis.
- Redis indisponível não deve impedir o redirecionamento se o banco estiver disponível.
- Redirecionamento HTTP deve ser 302.

## Qualidade
- Regras centrais devem ter testes automatizados com pytest.
- Não registrar tokens ou senhas em logs.
- Validar entradas com Pydantic.
- Documentar decisões arquiteturais em `docs/`.
- Atualizar README quando comandos ou variáveis de ambiente mudarem.
