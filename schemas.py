# Validação de Entrada/Saída

from pydantic import BaseModel, HttpUrl

# Garante que o texto enviado seja uma URL válida (ex: https://site.com)
class URLCreate(BaseModel):
    url: HttpUrl  

# O link encurtado completo (ex: http://127.0.0.1:8000/a8X9k2)
class URLResponse(BaseModel):
    original_url: str
    short_code: str
    short_url: str  

    class Config:
        from_attributes = True