# Estrutura de Arquivos - AAPM PDV

## 📁 Organização de Arquivos Estáticos

```
app/static/
├── css/                  # ✨ Todos os CSS centralizados
│   ├── base.css         # Estilos antigos (compatibilidade)
│   ├── dashboard.css    # Layout principal do PDV
│   ├── login.css        # Página de login
│   ├── style.css        # Estilos adicionais gerais
│   ├── home.css         # Estilo do PDV (carrinho, itens)
│   ├── usuarios.css     # Gestão de usuários
│   ├── painel.css       # Painel administrativo
│   ├── produtos.css     # Gestão de produtos (form + lista)
│   └── movimentacoes.css # Gestão de movimentações de estoque
│
└── js/                  # JavaScript específico por página
    └── home.js          # Lógica do PDV (carrinho, filtros, busca)

uploads/                 # Imagens de produtos
```

## 📝 Estrutura de Templates

```
app/templates/
├── base.html            # Template base (header, nav, body wrapper)
├── home.html            # PDV - Página principal
├── index.html           # Página inicial/dashboard
│
├── auth/
│   └── login.html       # Página de autenticação
│
├── usuarios/
│   ├── index.html       # Listagem de usuários
│   └── form.html        # Formulário de criar/editar usuário
│
├── produtos/
│   ├── index.html       # Listagem de produtos
│   ├── form.html        # Formulário de criar/editar produto
│   └── detalhe.html     # Detalhes do produto (se houver)
│
├── categorias/
│   ├── index.html       # Listagem de categorias
│   └── form.html        # Formulário de criar/editar categoria
│
├── movimentacoes/
│   ├── index.html       # Histórico geral de movimentações
│   ├── form.html        # Registro de movimentação (entrada/saída)
│   └── historico.html   # Histórico específico de um produto
│
└── painel/
    └── index.html       # Painel administrativo
```

## ✅ Benefícios da Nova Organização

1. **Separação de Responsabilidades**
   - Cada arquivo CSS/JS cuida de um aspecto específico
   - Facilita manutenção e debug

2. **Melhor Performance**
   - Carregamento apenas dos arquivos necessários por página
   - Menos CSS/JS desnecessário no navegador

3. **Reutilização**
   - Arquivos globais (base.css, dashboard.css) em todos os templates
   - Arquivo CSS específico apenas quando necesário

4. **Manutenibilidade**
   - Código organizado em arquivos separados
   - Fácil encontrar e editar estilos de uma página
   - Menos poluição nos templates HTML

## 📚 Como Referenciar um Novo CSS

Se você criar um novo template, adicione o CSS assim:

```html
{% extends "base.html" %}

{% block title %}Minha Página{% endblock %}

{% block styles %}
<link rel="stylesheet" href="/static/css/minha-pagina.css">
{% endblock %}

{% block content %}
<!-- Seu HTML aqui -->
{% endblock %}
```

## 📚 Como Referenciar um Novo JS

Se você precisar de JavaScript específico:

```html
{% block scripts %}
<script src="/static/js/minha-pagina.js"></script>
{% endblock %}
```

## 🎨 Estilos Globais Disponíveis

Todos os templates têm acesso aos estilos globais via `:root`:

- `--accent-color`: Cor principal (azul)
- `--accent-hover`: Hover da cor principal
- `--orange-color`: Cor secundária (laranja)
- `--orange-hover`: Hover da cor laranja
- `--bg-card`: Fundo dos cards
- `--border-color`: Cor das bordas
- `--text-primary`: Cor do texto principal
- `--text-muted`: Cor do texto muted

## 🔧 Consolidação de CSS Anterior

Os arquivos CSS genéricos foram consolidados:
- `home.css` - Carrinho e itens dinâmicos
- `usuarios.css` - Tabela, filtros e buttons
- `painel.css` - Cards de estatísticas
- `produtos.css` - Formulário e lista de produtos

Estes arquivos substituem os antigos `<style>` tags inline nos templates.
