from pydantic import BaseModel, EmailStr, HttpUrl, ConfigDict

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class URLCreate(BaseModel):
    original_url: HttpUrl

class URLRead(BaseModel):
    id: int
    short_code: str
    original_url: str
    short_url: str
    model_config = ConfigDict(from_attributes=True)
