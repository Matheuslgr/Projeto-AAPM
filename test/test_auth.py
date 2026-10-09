import pytest
from app.models.usuarios import Usuario
from app.auth import hash_senha

def test_login_pagina_sucesso(cliente):
    """GET /auth/login - Exibe página de login com sucesso (200)."""
    resp = cliente.get("/auth/login")
    assert resp.status_code == 200
    assert "text/html" in resp.headers["content-type"]
    assert "login" in resp.text.lower() or "entrar" in resp.text.lower()


def test_login_credenciais_validas_sucesso(cliente):
    """POST /auth/login - Sucesso com credenciais válidas e geração de cookie JWT."""
    resp = cliente.post(
        "/auth/login",
        data={"email": "admin@aapm.com.br", "senha": "admin123"},
        follow_redirects=False
    )
    assert resp.status_code == 302
    assert resp.headers["location"] == "/"
    assert "access_token" in resp.cookies


def test_login_senha_incorreta_erro(cliente):
    """POST /auth/login - Erro quando a senha informada está incorreta."""
    resp = cliente.post(
        "/auth/login",
        data={"email": "admin@aapm.com.br", "senha": "senha_errada_123"},
        follow_redirects=False
    )
    assert resp.status_code == 200
    assert "E-mail ou senha incorretos" in resp.text
    assert "access_token" not in resp.cookies


def test_login_usuario_inexistente_erro(cliente):
    """POST /auth/login - Erro quando o e-mail não existe no sistema."""
    resp = cliente.post(
        "/auth/login",
        data={"email": "naoexiste@aapm.com.br", "senha": "qualquersenha"},
        follow_redirects=False
    )
    assert resp.status_code == 200
    assert "E-mail ou senha incorretos" in resp.text
    assert "access_token" not in resp.cookies


def test_login_usuario_inativo_erro(cliente, db_session):
    """POST /auth/login - Erro quando o usuário está inativo no banco."""
    # Cria ou inativa um usuário
    usuario_inativo = db_session.query(Usuario).filter(Usuario.email == "inativo@aapm.com.br").first()
    if not usuario_inativo:
        usuario_inativo = Usuario(
            nome="Usuário Inativo",
            email="inativo@aapm.com.br",
            senha_hash=hash_senha("senha123"),
            role="operador",
            ativo=False
        )
        db_session.add(usuario_inativo)
    else:
        usuario_inativo.senha_hash = hash_senha("senha123")
        usuario_inativo.ativo = False
    db_session.commit()

    resp = cliente.post(
        "/auth/login",
        data={"email": "inativo@aapm.com.br", "senha": "senha123"},
        follow_redirects=False
    )
    assert resp.status_code == 200
    assert "Usuário inativo" in resp.text


def test_login_dados_invalidos_sem_campos(cliente):
    """POST /auth/login - Dados inválidos: envio de campos vazios ou ausentes (422)."""
    resp = cliente.post(
        "/auth/login",
        data={},
        follow_redirects=False
    )
    assert resp.status_code == 422


def test_logout_sucesso(cliente_admin):
    """GET /auth/logout - Sucesso ao deslogar e limpar cookie."""
    resp = cliente_admin.get("/auth/logout", follow_redirects=False)
    assert resp.status_code == 302
    assert "/auth/login" in resp.headers["location"]


def test_switch_conta_sucesso(cliente_admin):
    """GET /auth/switch - Sucesso ao alternar conta e redirecionar para login."""
    resp = cliente_admin.get("/auth/switch", follow_redirects=False)
    assert resp.status_code == 302
    assert "/auth/login" in resp.headers["location"]


def test_acesso_com_token_falso_erro(cliente):
    """Erro 401 ao enviar um cookie JWT corrompido / forjado."""
    cliente.cookies.set("access_token", "token.falso.invalido")
    resp = cliente.get("/usuarios/", follow_redirects=False)
    assert resp.status_code == 401
