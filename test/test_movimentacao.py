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