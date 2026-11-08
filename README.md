# Sistema AAPM — PDV & Gestão Comercial

<div align="center">

![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![Pytest](https://img.shields.io/badge/Tests-129%20Passed-22c55e?style=for-the-badge&logo=pytest&logoColor=white)
![License](https://img.shields.io/badge/Status-Produção-blue?style=for-the-badge)

<p align="center">
  <strong>Solução integrada de Ponto de Venda (PDV), Controle de Estoque, Gestão de Associados e Business Intelligence (BI) desenvolvida para a Associação de Pais e Mestres (AAPM) da Escola SENAI Francisco Matarazzo / Papelaria MARTPaper.</strong>
</p>

</div>

---


##  Funcionalidades Principais

###  Ponto de Venda (PDV)
- **Carrinho Interativo em Tempo Real:** Adição e remoção rápida de itens, controle de quantidades e atualização instantânea de totais.
- **Pesquisa Instantânea:** Filtro de catálogo com debounce e navegação por abas de categorias.
- **Clube MARTPaper (Associados):** Busca de cliente por nome ou CPF com aplicação automática de preço exclusivo com desconto para sócios da AAPM.
- **Desconto Flexível:** Desconto manual por valor fixo (R$) ou porcentagem (%) com validações de limite.
- **Múltiplos Meios de Pagamento:** Suporte para Dinheiro (com cálculo automático de troco), Cartão de Débito, Cartão de Crédito e PIX.
- **Divisão de Pagamentos:** Possibilidade de quitar uma mesma venda utilizando 2 formas de pagamento distintas.
- **Comprovante de Venda:** Geração de cupom de conferência detalhado para impressão ou conferência operacional.

###  Painel Administrativo & Business Intelligence
- **Métricas em Tempo Real:** Faturamento diário, total de pedidos, ticket médio e taxa de adesão ao Clube MARTPaper.
- **Gráficos Interativos (Chart.js):** 
  - Faturamento diário dos últimos 7 dias com curva de tendência.
  - Distribuição percentual de formas de pagamento (gráfico donut).
  - Análise de horários de pico (volume de vendas por faixa de hora).
- **Controle de Estoque Crítico:** Lista instantânea de produtos com estoque baixo ($\le 5$ unidades).
- **Ranking Top 5:** Produtos mais vendidos em quantidade e faturamento.

###  Controle de Estoque & Movimentações
- **Entradas e Saídas:** Registro de auditoria com data/hora, tipo de operação, quantidade, custo unitário, valor total, motivo/observação e usuário responsável.
- **Histórico por Produto:** Visualização completa da movimentação individual de cada mercadoria.
- **Alertas Visuais de Estoque:** Badges intuitivas indicando estoque normal, baixo ou zerado.

###  Gestão de Clientes, Categorias e Produtos
- **Catálogo de Produtos:** Cadastro com fotos de exibição, preço de balcão e preço promocional para associados, vínculo com categorias e controle de visibilidade.
- **Categorias Dinâmicas:** Organização de itens da papelaria e serviços com contagem automática de produtos vinculados.
- **Gestão de Clientes:** Controle de membros ativos, histórico e identificação ágil no caixa.

###  Segurança & Controle de Acesso (RBAC)
- **Autenticação Segura:** Criptografia de senhas com algoritmo Bcrypt e sessões gerenciadas via tokens JWT em cookies seguros.
- **Níveis de Permissão:** Perfis diferenciados para **Administrador** (acesso total) e **Operador** (foco em vendas e movimentações).
- **Proteção de Integridade:** Regras de negócio que impedem a autoexclusão ou autodesativação do próprio administrador logado.

---

##  Tecnologias Utilizadas

| Camada | Tecnologias |
|---|---|
| **Backend** | [Python 3.13+](https://www.python.org/) • [FastAPI](https://fastapi.tiangolo.com/) • [Uvicorn](https://www.uvicorn.org/) |
| **Banco de Dados & ORM** | [SQLAlchemy](https://www.sqlalchemy.org/) • [SQLite](https://sqlite.org/) • [Alembic Migrations](https://alembic.sqlalchemy.org/) |
| **Segurança & Auth** | [Passlib (Bcrypt)](https://passlib.readthedocs.io/) • [Python-Jose (JWT)](https://python-jose.readthedocs.io/) |
| **Frontend** | [Jinja2 Templates](https://jinja.palletsprojects.com/) • HTML5 Semântico • CSS3 Moderno (Cards padronizados em 1500px) • Vanilla JavaScript |
| **Componentes & UI** | [Lucide Icons](https://lucide.dev/) • [Chart.js](https://www.chartjs.org/) • Google Fonts (Inter) |
| **Testes Automatizados** | [Pytest](https://docs.pytest.org/) • [HTTPX](https://www.python-httpx.org/) • AnyIO |

---

##  Estrutura do Projeto

```text
Projeto-AAPM/
├── app/
│   ├── controllers/         # Rotas e controladores da aplicação
│   │   ├── auth_controller.py
│   │   ├── cliente_controller.py
│   │   ├── produto_controller.py
│   │   ├── categoria_controller.py
│   │   ├── movimentacao_controller.py
│   │   ├── pdv_controller.py
│   │   ├── painel_controller.py
│   │   └── usuario_controller.py
│   ├── models/              # Modelos relacionais (SQLAlchemy ORM)
│   │   ├── usuarios.py
│   │   ├── produto.py
│   │   ├── categoria.py
│   │   ├── cliente.py
│   │   ├── movimentacao.py
│   │   ├── venda.py
│   │   └── armario.py
│   ├── templates/           # Telas e layouts em Jinja2
│   │   ├── auth/            # Login e autenticação
│   │   ├── painel/          # Dashboard e gráficos de BI
│   │   ├── produtos/        # Listagem e formulários de produtos
│   │   ├── categorias/      # Listagem e formulários de categorias
│   │   ├── clientes/        # Listagem e formulários de clientes
│   │   ├── movimentacoes/   # Registro e histórico de estoque
│   │   ├── historico_venda/ # Histórico de vendas e comprovantes
│   │   ├── base.html        # Layout base com barra superior e navegação
│   │   └── home.html        # Interface principal do PDV
│   ├── static/              # Ativos estáticos
│   │   ├── css/             # Estilos modulares (Cards 1500px)
│   │   ├── js/              # Lógica de carrinho, modais e filtros
│   │   ├── images/          # Logotipos e identidades visuais
│   │   └── uploads/         # Imagens dos produtos cadastrados
│   ├── auth.py              # Middleware, geração de JWT e hashing
│   ├── database.py          # Configuração de sessões do SQLAlchemy
│   └── main.py              # Ponto de entrada FastAPI e injeção de rotas
├── migrations/              # Histórico de versões e migrações do banco (Alembic)
├── test/                    # Suite com 129 testes automatizados
├── .env                     # Variáveis de ambiente
├── pytest.ini               # Configuração da suite de testes
├── requirements.txt         # Dependências do projeto
└── README.md                # Documentação técnica oficial
```

---

##  Como Executar o Projeto

### 1. Pré-requisitos
- **Python 3.11 ou superior** instalado na máquina.
- **Git** instalado.

### 2. Clonar o Repositório
```bash
git clone https://github.com/seu-usuario/Projeto-AAPM.git
cd Projeto-AAPM
```

### 3. Criar e Ativar o Ambiente Virtual

- **No Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

- **No Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. Instalar as Dependências
```bash
pip install -r requirements.txt
```

### 5. Configurar as Variáveis de Ambiente
Crie ou verifique o arquivo `.env` na raiz do projeto:
```dotenv
DATABASE_URL=sqlite:///banco.db
SECRET_KEY=sua_chave_secreta_super_segura_aqui
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

### 6. Executar as Migrações do Banco de Dados
```bash
python -m alembic upgrade head
```

### 7. (Opcional) Popular o Banco com Dados Iniciais
Para carregar usuários, categorias e catálogo de produtos de teste:
```bash
python criar_usuarios.py
python popular_categorias.py
python popular_produtos.py
python popular_armarios.py
```

### 8. Iniciar a Aplicação
```bash
python -m uvicorn app.main:app --reload
```

Acesse a aplicação no navegador em:  
 **[http://127.0.0.1:8000](http://127.0.0.1:8000)**

---

##  Credenciais Padrão para Testes

| Perfil | E-mail de Acesso | Senha | Acesso aos Módulos |
|---|---|---|---|
| **Administrador** | `joaosilva@topzera.com.br` | `joao1345` | Total (PDV, Histórico, Movimentações, Clientes, Produtos, Categorias, Painel, Usuários) |
| **Operador** | `operador@teste.com.br` | `operador123` | PDV, Histórico de Vendas e Movimentações de Estoque |

---

##  Testes Automatizados

O sistema conta com **129 testes automatizados** com cobertura integral de rotas, integridade de dados, regras de negócio e autenticação.

Para executar a suite de testes com saída detalhada:
```bash
pytest -v
```

Ou de forma rápida:
```bash
pytest
```

>  **Garantia de Isolamento:** Os testes executam em banco isolado (`banco test.db`), garantindo que os dados operacionais do banco principal (`banco.db`) nunca sejam alterados ou corrompidos durante os testes.

---

##  Padrões de Interface (Design System)

- **Cards Padronizados (1500px):** Todos os módulos principais de gestão (`Histórico`, `Movimentações`, `Clientes`, `Produtos`, `Categorias` e `Usuários`) contam com viewport uniforme de `max-width: 1500px`.
- **Preenchimento e Tipografia:** Espaçamento padronizado de `32px`, bordas arredondadas de `16px` e tipografia Inter com hierarquia limpa.
- **Feedback Visual:** Notificações flutuantes, modais de confirmação para ações destrutivas e badges semânticas de status.

---

##  Autores & Agradecimentos

Projeto desenvolvido para a **Associação de Pais e Mestres (AAPM)** da **Escola SENAI Francisco Matarazzo**.  
Agradecimentos a todos os instrutores, colaboradores e alunos que contribuíram para a evolução desta ferramenta.
