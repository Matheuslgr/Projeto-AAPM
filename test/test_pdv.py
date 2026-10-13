import json
import pytest
from app.models.venda import Venda, ItemVenda, PagamentoVenda
from app.models.produto import Produto
from app.models.movimentacao import Movimentacao, TipoMovimentacao

def test_tela_pdv_nao_autenticado_erro(cliente):
    """GET /pdv/ - Erro 401 para usuário anônimo."""
    resp = cliente.get("/pdv/", follow_redirects=False)
    assert resp.status_code == 401


def test_tela_pdv_sucesso(cliente_operador):
    """GET /pdv/ - Sucesso ao carregar tela do PDV para operador."""
    resp = cliente_operador.get("/pdv/")
    assert resp.status_code == 200
    assert "text/html" in resp.headers["content-type"]
    assert "Apontador" in resp.text


def test_finalizar_venda_carrinho_vazio_erro(cliente_operador):
    """POST /pdv/finalizar - Erro ao enviar carrinho vazio."""
    payload = {
        "carrinho_json": "[]",
        "cliente_id": "0",
        "desconto_manual": "0.0",
        "desconto_tipo": "reais",
        "pagamentos_json": "[]"
    }
    resp = cliente_operador.post("/pdv/finalizar", data=payload, follow_redirects=False)
    assert resp.status_code == 302
    assert "erro=vazio" in resp.headers["location"]


def test_finalizar_venda_json_invalido_erro(cliente_operador):
    """POST /pdv/finalizar - Erro ao enviar JSON corrompido no carrinho."""
    payload = {
        "carrinho_json": "{invalido",
        "cliente_id": "0",
        "desconto_manual": "0.0",
        "desconto_tipo": "reais",
        "pagamentos_json": "[]"
    }
    resp = cliente_operador.post("/pdv/finalizar", data=payload, follow_redirects=False)
    assert resp.status_code == 302
    assert "erro=json" in resp.headers["location"]


def test_finalizar_venda_quantidade_invalida_erro(cliente_operador):
    """POST /pdv/finalizar - Erro quando a quantidade de um item for menor ou igual a zero."""
    carrinho = [{"produto_id": 14, "quantidade": 0}]
    payload = {
        "carrinho_json": json.dumps(carrinho),
        "cliente_id": "0",
        "desconto_manual": "0.0",
        "desconto_tipo": "reais",
        "pagamentos_json": "[]"
    }
    resp = cliente_operador.post("/pdv/finalizar", data=payload, follow_redirects=False)
    assert resp.status_code == 302
    assert "erro=quantidade" in resp.headers["location"]


def test_finalizar_venda_produto_inexistente_erro(cliente_operador):
    """POST /pdv/finalizar - Erro quando o item não existir no banco de dados."""
    carrinho = [{"produto_id": 99999, "quantidade": 1}]
    payload = {
        "carrinho_json": json.dumps(carrinho),
        "cliente_id": "0",
        "desconto_manual": "0.0",
        "desconto_tipo": "reais",
        "pagamentos_json": "[]"
    }
    resp = cliente_operador.post("/pdv/finalizar", data=payload, follow_redirects=False)
    assert resp.status_code == 302
    assert "erro=produto_inexistente" in resp.headers["location"]


def test_finalizar_venda_estoque_insuficiente_erro(cliente_operador):
    """POST /pdv/finalizar - Erro quando a quantidade pedida exceder o estoque disponível."""
    carrinho = [{"produto_id": 14, "quantidade": 9999}]
    payload = {
        "carrinho_json": json.dumps(carrinho),
        "cliente_id": "0",
        "desconto_manual": "0.0",
        "desconto_tipo": "reais",
        "pagamentos_json": "[]"
    }
    resp = cliente_operador.post("/pdv/finalizar", data=payload, follow_redirects=False)
    assert resp.status_code == 302
    assert "erro=estoque" in resp.headers["location"]


def test_finalizar_venda_dinheiro_sucesso(cliente_operador, db_session):
    """POST /pdv/finalizar - Sucesso na venda com pagamento em Dinheiro e cálculo de troco."""
    prod = db_session.query(Produto).filter_by(id=14).first()
    estoque_inicial = prod.estoque_atual

    carrinho = [{"produto_id": 14, "quantidade": 2}]  # 2 * 4.0 = 8.0
    pagamentos = [{
        "forma_pagamento": "DINHEIRO",
        "valor": 8.0,
        "valor_recebido": 10.0,
        "troco": 2.0
    }]
    payload = {
        "carrinho_json": json.dumps(carrinho),
        "cliente_id": "0",
        "observacao": "Venda teste dinheiro",
        "desconto_manual": "0.0",
        "desconto_tipo": "reais",
        "pagamentos_json": json.dumps(pagamentos)
    }
    resp = cliente_operador.post("/pdv/finalizar", data=payload, follow_redirects=False)
    assert resp.status_code == 302
    assert "/pdv/venda/" in resp.headers["location"]
    assert "sucesso=ok" in resp.headers["location"]

    venda_id = int(resp.headers["location"].split("/pdv/venda/")[1].split("?")[0])
    venda = db_session.query(Venda).filter_by(id=venda_id).first()
    assert venda is not None
    assert venda.total_bruto == 8.0
    assert venda.total_liquido == 8.0
    assert len(venda.itens) == 1
    assert venda.itens[0].quantidade == 2
    assert venda.itens[0].preco_unitario == 4.0

    assert len(venda.pagamentos) == 1
    assert venda.pagamentos[0].forma_pagamento == "DINHEIRO"
    assert venda.pagamentos[0].valor == 8.0
    assert venda.pagamentos[0].valor_recebido == 10.0
    assert venda.pagamentos[0].troco == 2.0

    # Estoque baixado
    db_session.refresh(prod)
    assert prod.estoque_atual == estoque_inicial - 2

    # Movimentação registrada
    mov = db_session.query(Movimentacao).filter_by(produto_id=14, observacao=f"Venda PDV #{venda_id}").first()
    assert mov is not None
    assert mov.tipo == TipoMovimentacao.SAIDA
    assert mov.quantidade == 2


def test_finalizar_venda_pix_sucesso(cliente_operador, db_session):
    """POST /pdv/finalizar - Sucesso na venda com pagamento via PIX."""
    carrinho = [{"produto_id": 14, "quantidade": 1}]  # 4.0
    pagamentos = [{"forma_pagamento": "PIX", "valor": 4.0}]
    payload = {
        "carrinho_json": json.dumps(carrinho),
        "cliente_id": "0",
        "desconto_manual": "0.0",
        "desconto_tipo": "reais",
        "pagamentos_json": json.dumps(pagamentos)
    }
    resp = cliente_operador.post("/pdv/finalizar", data=payload, follow_redirects=False)
    assert resp.status_code == 302
    assert "sucesso=ok" in resp.headers["location"]

    venda_id = int(resp.headers["location"].split("/pdv/venda/")[1].split("?")[0])
    venda = db_session.query(Venda).filter_by(id=venda_id).first()
    assert len(venda.pagamentos) == 1
    assert venda.pagamentos[0].forma_pagamento == "PIX"
    assert venda.pagamentos[0].valor == 4.0


def test_finalizar_venda_duas_formas_pagamento_sucesso(cliente_operador, db_session):
    """POST /pdv/finalizar - Sucesso na venda com 2 formas de pagamento (Dinheiro + PIX)."""
    carrinho = [{"produto_id": 14, "quantidade": 2}]  # 8.0
    pagamentos = [
        {"forma_pagamento": "DINHEIRO", "valor": 5.0, "valor_recebido": 5.0, "troco": 0.0},
        {"forma_pagamento": "PIX", "valor": 3.0}
    ]
    payload = {
        "carrinho_json": json.dumps(carrinho),
        "cliente_id": "0",
        "desconto_manual": "0.0",
        "desconto_tipo": "reais",
        "pagamentos_json": json.dumps(pagamentos)
    }
    resp = cliente_operador.post("/pdv/finalizar", data=payload, follow_redirects=False)
    assert resp.status_code == 302
    assert "sucesso=ok" in resp.headers["location"]

    venda_id = int(resp.headers["location"].split("/pdv/venda/")[1].split("?")[0])
    venda = db_session.query(Venda).filter_by(id=venda_id).first()
    assert len(venda.pagamentos) == 2
    formas = [p.forma_pagamento for p in venda.pagamentos]
    assert "DINHEIRO" in formas
    assert "PIX" in formas


def test_finalizar_venda_mais_de_duas_formas_erro(cliente_operador):
    """POST /pdv/finalizar - Erro ao tentar pagar com mais de 2 formas de pagamento."""
    carrinho = [{"produto_id": 14, "quantidade": 1}]
    pagamentos = [
        {"forma_pagamento": "DINHEIRO", "valor": 1.0},
        {"forma_pagamento": "PIX", "valor": 1.0},
        {"forma_pagamento": "CARTAO_DEBITO", "valor": 2.0}
    ]
    payload = {
        "carrinho_json": json.dumps(carrinho),
        "cliente_id": "0",
        "desconto_manual": "0.0",
        "desconto_tipo": "reais",
        "pagamentos_json": json.dumps(pagamentos)
    }
    resp = cliente_operador.post("/pdv/finalizar", data=payload, follow_redirects=False)
    assert resp.status_code == 302
    assert "erro=max_duas_formas" in resp.headers["location"]


def test_finalizar_venda_soma_pagamentos_divergente_erro(cliente_operador):
    """POST /pdv/finalizar - Erro quando a soma das parcelas não bate com o valor da venda."""
    carrinho = [{"produto_id": 14, "quantidade": 2}]  # total 8.0
    pagamentos = [{"forma_pagamento": "DINHEIRO", "valor": 5.0, "valor_recebido": 5.0}]  # falta 3.0
    payload = {
        "carrinho_json": json.dumps(carrinho),
        "cliente_id": "0",
        "desconto_manual": "0.0",
        "desconto_tipo": "reais",
        "pagamentos_json": json.dumps(pagamentos)
    }
    resp = cliente_operador.post("/pdv/finalizar", data=payload, follow_redirects=False)
    assert resp.status_code == 302
    assert "erro=soma_pagamentos_invalida" in resp.headers["location"]


def test_finalizar_venda_dinheiro_insuficiente_erro(cliente_operador):
    """POST /pdv/finalizar - Erro quando o valor recebido em dinheiro é menor que a parcela."""
    carrinho = [{"produto_id": 14, "quantidade": 1}]  # 4.0
    pagamentos = [{"forma_pagamento": "DINHEIRO", "valor": 4.0, "valor_recebido": 2.0}]
    payload = {
        "carrinho_json": json.dumps(carrinho),
        "cliente_id": "0",
        "desconto_manual": "0.0",
        "desconto_tipo": "reais",
        "pagamentos_json": json.dumps(pagamentos)
    }
    resp = cliente_operador.post("/pdv/finalizar", data=payload, follow_redirects=False)
    assert resp.status_code == 302
    assert "erro=dinheiro_insuficiente" in resp.headers["location"]


def test_finalizar_venda_cliente_associado_sucesso(cliente_operador, db_session):
    """POST /pdv/finalizar - Aplica preço especial de associado do Clube MARTPaper."""
    # Produto 14: normal 4.0, associado 3.0
    # Cliente 1: is_associado = True
    carrinho = [{"produto_id": 14, "quantidade": 2}]  # 2 * 3.0 = 6.0
    pagamentos = [{"forma_pagamento": "PIX", "valor": 6.0}]
    payload = {
        "carrinho_json": json.dumps(carrinho),
        "cliente_id": "1",
        "desconto_manual": "0.0",
        "desconto_tipo": "reais",
        "pagamentos_json": json.dumps(pagamentos)
    }
    resp = cliente_operador.post("/pdv/finalizar", data=payload, follow_redirects=False)
    assert resp.status_code == 302
    assert "sucesso=ok" in resp.headers["location"]

    venda_id = int(resp.headers["location"].split("/pdv/venda/")[1].split("?")[0])
    venda = db_session.query(Venda).filter_by(id=venda_id).first()
    assert venda.total_bruto == 8.0
    assert venda.total_liquido == 6.0
    assert venda.cliente_id == 1


def test_finalizar_venda_desconto_manual_reais(cliente_operador, db_session):
    """POST /pdv/finalizar - Sucesso com desconto manual em reais."""
    carrinho = [{"produto_id": 14, "quantidade": 2}]  # 8.0
    # Desconto de R$ 3.0 -> total 5.0
    pagamentos = [{"forma_pagamento": "PIX", "valor": 5.0}]
    payload = {
        "carrinho_json": json.dumps(carrinho),
        "cliente_id": "0",
        "desconto_manual": "3.0",
        "desconto_tipo": "reais",
        "pagamentos_json": json.dumps(pagamentos)
    }
    resp = cliente_operador.post("/pdv/finalizar", data=payload, follow_redirects=False)
    assert resp.status_code == 302

    venda_id = int(resp.headers["location"].split("/pdv/venda/")[1].split("?")[0])
    venda = db_session.query(Venda).filter_by(id=venda_id).first()
    assert venda.total_liquido == 5.0
    assert venda.desconto_manual == 3.0


def test_finalizar_venda_desconto_acima_limite_erro(cliente_operador):
    """POST /pdv/finalizar - Erro ao tentar aplicar desconto maior que 100% ou maior que o total."""
    carrinho = [{"produto_id": 14, "quantidade": 1}]  # 4.0
    payload = {
        "carrinho_json": json.dumps(carrinho),
        "cliente_id": "0",
        "desconto_manual": "10.0",  # Maior que os 4.0
        "desconto_tipo": "reais",
        "pagamentos_json": "[]"
    }
    resp = cliente_operador.post("/pdv/finalizar", data=payload, follow_redirects=False)
    assert resp.status_code == 302
    assert "erro=desconto_acima_limite" in resp.headers["location"]


def test_detalhe_comprovante_venda_sucesso(cliente_operador):
    """GET /pdv/venda/{id} - Sucesso ao carregar comprovante de venda existente."""
    resp = cliente_operador.get("/pdv/venda/1")
    assert resp.status_code == 200
    assert "text/html" in resp.headers["content-type"]
    assert "Comprovante" in resp.text


def test_detalhe_comprovante_venda_inexistente(cliente_operador):
    """GET /pdv/venda/{id} - Redireciona para /pdv quando a venda não existe."""
    resp = cliente_operador.get("/pdv/venda/99999", follow_redirects=False)
    assert resp.status_code == 302
    assert resp.headers["location"] == "/pdv"


def test_historico_vendas_sucesso(cliente_operador):
    """GET /pdv/historico - Sucesso ao acessar histórico de vendas."""
    resp = cliente_operador.get("/pdv/historico")
    assert resp.status_code == 200
    assert "Histórico de Vendas" in resp.text


def test_historico_vendas_busca_e_ordem(cliente_operador):
    """GET /pdv/historico - Sucesso com parâmetros de busca e ordenação."""
    resp = cliente_operador.get("/pdv/historico?busca=1&ordem=maior_valor")
    assert resp.status_code == 200
    assert "Histórico de Vendas" in resp.text
