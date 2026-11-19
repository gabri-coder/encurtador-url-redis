# Arquitetura

- `frontend/`: interface React para cadastro, login e gestão de URLs.
- `backend/app/main.py`: rotas HTTP e orquestração.
- `backend/app/models.py`: entidades User e ShortURL.
- `backend/app/security.py`: hash Argon2 e JWT.
- `backend/app/cache.py`: acesso Redis e política TTL.
- `backend/app/database.py`: engine e sessões SQLAlchemy.
- `backend/tests/`: testes da regra de cache.

O endpoint público `GET /r/{short_code}` não exige autenticação, pois é o destino dos links compartilhados. Endpoints de criação e listagem exigem JWT.
