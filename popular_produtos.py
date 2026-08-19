from app.database import Session
from app.models.produto import Produto
from app.models.categoria import Categoria

CATEGORIAS = [
    "Serviços e Taxas",
    "Material Escolar",
    "Costura e Têxtil",
    "Desenho Técnico",
    "Papelaria e Organização",
    "Vestuário e Identificação",
    "Eletrônicos e EPI",
    "Lazer e Recreação",
]

PRODUTOS = [
    # Serviços e Taxas
    {"nome": "SEMESTRALIDADE AAPM", "preco": 100.0, "preco_associado": None, "categoria": "Serviços e Taxas"},
    {"nome": "ARMÁRIO + SEMESTRALIDADE AAPM", "preco": 130.0, "preco_associado": None, "categoria": "Serviços e Taxas"},
    {"nome": "Estacionamento (período noite e sábado)", "preco": 400.0, "preco_associado": None, "categoria": "Serviços e Taxas"},
    {"nome": "2ª via de carteirinha", "preco": 20.0, "preco_associado": 15.0, "categoria": "Serviços e Taxas"},

    # Costura e Têxtil
    {"nome": "Abridor de casa", "preco": 5.0, "preco_associado": 4.0, "categoria": "Costura e Têxtil"},
    {"nome": "Agulha de maquina N. 11- pacote c/ 10un", "preco": 10.0, "preco_associado": 8.0, "categoria": "Costura e Têxtil"},
    {"nome": "Alfinete c/ cabeça colorida", "preco": 3.0, "preco_associado": 2.0, "categoria": "Costura e Têxtil"},
    {"nome": "Alfinete simples", "preco": 7.0, "preco_associado": 6.0, "categoria": "Costura e Têxtil"},
    {"nome": "Alicate de Pic", "preco": 37.0, "preco_associado": 30.0, "categoria": "Costura e Têxtil"},
    {"nome": "Avental", "preco": 50.0, "preco_associado": 45.0, "categoria": "Costura e Têxtil"},
    {"nome": "Bobina", "preco": 2.0, "preco_associado": 1.0, "categoria": "Costura e Têxtil"},
    {"nome": "Caixa de bobina", "preco": 8.0, "preco_associado": 7.0, "categoria": "Costura e Têxtil"},
    {"nome": "Carretilha", "preco": 6.0, "preco_associado": 5.0, "categoria": "Costura e Têxtil"},
    {"nome": "Fita Métrica", "preco": 5.0, "preco_associado": 3.0, "categoria": "Costura e Têxtil"},
    {"nome": "Giz lapis marcar tecido cores", "preco": 5.0, "preco_associado": 4.0, "categoria": "Costura e Têxtil"},
    {"nome": "Kit de Modelagem", "preco": 215.0, "preco_associado": 185.0, "categoria": "Costura e Têxtil"},
    {"nome": "Lente Conta Fio", "preco": 28.0, "preco_associado": 23.0, "categoria": "Costura e Têxtil"},
    {"nome": "Pinça Costura", "preco": 7.0, "preco_associado": 5.0, "categoria": "Costura e Têxtil"},
    {"nome": "Tesoura Arremate", "preco": 6.0, "preco_associado": 4.0, "categoria": "Costura e Têxtil"},
    {"nome": "Tesoura Picotar", "preco": 14.0, "preco_associado": 12.0, "categoria": "Costura e Têxtil"},
    {"nome": "Vazador 2mm", "preco": 16.0, "preco_associado": 14.0, "categoria": "Costura e Têxtil"},

    # Material Escolar
    {"nome": "Apontador", "preco": 4.0, "preco_associado": 3.0, "categoria": "Material Escolar"},
    {"nome": "Borracha Artística", "preco": 10.0, "preco_associado": 9.0, "categoria": "Material Escolar"},
    {"nome": "Borracha branca", "preco": 2.5, "preco_associado": 2.0, "categoria": "Material Escolar"},
    {"nome": "Borracha Caneta", "preco": 13.5, "preco_associado": 11.0, "categoria": "Material Escolar"},
    {"nome": "Calculadora", "preco": 18.0, "preco_associado": 14.0, "categoria": "Material Escolar"},
    {"nome": "Caneta Mágica fantasminha colorida", "preco": 10.0, "preco_associado": 8.0, "categoria": "Material Escolar"},
    {"nome": "Caneta Nanquim", "preco": 20.0, "preco_associado": 16.0, "categoria": "Material Escolar"},
    {"nome": "Caneta Marca Texto", "preco": 7.0, "preco_associado": 5.0, "categoria": "Material Escolar"},
    {"nome": "Canetinha colorida c/ 12 cores", "preco": 10.0, "preco_associado": 8.5, "categoria": "Material Escolar"},
    {"nome": "Cola bastão", "preco": 3.0, "preco_associado": 2.0, "categoria": "Material Escolar"},
    {"nome": "Cola Liquida", "preco": 5.0, "preco_associado": 4.5, "categoria": "Material Escolar"},
    {"nome": "Durex", "preco": 4.0, "preco_associado": 3.0, "categoria": "Material Escolar"},
    {"nome": "Furador", "preco": 4.0, "preco_associado": 3.0, "categoria": "Material Escolar"},
    {"nome": "Grafite 05mm", "preco": 6.0, "preco_associado": 5.0, "categoria": "Material Escolar"},
    {"nome": "Grafite 07mm", "preco": 8.0, "preco_associado": 7.0, "categoria": "Material Escolar"},
    {"nome": "Grafite 09mm", "preco": 8.0, "preco_associado": 7.0, "categoria": "Material Escolar"},
    {"nome": "Lápis HB nº2", "preco": 1.5, "preco_associado": 1.0, "categoria": "Material Escolar"},
    {"nome": "Lapiseira 0,5 - 0,7 E  09mm", "preco": 10.0, "preco_associado": 8.5, "categoria": "Material Escolar"},
    {"nome": "Tesoura", "preco": 20.0, "preco_associado": 18.0, "categoria": "Material Escolar"},
    {"nome": "Grampeador pequeno", "preco": 10.0, "preco_associado": 9.0, "categoria": "Material Escolar"},
    {"nome": "Grampo p/ grampeador", "preco": 3.0, "preco_associado": 2.0, "categoria": "Material Escolar"},

    # Vestuário e Identificação
    {"nome": "Bolsa SENAI", "preco": 42.0, "preco_associado": 36.5, "categoria": "Vestuário e Identificação"},
    {"nome": "Camiseta malha Branca", "preco": 35.0, "preco_associado": 30.0, "categoria": "Vestuário e Identificação"},
    {"nome": "Camiseta malha Preta", "preco": 35.0, "preco_associado": 30.0, "categoria": "Vestuário e Identificação"},
    {"nome": "Cordão para crachá SENAI", "preco": 6.0, "preco_associado": 5.0, "categoria": "Vestuário e Identificação"},
    {"nome": "Porta crachá", "preco": 5.0, "preco_associado": 4.0, "categoria": "Vestuário e Identificação"},

    # Desenho Técnico
    {"nome": "Curva Francesa grande", "preco": 23.0, "preco_associado": 19.0, "categoria": "Desenho Técnico"},
    {"nome": "Curva Francesa pequena", "preco": 20.0, "preco_associado": 15.0, "categoria": "Desenho Técnico"},
    {"nome": "Esfuminho", "preco": 6.5, "preco_associado": 5.5, "categoria": "Desenho Técnico"},
    {"nome": "Esquadro", "preco": 5.0, "preco_associado": 4.0, "categoria": "Desenho Técnico"},
    {"nome": "Régua 15cm", "preco": 5.0, "preco_associado": 3.0, "categoria": "Desenho Técnico"},
    {"nome": "Régua 3 em 1", "preco": 55.0, "preco_associado": 50.0, "categoria": "Desenho Técnico"},
    {"nome": "Régua 30cm", "preco": 5.0, "preco_associado": 3.0, "categoria": "Desenho Técnico"},
    {"nome": "Régua conj. 3", "preco": 45.0, "preco_associado": 40.0, "categoria": "Desenho Técnico"},
    {"nome": "Régua Curvas", "preco": 5.0, "preco_associado": 5.0, "categoria": "Desenho Técnico"},
    {"nome": "Régua mm 30cm", "preco": 9.0, "preco_associado": 7.0, "categoria": "Desenho Técnico"},
    {"nome": "Régua mm 60cm", "preco": 23.0, "preco_associado": 19.0, "categoria": "Desenho Técnico"},

    # Papelaria e Organização
    {"nome": "Estojo Organizador M", "preco": 20.0, "preco_associado": 17.0, "categoria": "Papelaria e Organização"},
    {"nome": "Fita Crepe", "preco": 7.0, "preco_associado": 6.0, "categoria": "Papelaria e Organização"},
    {"nome": "Papel Kraft", "preco": 16.0, "preco_associado": 15.0, "categoria": "Papelaria e Organização"},
    {"nome": "Papel Kraft A-4 Folha unitária", "preco": 1.5, "preco_associado": 1.0, "categoria": "Papelaria e Organização"},
    {"nome": "Papel Sulfite c/100f", "preco": 9.0, "preco_associado": 8.0, "categoria": "Papelaria e Organização"},

    # Eletrônicos e EPI
    {"nome": "Óculos de sobrepor 3M", "preco": 26.0, "preco_associado": 24.0, "categoria": "Eletrônicos e EPI"},
    {"nome": "Óculos simples 3M", "preco": 16.0, "preco_associado": 14.0, "categoria": "Eletrônicos e EPI"},
    {"nome": "Protetor auricular", "preco": 6.0, "preco_associado": 5.0, "categoria": "Eletrônicos e EPI"},

    # Lazer e Recreação
    {"nome": "Garrafa (Squeeze)", "preco": 5.0, "preco_associado": 4.0, "categoria": "Lazer e Recreação"},
]


def seed_produtos():
    db = Session()
    try:
        # Garante a existência das categorias no banco
        cat_map = {}
        for nome_cat in CATEGORIAS:
            cat_obj = db.query(Categoria).filter_by(nome=nome_cat).first()
            if not cat_obj:
                cat_obj = Categoria(nome=nome_cat, ativo=True)
                db.add(cat_obj)
                db.flush()
            cat_map[nome_cat] = cat_obj.id

        inseridos = 0
        atualizados = 0
        for item in PRODUTOS:
            cat_id = cat_map.get(item.get("categoria"))

            existente = db.query(Produto).filter(
                (Produto.nome.ilike(item["nome"]))
            ).first()

            if existente:
                existente.preco = item["preco"]
                existente.preco_associado = item["preco_associado"]
                if cat_id:
                    existente.categoria_id = cat_id
                atualizados += 1
            else:
                produto = Produto(
                    nome=item["nome"],
                    preco=item["preco"],
                    preco_associado=item["preco_associado"],
                    estoque_atual=10,
                    ativo=True,
                    imagem_path=None,
                    categoria_id=cat_id,
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
