import secrets
import string
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.orm import Session
import jwt
from .database import Base, engine, get_db
from .models import User, ShortURL
from .schemas import UserCreate, UserLogin, Token, URLCreate
from .security import hash_password, verify_password, create_access_token, decode_access_token
from . import cache

Base.metadata.create_all(bind=engine)
app = FastAPI(title="Encurtador de URL com Redis", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        email = decode_access_token(token)
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado.")
    user = db.scalar(select(User).where(User.email == email))
    if not user:
        raise HTTPException(status_code=401, detail="Usuário não encontrado.")
    return user

def make_code(length: int = 7) -> str:
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/auth/register", status_code=status.HTTP_201_CREATED)
def register(data: UserCreate, db: Session = Depends(get_db)):
    if len(data.password) < 8:
        raise HTTPException(status_code=422, detail="A senha deve ter pelo menos 8 caracteres.")
    if db.scalar(select(User).where(User.email == data.email)):
        raise HTTPException(status_code=409, detail="Este e-mail já está cadastrado.")
    user = User(email=data.email, password_hash=hash_password(data.password))
    db.add(user)
    db.commit()
    return {"message": "Usuário cadastrado com sucesso."}

@app.post("/auth/login", response_model=Token)
def login(data: UserLogin, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == data.email))
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="E-mail ou senha incorretos.")
    return Token(access_token=create_access_token(user.email))

@app.post("/urls", status_code=status.HTTP_201_CREATED)
def create_url(data: URLCreate, user: User = Depends(current_user), db: Session = Depends(get_db)):
    for _ in range(5):
        code = make_code()
        if not db.scalar(select(ShortURL).where(ShortURL.short_code == code)):
            break
    else:
        raise HTTPException(status_code=503, detail="Não foi possível gerar um código único.")
    item = ShortURL(short_code=code, original_url=str(data.original_url), user_id=user.id)
    db.add(item)
    db.commit()
    db.refresh(item)
    return {"id": item.id, "short_code": code, "original_url": item.original_url,
            "short_url": f"http://localhost:8000/r/{code}"}

@app.get("/urls")
def list_urls(user: User = Depends(current_user), db: Session = Depends(get_db)):
    rows = db.scalars(select(ShortURL).where(ShortURL.user_id == user.id).order_by(ShortURL.id.desc())).all()
    return [{"id": x.id, "short_code": x.short_code, "original_url": x.original_url,
             "short_url": f"http://localhost:8000/r/{x.short_code}"} for x in rows]

@app.get("/r/{short_code}")
def redirect_short_url(short_code: str, db: Session = Depends(get_db)):
    # Caminho rápido: cache hit não executa SELECT no banco.
    try:
        cached = cache.get_cached_url(short_code)
    except Exception:
        cached = None  # Redis indisponível: fallback seguro para o banco.
    if cached:
        return RedirectResponse(url=cached, status_code=302, headers={"X-Cache": "HIT"})

    item = db.scalar(select(ShortURL).where(ShortURL.short_code == short_code))
    if not item:
        raise HTTPException(status_code=404, detail="URL curta não encontrada.")
    try:
        cache.cache_url(short_code, item.original_url)
    except Exception:
        pass  # A aplicação continua funcionando sem cache.
    return RedirectResponse(url=item.original_url, status_code=302, headers={"X-Cache": "MISS"})
