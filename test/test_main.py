import pytest

def test_home_nao_autenticado_renderiza_login(cliente):
    """GET / - Usuário não logado visualiza a página de login."""
    resp = cliente.get("/")
    assert resp.status_code == 200
    assert "login" in resp.text.lower() or "entrar" in resp.text.lower()


def test_home_autenticado_renderiza_pdv(cliente_operador):
    """GET / - Usuário autenticado visualiza o painel inicial/PDV."""
    resp = cliente_operador.get("/")
    assert resp.status_code == 200
    assert "Apontador" in resp.text or "PDV" in resp.text or "Categorias" in resp.text


def test_rota_inexistente_retorna_404(cliente):
    """GET /rota-inexistente - Retorna página de erro 404 customizada."""
    resp = cliente.get("/rota-totalmente-inexistente-xyz")
    assert resp.status_code == 404
    assert "404" in resp.text or "não encontrada" in resp.text.lower()
