#  Conectar Python ao SQlite e gerenciar sessões

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Trocando localhost por 127.0.0.1 força a conexão via IPv4
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:@127.0.0.1:3306/encurtador_db"

# Cria o "motor" que se conecta ao arquivo do banco
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, )

# Cria a fábrica de sessões (para abrir e fechar conexões)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para criar os modelos/tabelas
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()