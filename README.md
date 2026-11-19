# Encurtador de URL com Cache Redis

Projeto acadêmico — Programação Avançada. Backend FastAPI, frontend React, SQLAlchemy e Redis.

## Requisitos
- Python 3.12+
- Node.js 20+
- Docker e Docker Compose (recomendado)
- Git

## Executar com Docker (Mac, Linux e Windows)
1. Clone o repositório.
2. Na raiz, crie `.env` (opcional) e defina `SECRET_KEY` com uma chave longa e aleatória.
3. Execute `docker compose up --build`.
4. Acesse o frontend em http://localhost:5173 e a documentação da API em http://localhost:8000/docs.
5. Para encerrar: `docker compose down`. Para apagar também os dados persistidos: `docker compose down -v`.

## Executar sem Docker

### Backend
Mac/Linux:
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
# Redis deve estar em execução em localhost:6379
uvicorn app.main:app --reload
```
Windows PowerShell:
```powershell
cd backend
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```
O banco SQLite é criado automaticamente em `backend/encurtador.db`. Para usar outro banco, configure `DATABASE_URL`.

### Frontend
Em outro terminal:
```bash
cd frontend
npm install
npm run dev
```
Acesse http://localhost:5173.

## Testes
Com o ambiente virtual ativo e dentro de `backend`:
```bash
pytest -q
```
Os testes verificam a duração do TTL, a renovação no cache hit e a convenção da chave Redis.

## Demonstração do cache
1. Faça cadastro e login; crie uma URL.
2. Acesse `http://localhost:8000/r/CODIGO` uma vez. A resposta de redirecionamento inclui `X-Cache: MISS`: o backend consultou o banco e gravou no Redis.
3. Acesse a mesma URL novamente. A resposta inclui `X-Cache: HIT`: o Redis respondeu sem SELECT no banco.
4. Consulte o TTL:
```bash
docker compose exec redis redis-cli TTL url:CODIGO
```
O TTL começa em 15.552.000 segundos (180 dias) e é renovado a cada acesso pelo cache.
5. Para simular expiração sem esperar seis meses:
```bash
docker compose exec redis redis-cli EXPIRE url:CODIGO 5
docker compose exec redis redis-cli TTL url:CODIGO
```
Espere cinco segundos e consulte o TTL novamente. Ao acessar o link depois da expiração, haverá MISS e a chave será recriada.

## Pergunta central — resposta
O sistema mantém no Redis o mapeamento `url:<codigo> -> URL original` com TTL de 15.552.000 segundos. Em um cache hit, renova o TTL e redireciona sem consultar o banco. Se a chave expirou após 180 dias sem acessos, o próximo acesso causa cache miss: o backend consulta o banco, recria a chave e redireciona. Redis é cache, não fonte definitiva dos dados; por isso a URL permanece no banco.

## Decisões importantes
- **302 em vez de 301:** o destino é resolvido dinamicamente; 302 evita cache permanente do redirecionamento por navegadores e intermediários.
- **TTL deslizante:** cada acesso renova os 180 dias, de modo que links ativos permaneçam no cache.
- **Fallback:** se Redis estiver indisponível, o backend tenta o banco; o serviço continua funcional, embora sem aceleração.
- **Isolamento:** cada usuário lista apenas os links associados ao próprio `user_id`.
- **Autenticação:** JWT e senha armazenada com hash Argon2.

## Limitações e próximos passos
Esta é uma base acadêmica funcional. Antes de produção, adicionar migrações Alembic, rate limiting, validação contra URLs internas/SSRF, logs estruturados, gestão de segredos e testes de integração com Redis e banco real.
