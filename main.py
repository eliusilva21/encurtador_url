from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
import string
import random

from database import engine, get_db, Base
from models import CategoriaModel, URLModel, CliqueModel

# Cria as tabelas se ainda não existirem no MySQL
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Encurtador de URLs com Categorias Relacionais")

# Libera o CORS para o seu HTML enviar requisições
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          
    allow_credentials=True,
    allow_methods=["*"],          
    allow_headers=["*"],          
)

# Schema para receber os dados
class URLCreate(BaseModel):
    url: str
    categoria: str = "geral"


def gerar_short_code(tamanho=6):
    caracteres = string.ascii_letters + string.digits
    return "".join(random.choice(caracteres) for _ in range(tamanho))


# ================= 1. ENCURTAR LINK E ASSOCIAR À CATEGORIA =================
@app.post("/encurtar")
def encurtar_url(dados: URLCreate, db: Session = Depends(get_db)):
    # Normaliza a categoria (converte para minúsculas e remove espaços extras nas pontas)
    categoria_input = dados.categoria.lower().strip()

    # Busca a categoria flexibilizando espaço ou underline (ex: "casa utilidades" ou "casa_utilidades")
    categoria_db = db.query(CategoriaModel).filter(
        (CategoriaModel.nome == categoria_input) | 
        (CategoriaModel.nome == categoria_input.replace("_", " ")) |
        (CategoriaModel.nome == categoria_input.replace(" ", "_"))
    ).first()
    
    # Se ainda assim não existir no banco, cria a nova categoria
    if not categoria_db:
        categoria_db = CategoriaModel(nome=categoria_input)
        db.add(categoria_db)
        db.commit()
        db.refresh(categoria_db)

    # Verifica se a URL original já existe no banco
    url_existente = db.query(URLModel).filter(URLModel.original_url == dados.url).first()
    
    if url_existente:
        # Se o link já existia mas sob outra categoria, atualiza para a nova se necessário
        url_existente.categoria_id = categoria_db.id
        db.commit()
        db.refresh(url_existente)
        
        return {
            "id": url_existente.id,
            "short_url": f"http://127.0.0.1:8000/{url_existente.short_code}",
            "categoria": {
                "id": categoria_db.id,
                "nome": categoria_db.nome
            },
            "status": "Link já existia e foi associado à categoria!"
        }

    # Gera short code e salva novo link
    short_code = gerar_short_code()
    while db.query(URLModel).filter(URLModel.short_code == short_code).first():
        short_code = gerar_short_code()

    nova_url = URLModel(
        original_url=dados.url,
        short_code=short_code,
        categoria_id=categoria_db.id 
    )
    db.add(nova_url)
    db.commit()
    db.refresh(nova_url)

    return {
        "id": nova_url.id,
        "short_url": f"http://127.0.0.1:8000/{nova_url.short_code}",
        "categoria": {
            "id": categoria_db.id,
            "nome": categoria_db.nome
        },
        "status": "Novo link criado com sucesso!"
    }


# ================= 2. REDIRECIONAR E REGISTRAR CLIQUE =================
@app.get("/{short_code}")
def redirecionar_url(short_code: str, db: Session = Depends(get_db)):
    url_db = db.query(URLModel).filter(URLModel.short_code == short_code).first()

    if not url_db:
        raise HTTPException(status_code=404, detail="Link não encontrado")

    # Registra o clique no MySQL
    novo_clique = CliqueModel(url_id=url_db.id)
    db.add(novo_clique)
    db.commit()
    db.refresh(novo_clique)

    # status_code=307 impede o navegador de guardar cache e força a contagem sempre
    return RedirectResponse(url=url_db.original_url, status_code=307)

# ================= 3. LISTAR TODAS AS CATEGORIAS =================
@app.get("/categorias/todas")
def listar_categorias_e_links(db: Session = Depends(get_db)):
    categorias = db.query(CategoriaModel).order_by(CategoriaModel.id.asc()).all()

    resultado = []
    for cat in categorias:
        links_da_categoria = db.query(URLModel).filter(URLModel.categoria_id == cat.id).order_by(URLModel.id.asc()).all()

        resultado.append({
            "categoria_id": cat.id,
            "categoria_nome": cat.nome,
            "total_links": len(links_da_categoria),
            "links": [
                {
                    "link_id": link.id,
                    "original_url": link.original_url,
                    "short_code": link.short_code,
                    "short_url": f"http://127.0.0.1:8000/{link.short_code}",
                    "total_cliques": len(link.cliques)
                } for link in links_da_categoria
            ]
        })

    return resultado