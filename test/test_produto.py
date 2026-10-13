import pytest
from app.models.produto import Produto

def test_listar_produtos_sucesso(cliente_admin):
    """GET /produtos/ - Sucesso na listagem de produtos para admin."""
    resp = cliente_admin.get("/produtos/")
    assert resp.status_code == 200
    assert "text/html" in resp.headers["content-type"]
    assert "Apontador" in resp.text or "Borracha" in resp.text


def test_listar_produtos_busca_sucesso(cliente_admin):
    """GET /produtos/ - Sucesso com busca por termo."""
    resp = cliente_admin.get("/produtos/?busca=Apontador")
    assert resp.status_code == 200
    assert "Apontador" in resp.text


def test_listar_produtos_filtro_categoria(cliente_admin):
    """GET /produtos/ - Sucesso com filtro por categoria."""
    resp = cliente_admin.get("/produtos/?categoria_id=2")
    assert resp.status_code == 200
    assert "Apontador" in resp.text


def test_listar_produtos_inativos(cliente_admin, db_session):
    """GET /produtos/ - Sucesso ao filtrar por produtos inativos."""
    prod = db_session.query(Produto).first()
    if prod:
        prod.ativo = False
        db_session.commit()
    resp = cliente_admin.get("/produtos/?mostrar=inativos")
    assert resp.status_code == 200


def test_listar_produtos_nao_autenticado_erro(cliente):
    """GET /produtos/ - Erro 401 para usuário anônimo."""
    resp = cliente.get("/produtos/", follow_redirects=False)
    assert resp.status_code == 401


def test_listar_produtos_operador_proibido_erro(cliente_operador):
    """GET /produtos/ - Erro 403 para operador sem perfil admin."""
    resp = cliente_operador.get("/produtos/", follow_redirects=False)
    assert resp.status_code == 403


def test_form_novo_produto_sucesso(cliente_admin):
    """GET /produtos/novo - Sucesso ao abrir formulário de novo produto."""
    resp = cliente_admin.get("/produtos/novo")
    assert resp.status_code == 200
    assert "form" in resp.text.lower()


def test_criar_produto_sucesso(cliente_admin, db_session):
    """POST /produtos/novo - Sucesso ao cadastrar produto válido."""
    payload = {
        "nome": "Caderno Universitário Teste 2026",
        "preco": "19.90",
        "preco_associado": "17.00",
        "estoque_atual": "50",
        "categoria_id": "2"
    }
    files = {"imagem": ("", b"", "application/octet-stream")}
    resp = cliente_admin.post("/produtos/novo", data=payload, files=files, follow_redirects=False)
    assert resp.status_code == 302
    assert "/produtos?criado=ok" in resp.headers["location"]

    prod = db_session.query(Produto).filter_by(nome="Caderno Universitário Teste 2026").first()
    assert prod is not None
    assert prod.preco == 19.90
    assert prod.preco_associado == 17.00
    assert prod.estoque_atual == 50
    assert prod.ativo is True


def test_criar_produto_nome_duplicado_erro(cliente_admin):
    """POST /produtos/novo - Erro 400 ao tentar cadastrar produto com nome já existente."""
    payload = {
        "nome": "Apontador",
        "preco": "5.00",
        "preco_associado": "4.00",
        "estoque_atual": "10",
        "categoria_id": "2"
    }
    files = {"imagem": ("", b"", "application/octet-stream")}
    resp = cliente_admin.post("/produtos/novo", data=payload, files=files, follow_redirects=False)
    assert resp.status_code == 400
    assert "Já existe um produto com este nome" in resp.text


def test_detalhe_produto_sucesso(cliente_operador):
    """GET /produtos/{id} - Sucesso ao exibir detalhes de um produto existente (operador permitido)."""
    resp = cliente_operador.get("/produtos/14")
    assert resp.status_code == 200
    assert "Apontador" in resp.text


def test_detalhe_produto_inexistente_redirect(cliente_operador):
    """GET /produtos/{id} - Redireciona para /produtos quando o produto não existe."""
    resp = cliente_operador.get("/produtos/99999", follow_redirects=False)
    assert resp.status_code == 302
    assert resp.headers["location"] == "/produtos"


def test_form_editar_produto_sucesso(cliente_admin):
    """GET /produtos/{id}/editar - Sucesso ao abrir tela de edição de produto."""
    resp = cliente_admin.get("/produtos/14/editar")
    assert resp.status_code == 200
    assert "Apontador" in resp.text


def test_form_editar_produto_inexistente(cliente_admin):
    """GET /produtos/{id}/editar - Redireciona quando produto a editar não existe."""
    resp = cliente_admin.get("/produtos/99999/editar", follow_redirects=False)
    assert resp.status_code == 302
    assert resp.headers["location"] == "/produtos"


def test_editar_produto_sucesso(cliente_admin, db_session):
    """POST /produtos/{id}/editar - Sucesso ao atualizar produto existente."""
    payload = {
        "nome": "Apontador Super Especial",
        "preco": "6.50",
        "preco_associado": "5.50",
        "estoque_atual": "25",
        "categoria_id": "2"
    }
    files = {"imagem": ("", b"", "application/octet-stream")}
    resp = cliente_admin.post("/produtos/14/editar", data=payload, files=files, follow_redirects=False)
    assert resp.status_code == 302
    assert "/produtos?editado=ok" in resp.headers["location"]

    prod = db_session.query(Produto).filter_by(id=14).first()
    assert prod.nome == "Apontador Super Especial"
    assert prod.preco == 6.50
    assert prod.estoque_atual == 25


def test_editar_produto_conflito_nome_erro(cliente_admin):
    """POST /produtos/{id}/editar - Erro 400 ao editar produto colocando o nome de outro produto já existente."""
    payload = {
        "nome": "Borracha branca",  # Já pertence ao id 22
        "preco": "6.50",
        "preco_associado": "5.50",
        "estoque_atual": "25",
        "categoria_id": "2"
    }
    files = {"imagem": ("", b"", "application/octet-stream")}
    resp = cliente_admin.post("/produtos/14/editar", data=payload, files=files, follow_redirects=False)
    assert resp.status_code == 400
    assert "Já existe outro produto com este nome" in resp.text


def test_desativar_produto_sucesso(cliente_admin, db_session):
    """POST /produtos/{id}/desativar - Sucesso ao desativar produto."""
    resp = cliente_admin.post("/produtos/14/desativar", follow_redirects=False)
    assert resp.status_code == 302
    assert "/produtos?desativado=ok" in resp.headers["location"]

    prod = db_session.query(Produto).filter_by(id=14).first()
    assert prod.ativo is False


def test_reativar_produto_sucesso(cliente_admin, db_session):
    """POST /produtos/{id}/reativar - Sucesso ao reativar produto."""
    prod = db_session.query(Produto).filter_by(id=14).first()
    prod.ativo = False
    db_session.commit()

    resp = cliente_admin.post("/produtos/14/reativar", follow_redirects=False)
    assert resp.status_code == 302
    assert "/produtos?reativado=ok" in resp.headers["location"]

    prod = db_session.query(Produto).filter_by(id=14).first()
    assert prod.ativo is True


def test_toggle_ativo_produto_sucesso(cliente_admin, db_session):
    """POST /produtos/{id}/toggle-ativo - Alterna status de ativo do produto."""
    resp = cliente_admin.post("/produtos/14/toggle-ativo", data={"mostrar": "ativos"}, follow_redirects=False)
    assert resp.status_code == 302

    prod = db_session.query(Produto).filter_by(id=14).first()
    assert prod.ativo is False
