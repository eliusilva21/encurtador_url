from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

# 1. Tabela de Categorias
class CategoriaModel(Base):
    __tablename__ = "categorias"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), unique=True, nullable=False)

    urls = relationship("URLModel", back_populates="categoria")

# 2. Tabela de URLs
class URLModel(Base):
    __tablename__ = "urls"

    id = Column(Integer, primary_key=True, index=True)
    original_url = Column(String(500), nullable=False)
    short_code = Column(String(10), unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    categoria_id = Column(Integer, ForeignKey("categorias.id"), nullable=True)

    categoria = relationship("CategoriaModel", back_populates="urls")
    cliques = relationship("CliqueModel", back_populates="url")

# 3. Tabela de Histórico de Cliques (Analytics)
class CliqueModel(Base):
    __tablename__ = "cliques"

    id = Column(Integer, primary_key=True, index=True)
    data_clique = Column(DateTime, default=datetime.utcnow)

    url_id = Column(Integer, ForeignKey("urls.id"), nullable=False)

    url = relationship("URLModel", back_populates="cliques")