import pytest
from app.models.usuarios import Usuario

def test_listar_usuarios_sucesso(cliente_admin):
    """GET /usuarios/ - Sucesso ao listar usuários para admin."""
    resp = cliente_admin.get("/usuarios/")
    assert resp.status_code == 200
    assert "text/html" in resp.headers["content-type"]
    assert "admin@aapm.com.br" in resp.text


def test_listar_usuarios_busca_sucesso(cliente_admin):
    """GET /usuarios/ - Sucesso na busca de usuário por nome ou email."""
    resp = cliente_admin.get("/usuarios/?busca=joao")
    assert resp.status_code == 200
    assert "joao@aapm.com" in resp.text


def test_listar_usuarios_filtro_role(cliente_admin):
    """GET /usuarios/ - Sucesso ao filtrar usuários por role."""
    resp = cliente_admin.get("/usuarios/?role=operador")
    assert resp.status_code == 200
    assert "joao@aapm.com" in resp.text


def test_listar_usuarios_nao_autenticado_erro(cliente):
    """GET /usuarios/ - Erro 401 para usuário anônimo."""
    resp = cliente.get("/usuarios/", follow_redirects=False)
    assert resp.status_code == 401


def test_listar_usuarios_operador_proibido_erro(cliente_operador):
    """GET /usuarios/ - Erro 403 para operador sem privilégio admin."""
    resp = cliente_operador.get("/usuarios/", follow_redirects=False)
    assert resp.status_code == 403


def test_form_novo_usuario_sucesso(cliente_admin):
    """GET /usuarios/novo - Sucesso ao exibir tela de cadastro de usuário."""
    resp = cliente_admin.get("/usuarios/novo")
    assert resp.status_code == 200
    assert "form" in resp.text.lower()


def test_criar_usuario_sucesso(cliente_admin, db_session):
    """POST /usuarios/novo - Sucesso ao cadastrar novo usuário válido."""
    payload = {
        "nome": "Novo Operador Teste",
        "email": "novoteste@aapm.com.br",
        "senha": "senhaSegura123",
        "role": "operador"
    }
    resp = cliente_admin.post("/usuarios/novo", data=payload, follow_redirects=False)
    assert resp.status_code == 302
    assert "/usuarios?criado=ok" in resp.headers["location"]

    user = db_session.query(Usuario).filter_by(email="novoteste@aapm.com.br").first()
    assert user is not None
    assert user.nome == "Novo Operador Teste"
    assert user.role == "operador"
    assert user.ativo is True


def test_criar_usuario_email_duplicado_erro(cliente_admin):
    """POST /usuarios/novo - Erro 400 ao cadastrar usuário com email já existente."""
    payload = {
        "nome": "Duplicado Teste",
        "email": "admin@aapm.com.br",
        "senha": "qualquersenha",
        "role": "admin"
    }
    resp = cliente_admin.post("/usuarios/novo", data=payload, follow_redirects=False)
    assert resp.status_code == 400
    assert "Este e-mail já está cadastrado" in resp.text


def test_criar_usuario_role_invalido_erro(cliente_admin):
    """POST /usuarios/novo - Erro 400 ao tentar cadastrar usuário com perfil inválido."""
    payload = {
        "nome": "Perfil Invalido",
        "email": "hacker@aapm.com.br",
        "senha": "123",
        "role": "superadmin_invalido"
    }
    resp = cliente_admin.post("/usuarios/novo", data=payload, follow_redirects=False)
    assert resp.status_code == 400
    assert "Perfil de acesso inválido" in resp.text


def test_form_editar_usuario_sucesso(cliente_admin):
    """GET /usuarios/{id}/editar - Sucesso ao abrir formulário de edição de usuário."""
    resp = cliente_admin.get("/usuarios/2/editar")
    assert resp.status_code == 200
    assert "joao@aapm.com" in resp.text


def test_form_editar_usuario_inexistente(cliente_admin):
    """GET /usuarios/{id}/editar - Redireciona quando usuário não existe."""
    resp = cliente_admin.get("/usuarios/99999/editar", follow_redirects=False)
    assert resp.status_code == 302
    assert resp.headers["location"] == "/usuarios"


def test_editar_usuario_sucesso(cliente_admin, db_session):
    """POST /usuarios/{id}/editar - Sucesso ao atualizar dados do usuário."""
    payload = {
        "nome": "João Silva Atualizado",
        "email": "joao.atualizado@aapm.com",
        "role": "operador",
        "senha": ""  # sem alterar senha
    }
    resp = cliente_admin.post("/usuarios/2/editar", data=payload, follow_redirects=False)
    assert resp.status_code == 302
    assert "/usuarios?editado=ok" in resp.headers["location"]

    user = db_session.query(Usuario).filter_by(id=2).first()
    assert user.nome == "João Silva Atualizado"
    assert user.email == "joao.atualizado@aapm.com"


def test_editar_usuario_email_conflito_erro(cliente_admin):
    """POST /usuarios/{id}/editar - Erro 400 ao colocar email já pertencente a outro usuário."""
    payload = {
        "nome": "João Conflito",
        "email": "admin@aapm.com.br",  # Já é do id 1
        "role": "operador",
        "senha": ""
    }
    resp = cliente_admin.post("/usuarios/2/editar", data=payload, follow_redirects=False)
    assert resp.status_code == 400
    assert "Este e-mail já está em uso por outro usuário" in resp.text


def test_toggle_ativo_outro_usuario(cliente_admin, db_session):
    """POST /usuarios/{id}/toggle-ativo - Alterna status de outro usuário com sucesso."""
    user = db_session.query(Usuario).filter_by(id=2).first()
    status_inicial = user.ativo

    resp = cliente_admin.post("/usuarios/2/toggle-ativo", follow_redirects=False)
    assert resp.status_code == 302
    assert resp.headers["location"] == "/usuarios"

    user_atualizado = db_session.query(Usuario).filter_by(id=2).first()
    assert user_atualizado.ativo != status_inicial


def test_toggle_ativo_auto_proprio_bloqueado(cliente_admin):
    """POST /usuarios/{id}/toggle-ativo - Proteção impede que o admin desative a si próprio."""
    resp = cliente_admin.post("/usuarios/1/toggle-ativo", follow_redirects=False)
    assert resp.status_code == 302
    assert "erro=autoproprio" in resp.headers["location"]


def test_excluir_usuario_sucesso(cliente_admin, db_session):
    """POST /usuarios/{id}/excluir - Sucesso ao excluir outro usuário."""
    resp = cliente_admin.post("/usuarios/3/excluir", follow_redirects=False)
    assert resp.status_code == 302
    assert "/usuarios?excluido=ok" in resp.headers["location"]

    user = db_session.query(Usuario).filter_by(id=3).first()
    assert user is None


def test_excluir_usuario_auto_proprio_bloqueado(cliente_admin):
    """POST /usuarios/{id}/excluir - Proteção impede que o admin exclua a si mesmo."""
    resp = cliente_admin.post("/usuarios/1/excluir", follow_redirects=False)
    assert resp.status_code == 302
    assert "erro=autoproprio_excluir" in resp.headers["location"]
