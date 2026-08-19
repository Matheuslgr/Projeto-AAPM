from app.database import Session
from app.models.produto import Produto

PRODUTOS = [
    {"nome": "SEMESTRALIDADE AAPM", "preco": 100.0, "preco_associado": None},
    {"nome": "ARMÁRIO + SEMESTRALIDADE AAPM", "preco": 130.0, "preco_associado": None},
    {"nome": "Estacionamento (período noite e sábado)", "preco": 400.0, "preco_associado": None},
    {"nome": "2ª via de carteirinha", "preco": 20.0, "preco_associado": 15.0},
    {"nome": "Abridor de casa", "preco": 5.0, "preco_associado": 4.0},
    {"nome": "Agulha de maquina N. 11- pacote c/ 10un", "preco": 10.0, "preco_associado": 8.0},
    {"nome": "Alfinete c/ cabeça colorida", "preco": 3.0, "preco_associado": 2.0},
    {"nome": "Alfinete simples", "preco": 7.0, "preco_associado": 6.0},
    {"nome": "Alicate de Pic", "preco": 37.0, "preco_associado": 30.0},
    {"nome": "Apontador", "preco": 4.0, "preco_associado": 3.0},
    {"nome": "Avental", "preco": 50.0, "preco_associado": 45.0},
    {"nome": "Bobina", "preco": 2.0, "preco_associado": 1.0},
    {"nome": "Bolsa SENAI", "preco": 42.0, "preco_associado": 36.5},
    {"nome": "Borracha Artística", "preco": 10.0, "preco_associado": 9.0},
    {"nome": "Borracha branca", "preco": 2.5, "preco_associado": 2.0},
    {"nome": "Borracha Caneta", "preco": 13.5, "preco_associado": 11.0},
    {"nome": "Caixa de bobina", "preco": 8.0, "preco_associado": 7.0},
    {"nome": "Calculadora", "preco": 18.0, "preco_associado": 14.0},
    {"nome": "Camiseta malha Branca", "preco": 35.0, "preco_associado": 30.0},
    {"nome": "Camiseta malha Preta", "preco": 35.0, "preco_associado": 30.0},
    {"nome": "Caneta Mágica fantasminha colorida", "preco": 10.0, "preco_associado": 8.0},
    {"nome": "Caneta Nanquim", "preco": 20.0, "preco_associado": 16.0},
    {"nome": "Caneta Marca Texto", "preco": 7.0, "preco_associado": 5.0},
    {"nome": "Canetinha colorida c/ 12 cores", "preco": 10.0, "preco_associado": 8.5},
    {"nome": "Carretilha", "preco": 6.0, "preco_associado": 5.0},
    {"nome": "Cola bastão", "preco": 3.0, "preco_associado": 2.0},
    {"nome": "Cola Liquida", "preco": 5.0, "preco_associado": 4.5},
    {"nome": "Cordão para crachá SENAI", "preco": 6.0, "preco_associado": 5.0},
    {"nome": "Curva Francesa grande", "preco": 23.0, "preco_associado": 19.0},
    {"nome": "Curva Francesa pequena", "preco": 20.0, "preco_associado": 15.0},
    {"nome": "Durex", "preco": 4.0, "preco_associado": 3.0},
    {"nome": "Esfuminho", "preco": 6.5, "preco_associado": 5.5},
    {"nome": "Fita Crepe", "preco": 7.0, "preco_associado": 6.0},
    {"nome": "Esquadro", "preco": 5.0, "preco_associado": 4.0},
    {"nome": "Estojo Organizador M", "preco": 20.0, "preco_associado": 17.0},
    {"nome": "Fita Métrica", "preco": 5.0, "preco_associado": 3.0},
    {"nome": "Furador", "preco": 4.0, "preco_associado": 3.0},
    {"nome": "Garrafa (Squeeze)", "preco": 5.0, "preco_associado": 4.0},
    {"nome": "Giz lapis marcar tecido cores", "preco": 5.0, "preco_associado": 4.0},
    {"nome": "Grafite 05mm", "preco": 6.0, "preco_associado": 5.0},
    {"nome": "Grafite 07mm", "preco": 8.0, "preco_associado": 7.0},
    {"nome": "Grafite 09mm", "preco": 8.0, "preco_associado": 7.0},
    {"nome": "Kit de Modelagem", "preco": 215.0, "preco_associado": 185.0},
    {"nome": "Lápis HB nº2", "preco": 1.5, "preco_associado": 1.0},
    {"nome": "Lapiseira 0,5 - 0,7 E  09mm", "preco": 10.0, "preco_associado": 8.5},
    {"nome": "Lente Conta Fio", "preco": 28.0, "preco_associado": 23.0},
    {"nome": "Óculos de sobrepor 3M", "preco": 26.0, "preco_associado": 24.0},
    {"nome": "Óculos simples 3M", "preco": 16.0, "preco_associado": 14.0},
    {"nome": "Papel Kraft", "preco": 16.0, "preco_associado": 15.0},
    {"nome": "Papel Kraft A-4 Folha unitária", "preco": 1.5, "preco_associado": 1.0},
    {"nome": "Papel Sulfite c/100f", "preco": 9.0, "preco_associado": 8.0},
    {"nome": "Pinça Costura", "preco": 7.0, "preco_associado": 5.0},
    {"nome": "Porta crachá", "preco": 5.0, "preco_associado": 4.0},
    {"nome": "Protetor auricular", "preco": 6.0, "preco_associado": 5.0},
    {"nome": "Régua 15cm", "preco": 5.0, "preco_associado": 3.0},
    {"nome": "Régua 3 em 1", "preco": 55.0, "preco_associado": 50.0},
    {"nome": "Régua 30cm", "preco": 5.0, "preco_associado": 3.0},
    {"nome": "Régua conj. 3", "preco": 45.0, "preco_associado": 40.0},
    {"nome": "Régua Curvas", "preco": 5.0, "preco_associado": 5.0},
    {"nome": "Régua mm 30cm", "preco": 9.0, "preco_associado": 7.0},
    {"nome": "Régua mm 60cm", "preco": 23.0, "preco_associado": 19.0},
    {"nome": "Tesoura", "preco": 20.0, "preco_associado": 18.0},
    {"nome": "Tesoura Arremate", "preco": 6.0, "preco_associado": 4.0},
    {"nome": "Tesoura Picotar", "preco": 14.0, "preco_associado": 12.0},
    {"nome": "Vazador 2mm", "preco": 16.0, "preco_associado": 14.0},
    {"nome": "Grampeador pequeno", "preco": 10.0, "preco_associado": 9.0},
    {"nome": "Grampo p/ grampeador", "preco": 3.0, "preco_associado": 2.0},
]


def seed_produtos():
    db = Session()
    try:
        inseridos = 0
        atualizados = 0
        for item in PRODUTOS:
            existente = db.query(Produto).filter(
                (Produto.nome.ilike(item["nome"])) | (Produto.nome.ilike(f"%{item['nome']}%"))
            ).first()

            if existente:
                existente.preco = item["preco"]
                existente.preco_associado = item["preco_associado"]
                atualizados += 1
            else:
                produto = Produto(
                    nome=item["nome"],
                    preco=item["preco"],
                    preco_associado=item["preco_associado"],
                    estoque_atual=10,
                    ativo=True,
                    imagem_path=None,
                    categoria_id=None,
                )
                db.add(produto)
                inseridos += 1

        db.commit()
        print(f"Inserção/Atualização finalizada: {inseridos} criados, {atualizados} atualizados.")
    except Exception as erro:
        db.rollback()
        print(f"Erro ao popular produtos: {erro}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_produtos()
