import pytest

def test_painel_nao_autenticado_erro(cliente):
    """GET /painel - Erro 401 para usuário anônimo."""
    resp = cliente.get("/painel", follow_redirects=False)
    assert resp.status_code == 401


def test_painel_operador_proibido_erro(cliente_operador):
    """GET /painel - Erro 403 para usuário operador sem perfil admin."""
    resp = cliente_operador.get("/painel", follow_redirects=False)
    assert resp.status_code == 403


def test_painel_admin_sucesso(cliente_admin):
    """GET /painel - Sucesso ao acessar dashboard com usuário administrador."""
    resp = cliente_admin.get("/painel")
    assert resp.status_code == 200
    assert "text/html" in resp.headers["content-type"]
    assert "Painel" in resp.text
    # Verifica presença dos blocos essenciais do dashboard
    assert "Formas de Pagamento" in resp.text
    assert "Clube MARTPaper" in resp.text
    assert "chartPagamentos" in resp.text
    assert "chartVendas7Dias" in resp.text


def test_painel_com_barra_sucesso(cliente_admin):
    """GET /painel/ - Sucesso ao acessar rota com barra final."""
    resp = cliente_admin.get("/painel/")
    assert resp.status_code == 200
    assert "Painel" in resp.text
