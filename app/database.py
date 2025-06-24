from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

# Configuração melhorada do engine com pool de conexões
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_size=20,  # Número de conexões no pool
    max_overflow=30,  # Conexões adicionais que podem ser criadas
    pool_pre_ping=True,  # Verifica se a conexão ainda está válida
    pool_recycle=3600,  # Recicla conexões a cada hora
    pool_timeout=30,  # Timeout para obter conexão do pool
    echo=False  # Set to True para debug SQL
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()