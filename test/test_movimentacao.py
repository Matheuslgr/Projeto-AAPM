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

def test_registrar_saida_estoque_insuficiente_erro(cliente_operador, db_session):
    """POST /movimentacoes/nova - Erro 400 por estoque insuficiente ao tentar saída maior que disponível."""
    prod = db_session.query(Produto).filter_by(id=14).first()
    qtd_excessiva = prod.estoque_atual + 500

    payload = {
        "produto_id": 14,
        "tipo": "saida",
        "quantidade": qtd_excessiva,
        "preco_unitario": 4.00,
        "observacao": "Tentativa inválida"
    }
    resp = cliente_operador.post("/movimentacoes/nova", data=payload, follow_redirects=False)
    assert resp.status_code == 400
    assert "Estoque insuficiente" in resp.text

def test_registrar_movimentacao_quantidade_invalida_erro(cliente_operador):
    """POST /movimentacoes/nova - Dados inválidos: quantidade zero ou negativa."""
    payload = {
        "produto_id": 14,
        "tipo": "entrada",
        "quantidade": 0,
        "preco_unitario": 4.00,
        "observacao": "Quantidade zerada"
    }
    resp = cliente_operador.post("/movimentacoes/nova", data=payload, follow_redirects=False)
    assert resp.status_code == 400
    assert "A quantidade deve ser maior que zero" in resp.text

def test_registrar_movimentacao_tipo_invalido_erro(cliente_operador):
    """POST /movimentacoes/nova - Dados inválidos: tipo de movimentação não permitido."""
    payload = {
        "produto_id": 14,
        "tipo": "tipo_desconhecido",
        "quantidade": 5,
        "preco_unitario": 4.00,
        "observacao": "Tipo incorreto"
    }
    resp = cliente_operador.post("/movimentacoes/nova", data=payload, follow_redirects=False)
    assert resp.status_code == 400
    assert "Tipo de movimentação inválido" in resp.text


def test_registrar_movimentacao_produto_inexistente_erro(cliente_operador):
    """POST /movimentacoes/nova - Redirecionamento quando o produto_id não existe."""
    payload = {
        "produto_id": 99999,
        "tipo": "entrada",
        "quantidade": 5,
        "preco_unitario": 4.00,
        "observacao": "Produto fantasma"
    }
    resp = cliente_operador.post("/movimentacoes/nova", data=payload, follow_redirects=False)
    assert resp.status_code == 302
    assert "/movimentacoes/nova" in resp.headers["location"]


def test_historico_produto_sucesso(cliente_operador):
    """GET /movimentacoes/produto/{id} - Sucesso ao consultar movimentações de produto específico."""
    resp = cliente_operador.get("/movimentacoes/produto/14")
    assert resp.status_code == 200
    assert "Apontador" in resp.text


def test_historico_produto_inexistente_erro(cliente_operador):
    """GET /movimentacoes/produto/{id} - Redirecionamento quando o produto não existe."""
    resp = cliente_operador.get("/movimentacoes/produto/99999", follow_redirects=False)
    assert resp.status_code == 302
    assert resp.headers["location"] == "/produtos"
