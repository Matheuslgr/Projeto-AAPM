import pytest
from app.models.armario import Armario

def test_listar_armarios_sucesso(cliente_admin):
    """GET /armarios/ - Sucesso ao exibir tela de gerenciamento de armários."""
    resp = cliente_admin.get("/armarios/")
    assert resp.status_code == 200
    assert "text/html" in resp.headers["content-type"]
    assert "005" in resp.text


def test_api_listar_armarios_sucesso(cliente_admin):
    """GET /armarios/api/listar - Sucesso na API JSON de listagem e filtros."""
    resp = cliente_admin.get("/armarios/api/listar?filtro=disponiveis&q=005")
    assert resp.status_code == 200
    data = resp.json()
    assert data["sucesso"] is True
    assert "stats" in data
    assert len(data["armarios"]) >= 1


def test_obter_armario_sucesso(cliente_admin):
    """GET /armarios/{id} - Sucesso ao obter detalhes de um armário existente."""
    resp = cliente_admin.get("/armarios/5")
    assert resp.status_code == 200
    data = resp.json()
    assert data["sucesso"] is True
    assert data["armario"]["numero"] == "005"


def test_obter_armario_inexistente_erro(cliente_admin):
    """GET /armarios/{id} - Erro 404 quando o armário não existe."""
    resp = cliente_admin.get("/armarios/99999")
    assert resp.status_code == 404


def test_criar_armario_sucesso(cliente_admin, db_session):
    """POST /armarios/novo - Sucesso ao cadastrar um novo armário com bloco válido."""
    payload = {"numero": "888", "localizacao": "Bloco B"}
    headers = {"Accept": "application/json", "X-Requested-With": "XMLHttpRequest"}
    resp = cliente_admin.post("/armarios/novo", data=payload, headers=headers)
    assert resp.status_code == 200
    assert resp.json()["sucesso"] is True

    arm = db_session.query(Armario).filter_by(numero="888").first()
    assert arm is not None
    assert arm.localizacao == "Bloco B"
    assert arm.status == "Livre"


def test_criar_armario_bloco_invalido_erro(cliente_admin):
    """POST /armarios/novo - Dados inválidos: localização fora dos blocos permitidos (400)."""
    payload = {"numero": "889", "localizacao": "Bloco Z"}
    resp = cliente_admin.post("/armarios/novo", data=payload)
    assert resp.status_code == 400
    assert "Selecione uma localização válida" in resp.text


def test_criar_armario_duplicado_erro(cliente_admin):
    """POST /armarios/novo - Erro 400 ao tentar cadastrar armário com número já existente."""
    payload = {"numero": "005", "localizacao": "Bloco A"}
    resp = cliente_admin.post("/armarios/novo", data=payload)
    assert resp.status_code == 400
    assert "já está cadastrado" in resp.text


def test_reservar_armario_sucesso(cliente_admin, db_session):
    """POST /armarios/{id}/reservar - Sucesso ao reservar armário livre."""
    payload = {
        "aluno_nome": "Estudante Teste",
        "turma": "Desenvolvimento 2026",
        "contato": "11988889999",
        "data_inicio": "2026-03-01",
        "data_termino": "2026-12-15",
        "observacoes": "Reserva anual"
    }
    headers = {"Accept": "application/json", "X-Requested-With": "XMLHttpRequest"}
    resp = cliente_admin.post("/armarios/5/reservar", data=payload, headers=headers)
    assert resp.status_code == 200
    assert resp.json()["sucesso"] is True

    arm = db_session.query(Armario).filter_by(id=5).first()
    assert arm.status == "Ocupado"
    assert arm.aluno_nome == "Estudante Teste"


def test_reservar_armario_datas_invalidas_erro(cliente_admin):
    """POST /armarios/{id}/reservar - Dados inválidos: data término anterior à data de início (400)."""
    payload = {
        "aluno_nome": "Estudante Invertido",
        "data_inicio": "2026-10-10",
        "data_termino": "2026-10-01",
    }
    headers = {"Accept": "application/json", "X-Requested-With": "XMLHttpRequest"}
    resp = cliente_admin.post("/armarios/5/reservar", data=payload, headers=headers)
    assert resp.status_code == 400
    assert "anterior à data de início" in resp.text


def test_reservar_armario_inexistente_erro(cliente_admin):
    """POST /armarios/{id}/reservar - Erro 404 para armário inexistente."""
    payload = {
        "aluno_nome": "Teste",
        "data_inicio": "2026-01-01",
        "data_termino": "2026-02-01",
    }
    resp = cliente_admin.post("/armarios/99999/reservar", data=payload)
    assert resp.status_code == 404


def test_liberar_armario_sucesso(cliente_admin, db_session):
    """POST /armarios/{id}/liberar - Sucesso ao liberar armário reservado."""
    arm = db_session.query(Armario).filter_by(id=5).first()
    arm.status = "Ocupado"
    arm.aluno_nome = "Aluno Anterior"
    db_session.commit()

    headers = {"Accept": "application/json", "X-Requested-With": "XMLHttpRequest"}
    resp = cliente_admin.post("/armarios/5/liberar", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["sucesso"] is True

    db_session.refresh(arm)
    assert arm.status == "Livre"
    assert arm.aluno_nome is None


def test_liberar_armario_inexistente_erro(cliente_admin):
    """POST /armarios/{id}/liberar - Erro 404 ao tentar liberar armário inexistente."""
    resp = cliente_admin.post("/armarios/99999/liberar")
    assert resp.status_code == 404


def test_excluir_armario_sucesso(cliente_admin, db_session):
    """POST /armarios/{id}/excluir - Sucesso ao excluir armário do sistema."""
    headers = {"Accept": "application/json", "X-Requested-With": "XMLHttpRequest"}
    resp = cliente_admin.post("/armarios/6/excluir", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["sucesso"] is True

    excluido = db_session.query(Armario).filter_by(id=6).first()
    assert excluido is None


def test_excluir_armario_inexistente_erro(cliente_admin):
    """POST /armarios/{id}/excluir - Erro 404 para exclusão de armário inexistente."""
    resp = cliente_admin.post("/armarios/99999/excluir")
    assert resp.status_code == 404


def test_armarios_operador_proibido_erro(cliente_operador):
    """GET /armarios/ - Erro 403 para operador."""
    resp = cliente_operador.get("/armarios/", follow_redirects=False)
    assert resp.status_code == 403


def test_armarios_nao_autenticado_erro(cliente):
    """GET /armarios/ - Erro 401 para usuário anônimo."""
    resp = cliente.get("/armarios/", follow_redirects=False)
    assert resp.status_code == 401
