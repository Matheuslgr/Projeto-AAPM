import pytest
from app.models.produto import Produto
from app.models.movimentacao import Movimentacao, TipoMovimentacao

def test_listar_movimentacoes_sucesso(cliente_operador):
    """GET /movimentacoes/ - Sucesso ao visualizar histórico geral de movimentações."""
    resp = cliente_operador.get("/movimentacoes/")
    assert resp.status_code == 200
    assert "text/html" in resp.headers["content-type"]

def test_listar_movimentacoes_filtros_sucesso(cliente_operador):
    """GET /movimentacoes/ - Sucesso com filtros por tipo, ordenação e produto."""
    resp = cliente_operador.get("/movimentacoes/?produto_id=14&tipo=entrada&ordem=recentes")
    assert resp.status_code == 200

def test_listar_movimentacoes_nao_autenticado_erro(cliente):
    """GET /movimentacoes/ - Erro 401 para usuário não logado."""
    resp = cliente.get("/movimentacoes/", follow_redirects=False)
    assert resp.status_code == 401

def test_form_nova_movimentacao_sucesso(cliente_operador):
    """GET /movimentacoes/nova - Sucesso ao abrir formulário de movimentação."""
    resp = cliente_operador.get("/movimentacoes/nova")
    assert resp.status_code == 200
    assert "form" in resp.text.lower()

def test_registrar_entrada_sucesso(cliente_admin, db_session):
    """POST /movimentacoes/nova - Sucesso ao registrar entrada e aumentar estoque."""
    prod = db_session.query(Produto).filter_by(id=14).first()
    estoque_inicial = prod.estoque_atual

    payload = {
        "produto_id": 14,
        "tipo": "entrada",
        "quantidade": 15,
        "preco_unitario": 4.00,
        "observacao": "Reposição de estoque"
    }
    resp = cliente_admin.post("/movimentacoes/nova", data=payload, follow_redirects=False)
    assert resp.status_code == 302

    db_session.refresh(prod)
    assert prod.estoque_atual == estoque_inicial + 15

    mov = db_session.query(Movimentacao).filter_by(produto_id=14, observacao="Reposição de estoque").first()
    assert mov is not None
    assert mov.tipo == TipoMovimentacao.ENTRADA
    assert mov.quantidade == 15

def test_registrar_saida_sucesso(cliente_operador, db_session):
    """POST /movimentacoes/nova - Sucesso ao registrar saída e decrementar estoque."""
    prod = db_session.query(Produto).filter_by(id=14).first()
    estoque_inicial = prod.estoque_atual

    payload = {
        "produto_id": 14,
        "tipo": "saida",
        "quantidade": 2,
        "preco_unitario": 4.00,
        "observacao": "Saída balcão"
    }
    resp = cliente_operador.post("/movimentacoes/nova", data=payload, follow_redirects=False)
    assert resp.status_code == 302

    db_session.refresh(prod)
    assert prod.estoque_atual == estoque_inicial - 2