# test_armarios_api.py — Teste de API do Módulo de Armários

import requests
import random

BASE_URL = "http://127.0.0.1:8000"

def test_api():
    session = requests.Session()
    
    # 1. Login como admin
    login_data = {
        "email": "joaosilva@topzera.com.br",
        "senha": "joao1345"
    }
    resp = session.post(f"{BASE_URL}/auth/login", data=login_data, allow_redirects=True)
    print("Status Login:", resp.status_code)
    assert resp.status_code in [200, 302], "Falha no login"

    # 2. Listar armários via API
    resp = session.get(f"{BASE_URL}/armarios/api/listar")
    print("Status Listar API:", resp.status_code)
    data = resp.json()
    print("Stats Iniciais:", data["stats"])
    assert data["sucesso"] == True
    total_inicial = data["stats"]["total"]
    disponiveis_inicial = data["stats"]["disponiveis"]

    # 3. Criar um novo armário dinâmico
    novo_num = f"99{random.randint(10, 99)}"
    resp = session.post(
        f"{BASE_URL}/armarios/novo",
        data={"numero": novo_num, "localizacao": "Bloco C"},
        headers={"Accept": "application/json", "X-Requested-With": "XMLHttpRequest"}
    )
    print("Status Criar Armário:", resp.status_code, resp.json())
    assert resp.json()["sucesso"] == True
    novo_id = resp.json()["id"]

    # 4. Reservar o Armário recém-criado
    reserva_data = {
        "aluno_nome": "teste",
        "turma": "Senai",
        "contato": "11999999999",
        "data_inicio": "2026-08-09",
        "data_termino": "2026-08-11",
        "observacoes": "tese"
    }
    resp = session.post(
        f"{BASE_URL}/armarios/{novo_id}/reservar",
        data=reserva_data,
        headers={"Accept": "application/json", "X-Requested-With": "XMLHttpRequest"}
    )
    print("Status Reservar Armário:", resp.status_code, resp.json())
    assert resp.json()["sucesso"] == True

    # 5. Listar novamente e conferir stats e armário reservado
    resp = session.get(f"{BASE_URL}/armarios/api/listar")
    data = resp.json()
    print("Stats após reserva:", data["stats"])
    assert data["stats"]["total"] == total_inicial + 1
    assert data["stats"]["ocupados"] >= 1

    # 6. Obter detalhes do Armário
    resp = session.get(f"{BASE_URL}/armarios/{novo_id}")
    arm_detail = resp.json()["armario"]
    print("Detalhes Armário:", arm_detail)
    assert arm_detail["status"] == "Ocupado"
    assert arm_detail["aluno_nome"] == "teste"
    assert arm_detail["turma"] == "Senai"

    # 7. Liberar o Armário
    resp = session.post(
        f"{BASE_URL}/armarios/{novo_id}/liberar",
        headers={"Accept": "application/json", "X-Requested-With": "XMLHttpRequest"}
    )
    print("Status Liberar Armário:", resp.status_code, resp.json())
    assert resp.json()["sucesso"] == True

    # 8. Excluir o Armário de teste
    resp = session.post(
        f"{BASE_URL}/armarios/{novo_id}/excluir",
        headers={"Accept": "application/json", "X-Requested-With": "XMLHttpRequest"}
    )
    print("Status Excluir Armário:", resp.status_code, resp.json())
    assert resp.json()["sucesso"] == True

    print("\nTODOS OS TESTES PASSARAM COM SUCESSO!")

if __name__ == "__main__":
    test_api()
