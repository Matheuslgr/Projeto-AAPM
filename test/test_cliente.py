import pytest
from app.models.cliente import Cliente

def test_listar_clientes_sucesso(cliente_admin):
    """GET /clientes/ - Sucesso ao listar clientes para admin."""
    resp = cliente_admin.get("/clientes/")
    assert resp.status_code == 200
    assert "Maria Alice" in resp.text
    assert "Lucas" in resp.text


def test_listar_clientes_filtros_sucesso(cliente_admin):
    """GET /clientes/ - Sucesso com busca e filtro de associados."""
    # Apenas associados
    resp = cliente_admin.get("/clientes/?apenas_associados=true")
    assert resp.status_code == 200
    assert "Maria Alice" in resp.text

    # Busca por matrícula
    resp_busca = cliente_admin.get("/clientes/?busca=1241")
    assert resp_busca.status_code == 200
    assert "Lucas" in resp_busca.text


def test_listar_clientes_operador_proibido_erro(cliente_operador):
    """GET /clientes/ - Erro 403 para usuário operador sem permissão de admin."""
    resp = cliente_operador.get("/clientes/", follow_redirects=False)
    assert resp.status_code == 403


def test_listar_clientes_nao_autenticado_erro(cliente):
    """GET /clientes/ - Erro 401 para requisição sem autenticação."""
    resp = cliente.get("/clientes/", follow_redirects=False)
    assert resp.status_code == 401


def test_form_novo_cliente_sucesso(cliente_admin):
    """GET /clientes/novo - Sucesso ao abrir formulário de cadastro de cliente."""
    resp = cliente_admin.get("/clientes/novo")
    assert resp.status_code == 200
    assert "form" in resp.text.lower()


def test_criar_cliente_sucesso(cliente_admin, db_session):
    """POST /clientes/novo - Sucesso na criação de novo cliente associado."""
    payload = {
        "nome": "Fernanda Estudante",
        "matricula": "998877",
        "telefone": "11988887777",
        "is_associado": True
    }
    resp = cliente_admin.post("/clientes/novo", data=payload, follow_redirects=False)
    assert resp.status_code == 302
    assert "/clientes?criado=ok" in resp.headers["location"]

    cli = db_session.query(Cliente).filter_by(matricula="998877").first()
    assert cli is not None
    assert cli.nome == "Fernanda Estudante"
    assert cli.is_associado is True


def test_criar_cliente_matricula_duplicada_erro(cliente_admin):
    """POST /clientes/novo - Erro 400 ao tentar cadastrar cliente com matrícula já existente."""
    payload = {
        "nome": "Aluno Conflitante",
        "matricula": "3431",  # Já pertence à Maria Alice
        "telefone": "11999990000",
        "is_associado": False
    }
    resp = cliente_admin.post("/clientes/novo", data=payload, follow_redirects=False)
    assert resp.status_code == 400
    assert "já cadastrada" in resp.text


def test_criar_cliente_dados_invalidos_sem_campos(cliente_admin):
    """POST /clientes/novo - Dados inválidos: falta do campo obrigatório nome (422)."""
    resp = cliente_admin.post("/clientes/novo", data={}, follow_redirects=False)
    assert resp.status_code == 422


def test_form_editar_cliente_sucesso(cliente_admin):
    """GET /clientes/{id}/editar - Sucesso ao carregar tela de edição de cliente."""
    resp = cliente_admin.get("/clientes/1/editar")
    assert resp.status_code == 200
    assert "Maria Alice" in resp.text


def test_form_editar_cliente_inexistente_erro(cliente_admin):
    """GET /clientes/{id}/editar - Redirecionamento 302 para cliente inexistente."""
    resp = cliente_admin.get("/clientes/99999/editar", follow_redirects=False)
    assert resp.status_code == 302
    assert resp.headers["location"] == "/clientes"


def test_editar_cliente_sucesso(cliente_admin, db_session):
    """POST /clientes/{id}/editar - Sucesso ao atualizar informações do cliente."""
    payload = {
        "nome": "Lucas Silva Atualizado",
        "matricula": "1241-ATUALIZADA",
        "telefone": "11977776666",
        "is_associado": True
    }
    resp = cliente_admin.post("/clientes/2/editar", data=payload, follow_redirects=False)
    assert resp.status_code == 302
    assert "/clientes?editado=ok" in resp.headers["location"]

    editado = db_session.query(Cliente).filter_by(id=2).first()
    assert editado.nome == "Lucas Silva Atualizado"
    assert editado.matricula == "1241-ATUALIZADA"
    assert editado.is_associado is True


def test_editar_cliente_matricula_conflito_erro(cliente_admin):
    """POST /clientes/{id}/editar - Redirecionamento com erro de matrícula duplicada."""
    payload = {
        "nome": "Lucas Silva",
        "matricula": "3431",  # Já pertence à Maria Alice (ID 1)
        "telefone": "",
        "is_associado": False
    }
    resp = cliente_admin.post("/clientes/2/editar", data=payload, follow_redirects=False)
    assert resp.status_code == 302
    assert "erro=matricula" in resp.headers["location"]


def test_toggle_ativo_cliente_sucesso(cliente_admin, db_session):
    """POST /clientes/{id}/toggle-ativo - Sucesso ao desativar cliente."""
    resp = cliente_admin.post("/clientes/1/toggle-ativo", follow_redirects=False)
    assert resp.status_code == 302
    assert resp.headers["location"] == "/clientes"

    cli = db_session.query(Cliente).filter_by(id=1).first()
    assert cli.ativo is False
