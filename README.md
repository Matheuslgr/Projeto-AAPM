# Projeto-AAPM 

<img width="1916" height="943" alt="Captura de tela 2026-04-24 094525" src="https://github.com/user-attachments/assets/e9bfc59c-49f5-4de6-a074-4763078b32ad" />


<img width="1316" height="868" alt="image" src="https://github.com/user-attachments/assets/91a21255-0436-4043-8108-ed4982491c08" />


# Instalar as bibliotecas

No terminal:
```bash
pip install -r requirements.txt
```

# Inicializar o alembic
No terminal:
```bash
python -m alembic init migrations
```

# Editar o arquivo alembic init -  na linha 89:
sqlalchemy.url = 

# Gerar a migration
no terminal:
```bash
python -m alembic revision --autogenerate -m "Criar a tabela usuarios"
```

# Aplicar a migration no banco
```bash
python -m alembic upgrade head
```

# Rodad o código
```bash
python -m uvicorn app.main:app --reload 
```


