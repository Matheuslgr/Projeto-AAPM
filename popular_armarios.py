# popular_armarios.py — Popula armários iniciais

from app.database import Session
from app.models.armario import Armario

def popular():
    db = Session()
    try:
        total_existentes = db.query(Armario).count()
        if total_existentes > 0:
            print(f"Já existem {total_existentes} armários cadastrados no banco.")
            return

        armarios_iniciais = []
        for i in range(1, 21):
            num_str = f"{i:03d}"
            local = "Bloco A" if i <= 10 else "Bloco B"
            armario = Armario(
                numero=num_str,
                localizacao=local,
                status="Livre"
            )
            armarios_iniciais.append(armario)

        db.add_all(armarios_iniciais)
        db.commit()
        print(f"Sucesso! {len(armarios_iniciais)} armários criados com sucesso.")
    except Exception as e:
        db.rollback()
        print(f"Erro ao popular armários: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    popular()
