import pytest
from app.models.categoria import Categoria

def test_listar_categorias_sucesso(cliente_admin):
    """GET /categorias/ - Sucesso na listagem de categorias para admin."""
    resp = cliente_admin.get("/categorias/")
    assert resp.status_code == 200
    assert "text/html" in resp.headers["content-type"]
    assert "Escrita e Correção" in resp.text or "Escrita" in resp.text


def test_listar_categorias_busca_sucesso(cliente_admin):
    """GET /categorias/ - Sucesso com busca por termo."""
    resp = cliente_admin.get("/categorias/?busca=Papéis")
    assert resp.status_code == 200
    assert "Papéis" in resp.text


def test_listar_categorias_nao_autenticado_erro(cliente):
    """GET /categorias/ - Erro 401 para usuário anônimo."""
    resp = cliente.get("/categorias/", follow_redirects=False)
    assert resp.status_code == 401


def test_listar_categorias_operador_proibido_erro(cliente_operador):
    """GET /categorias/ - Erro 403 para usuário operador sem perfil admin."""
    resp = cliente_operador.get("/categorias/", follow_redirects=False)
    assert resp.status_code == 403


def test_form_nova_categoria_sucesso(cliente_admin):
    """GET /categorias/nova - Sucesso ao exibir tela de cadastro de categoria."""
    resp = cliente_admin.get("/categorias/nova")
    assert resp.status_code == 200
    assert "form" in resp.text.lower()


def test_criar_categoria_sucesso(cliente_admin, db_session):
    """POST /categorias/nova - Sucesso ao criar categoria válida."""
    payload = {"nome": "Categoria Inovadora 2026"}
    resp = cliente_admin.post("/categorias/nova", data=payload, follow_redirects=False)
    assert resp.status_code == 302
    assert "/categorias?criado=ok" in resp.headers["location"]

    cat = db_session.query(Categoria).filter_by(nome="Categoria Inovadora 2026").first()
    assert cat is not None
    assert cat.ativo is True


def test_criar_categoria_duplicada_erro(cliente_admin):
    """POST /categorias/nova - Erro 400 ao tentar criar categoria com nome repetido."""
    payload = {"nome": "Escrita e Correção"}
    resp = cliente_admin.post("/categorias/nova", data=payload, follow_redirects=False)
    assert resp.status_code == 400
    assert "Já existe uma categoria com este nome" in resp.text


def test_criar_categoria_dados_invalidos_sem_campos(cliente_admin):
    """POST /categorias/nova - Dados inválidos: envio de formulário vazio (422)."""
    resp = cliente_admin.post("/categorias/nova", data={}, follow_redirects=False)
    assert resp.status_code == 422


def test_form_editar_categoria_sucesso(cliente_admin):
    """GET /categorias/{id}/editar - Sucesso ao abrir tela de edição de categoria existente."""
    resp = cliente_admin.get("/categorias/1/editar")
    assert resp.status_code == 200
    assert "form" in resp.text.lower()


def test_form_editar_categoria_inexistente_erro(cliente_admin):
    """GET /categorias/{id}/editar - Redirecionamento 302 para ID inexistente."""
    resp = cliente_admin.get("/categorias/99999/editar", follow_redirects=False)
    assert resp.status_code == 302
    assert resp.headers["location"] == "/categorias"


def test_editar_categoria_sucesso(cliente_admin, db_session):
    """POST /categorias/{id}/editar - Sucesso ao atualizar nome da categoria."""
    payload = {"nome": "Serviços Gráficos e Cópias"}
    resp = cliente_admin.post("/categorias/1/editar", data=payload, follow_redirects=False)
    assert resp.status_code == 302
    assert "/categorias?editado=ok" in resp.headers["location"]

    editada = db_session.query(Categoria).filter_by(id=1).first()
    assert editada.nome == "Serviços Gráficos e Cópias"


def test_editar_categoria_nome_duplicado_erro(cliente_admin):
    """POST /categorias/{id}/editar - Erro 400 ao renomear para nome já pertencente a outra categoria."""
    payload = {"nome": "Escrita e Correção"}  # Já é o nome da categoria 2
    resp = cliente_admin.post("/categorias/1/editar", data=payload, follow_redirects=False)
    assert resp.status_code == 400
    assert "Já existe outra categoria com este nome" in resp.text


def test_editar_categoria_inexistente_erro(cliente_admin):
    """POST /categorias/{id}/editar - Redirecionamento quando a categoria não existe."""
    resp = cliente_admin.post("/categorias/99999/editar", data={"nome": "Nao Existe"}, follow_redirects=False)
    assert resp.status_code == 302
    assert resp.headers["location"] == "/categorias"


def test_toggle_ativo_categoria_sucesso(cliente_admin, db_session):
    """POST /categorias/{id}/toggle-ativo - Sucesso ao desativar e reativar categoria."""
    # Desativa
    resp = cliente_admin.post("/categorias/1/toggle-ativo", follow_redirects=False)
    assert resp.status_code == 302
    assert "desativado=ok" in resp.headers["location"]

    cat = db_session.query(Categoria).filter_by(id=1).first()
    assert cat.ativo is False

    # Reativa
    resp2 = cliente_admin.post("/categorias/1/toggle-ativo", follow_redirects=False)
    assert resp2.status_code == 302
    assert "ativado=ok" in resp2.headers["location"]

    db_session.refresh(cat)
    assert cat.ativo is True


def test_excluir_categoria_com_produtos_vinculados_erro(cliente_admin):
    """POST /categorias/{id}/excluir - Bloqueio de regra de negócio ao tentar excluir categoria com produtos ativos."""
    resp = cliente_admin.post("/categorias/2/excluir", follow_redirects=False)
    assert resp.status_code == 302
    assert "erro=produtos_vinculados" in resp.headers["location"]


def test_excluir_categoria_sem_produtos_sucesso(cliente_admin, db_session):
    """POST /categorias/{id}/excluir - Sucesso ao excluir categoria vazia (sem produtos)."""
    nova_cat = Categoria(nome="Categoria Descartavel")
    db_session.add(nova_cat)
    db_session.commit()
    cat_id = nova_cat.id

    resp = cliente_admin.post(f"/categorias/{cat_id}/excluir", follow_redirects=False)
    assert resp.status_code == 302
    assert "excluido=ok" in resp.headers["location"]

    buscada = db_session.query(Categoria).filter_by(id=cat_id).first()
    assert buscada is None


def test_excluir_categoria_inexistente_erro(cliente_admin):
    """POST /categorias/{id}/excluir - Redirecionamento com erro quando ID não existe."""
    resp = cliente_admin.post("/categorias/99999/excluir", follow_redirects=False)
    assert resp.status_code == 302
    assert "erro=nao_encontrado" in resp.headers["location"]
