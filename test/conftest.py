import os
import sys
import sqlite3
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Garante que a raiz do projeto esteja no sys.path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from app.main import app
from app.database import get_db
from app.auth import criar_token

# Caminho do banco test.db obrigatório
DB_TEST_PATH = os.path.join(ROOT_DIR, "banco test.db")

@pytest.fixture()
def db_session():
    """
    Carrega o banco de testes 'banco test.db' diretamente para a memória via backup.
    Dessa forma:
    - O banco principal 'banco.db' NUNCA é tocado.
    - O arquivo 'banco test.db' é utilizado como base fiel e permanece intacto em disco.
    - Cada teste é executado com isolamento total em memória de alta performance.
    """
    assert os.path.exists(DB_TEST_PATH), f"Arquivo de banco de testes não encontrado em {DB_TEST_PATH}"

    mem_conn = sqlite3.connect(":memory:", check_same_thread=False)
    disk_conn = sqlite3.connect(DB_TEST_PATH)
    disk_conn.backup(mem_conn)
    disk_conn.close()

    engine = create_engine(
        "sqlite://",
        creator=lambda: mem_conn,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSession()

    def override_get_db():
        try:
            yield session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    yield session

    session.close()
    mem_conn.close()
    app.dependency_overrides.pop(get_db, None)


@pytest.fixture()
def cliente(db_session):
    """Cliente HTTP de teste sem autenticação prévia."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture()
def cliente_admin(cliente):
    """Cliente HTTP com cookie de autenticação JWT de Administrador."""
    token = criar_token({
        "sub": "admin@aapm.com.br",
        "nome": "Admin AAPM",
        "role": "admin",
        "id": 1
    })
    cliente.cookies.set("access_token", token)
    return cliente


@pytest.fixture()
def cliente_operador(cliente):
    """Cliente HTTP com cookie de autenticação JWT de Operador."""
    token = criar_token({
        "sub": "joao@aapm.com",
        "nome": "Operador João",
        "role": "operador",
        "id": 2
    })
    cliente.cookies.set("access_token", token)
    return cliente