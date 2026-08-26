// Carrega os dados passados pelo backend no elemento #pdv-data
const pdvDataElement = document.getElementById('pdv-data');
const pdvData = pdvDataElement ? JSON.parse(pdvDataElement.textContent) : { desconto_associado: 10.0, produtos: [] };

const DESCONTO_PCT = pdvData.desconto_associado || 10.0;
const productsData = pdvData.produtos || [];

// Estado do Carrinho e do Cliente
let carrinho = [];
let clienteAtual = { id: 0, associado: false };

// Elementos do DOM
const productsGrid = document.getElementById('products-grid');
const searchInput = document.getElementById('search-input');
const categoryButtons = document.querySelectorAll('.category-btn');
const emptyCartState = document.getElementById('empty-cart-state');
const cartItemsList = document.getElementById('cart-items-list');
const checkoutBtn = document.getElementById('checkout-btn');

// Filtros Atuais e Paginação
let currentSearch = "";
let currentCategory = "all";
let pdvCurrentPage = 1;
const PDV_ITEMS_PER_PAGE = 14;

/**
 * Renderiza o grid de produtos com base nos filtros atuais e paginação
 */
function renderProducts() {
    if (!productsGrid) return;
    productsGrid.innerHTML = "";
    
    const filteredProducts = productsData.filter(product => {
        const matchesSearch = product.name.toLowerCase().includes(currentSearch.toLowerCase());
        const matchesCategory = currentCategory === "all" || product.category === currentCategory;
        return matchesSearch && matchesCategory;
    });

    const totalFiltered = filteredProducts.length;
    const totalPages = Math.ceil(totalFiltered / PDV_ITEMS_PER_PAGE) || 1;

    if (pdvCurrentPage > totalPages) {
        pdvCurrentPage = totalPages;
    }
    if (pdvCurrentPage < 1) {
        pdvCurrentPage = 1;
    }

    const startIndex = (pdvCurrentPage - 1) * PDV_ITEMS_PER_PAGE;
    const paginatedProducts = filteredProducts.slice(startIndex, startIndex + PDV_ITEMS_PER_PAGE);

    if (paginatedProducts.length === 0) {
        productsGrid.innerHTML = `
            <div style="grid-column: 1/-1; text-align: center; color: var(--text-muted); padding: 40px;">
                Nenhum produto encontrado.
            </div>
        `;
        renderPdvPagination(0, 1);
        return;
    }

    paginatedProducts.forEach(product => {
        const card = document.createElement('div');
        card.className = 'product-card';
        card.onclick = () => addToCart(product.id);
        
        let imagemHtml = `
            <div class="product-image-placeholder">
                <i data-lucide="image"></i>
            </div>
        `;
        
        if (product.imagem && product.imagem !== "None" && product.imagem !== "" && !product.imagem.includes("produto-placeholder.png")) {
            imagemHtml = `
            <img src="${product.imagem}" alt="${product.name}" 
                 style="width: 100%; aspect-ratio: 1; object-fit: cover; border-radius: 8px;"
                 onerror="this.outerHTML='<div class=\\'product-image-placeholder\\'><i data-lucide=\\'image\\'></i></div>'; setTimeout(() => lucide.createIcons(), 10);">
            `;
        }

        card.innerHTML = `
            ${imagemHtml}
            <div class="product-info">
                <span class="product-name" title="${product.name}">${product.name}</span>
                <span class="product-category">${product.category}</span>
            </div>
            <div class="product-footer">
                <span class="product-price">R$ ${product.price.toFixed(2).replace('.', ',')}</span>
                <button class="add-to-cart-btn" onclick="event.stopPropagation(); addToCart(${product.id})">
                    <i data-lucide="shopping-cart"></i>
                </button>
            </div>
        `;
        
        productsGrid.appendChild(card);
    });

    renderPdvPagination(totalFiltered, totalPages);
    lucide.createIcons();
}

/**
 * Altera a página atual do PDV
 */
function changePdvPage(newPage) {
    pdvCurrentPage = newPage;
    renderProducts();
    const pdvSection = document.querySelector('.pdv-section');
    if (pdvSection) {
        pdvSection.scrollTo({ top: 0, behavior: 'smooth' });
    }
}

/**
 * Renderiza os controles de paginação do PDV
 */
function renderPdvPagination(totalItems, totalPages) {
    const paginationEl = document.getElementById('pdv-pagination');
    if (!paginationEl) return;

    if (totalItems <= PDV_ITEMS_PER_PAGE) {
        paginationEl.style.display = 'none';
        paginationEl.innerHTML = '';
        return;
    }

    paginationEl.style.display = 'flex';

    const start = (pdvCurrentPage - 1) * PDV_ITEMS_PER_PAGE + 1;
    const end = Math.min(pdvCurrentPage * PDV_ITEMS_PER_PAGE, totalItems);

    let pagesHtml = '';
    for (let p = 1; p <= totalPages; p++) {
        if (p === 1 || p === totalPages || (p >= pdvCurrentPage - 2 && p <= pdvCurrentPage + 2)) {
            pagesHtml += `
                <button type="button" class="pagination-btn ${p === pdvCurrentPage ? 'active' : ''}" onclick="changePdvPage(${p})">
                    ${p}
                </button>
            `;
        } else if (p === pdvCurrentPage - 3 || p === pdvCurrentPage + 3) {
            pagesHtml += `<span class="pagination-ellipsis">...</span>`;
        }
    }

    paginationEl.innerHTML = `
        <div class="pagination-info">
            Mostrando <strong>${start}</strong> a <strong>${end}</strong> de <strong>${totalItems}</strong> produtos
        </div>
        <div class="pagination-controls">
            <button type="button" class="pagination-btn ${pdvCurrentPage <= 1 ? 'disabled' : ''}" 
                    ${pdvCurrentPage <= 1 ? 'disabled' : ''} 
                    onclick="changePdvPage(${pdvCurrentPage - 1})">
                <i data-lucide="chevron-left" style="width: 16px; height: 16px;"></i>
                Anterior
            </button>
            <div class="pagination-pages">
                ${pagesHtml}
            </div>
            <button type="button" class="pagination-btn ${pdvCurrentPage >= totalPages ? 'disabled' : ''}" 
                    ${pdvCurrentPage >= totalPages ? 'disabled' : ''} 
                    onclick="changePdvPage(${pdvCurrentPage + 1})">
                Próximo
                <i data-lucide="chevron-right" style="width: 16px; height: 16px;"></i>
            </button>
        </div>
    `;

    lucide.createIcons();
}

/**
 * Adiciona um produto ao carrinho
 */
function addToCart(productId) {
    const product = productsData.find(p => p.id === productId);
    if (!product) return;

    const existente = carrinho.find(item => item.produto_id === productId);

    if (existente) {
        if (existente.quantidade < existente.estoque_max) {
            existente.quantidade += 1;
        } else {
            alert(`Estoque máximo atingido: ${existente.estoque_max} unidade(s).`);
            return;
        }
    } else {
        carrinho.push({
            produto_id: product.id,
            nome: product.name,
            preco: product.price,
            preco_associado: product.preco_associado !== undefined && product.preco_associado !== null ? product.preco_associado : product.price,
            quantidade: 1,
            estoque_max: product.estoque_max || 9999
        });
    }

    updateCartUI();
}

/**
 * Altera a quantidade de um item no carrinho
 */
function alterQtd(productId, delta) {
    const item = carrinho.find(i => i.produto_id === productId);
    if (!item) return;

    item.quantidade += delta;

    if (item.quantidade <= 0) {
        removeFromCart(productId);
        return;
    }

    if (item.quantidade > item.estoque_max) {
        item.quantidade = item.estoque_max;
        alert(`Estoque máximo disponível: ${item.estoque_max}`);
    }

    updateCartUI();
}

/**
 * Remove um item do carrinho
 */
function removeFromCart(productId) {
    carrinho = carrinho.filter(i => i.produto_id !== productId);
    updateCartUI();
}

const clientesData = pdvData.clientes || [
    { id: 0, nome: "Sem identificação (sem desconto)", matricula: "", is_associado: false }
];

/**
 * Abre o dropdown de clientes ao focar no campo de busca
 */
function abrirDropdownClientes() {
    const searchInput = document.getElementById('cliente-search-input');
    filtrarClientes(searchInput ? searchInput.value : '');
}

/**
 * Filtra a lista de clientes por nome ou matrícula e renderiza os resultados
 */
function filtrarClientes(termo) {
    const dropdown = document.getElementById('cliente-dropdown-results');
    if (!dropdown) return;

    const termLower = (termo || '').toLowerCase().trim();

    const filtrados = clientesData.filter(c => {
        if (!termLower) return true;
        const nomeMatch = c.nome.toLowerCase().includes(termLower);
        const matriculaMatch = c.matricula ? c.matricula.toLowerCase().includes(termLower) : false;
        return nomeMatch || matriculaMatch;
    });

    dropdown.innerHTML = '';

    if (filtrados.length === 0) {
        dropdown.innerHTML = `
            <div class="cliente-dropdown-empty">
                Nenhum cliente encontrado
            </div>
        `;
    } else {
        filtrados.forEach(cliente => {
            const item = document.createElement('div');
            item.className = `cliente-dropdown-item ${cliente.id === clienteAtual.id ? 'selected' : ''}`;
            item.onclick = () => selecionarCliente(cliente);

            const isAssociado = cliente.is_associado;
            const matriculaStr = cliente.matricula ? `(${cliente.matricula})` : '';
            const badgeHtml = isAssociado ? `<span class="badge-opt-associado">✓ ASSOCIADO</span>` : '';

            item.innerHTML = `
                <div class="cliente-opt-info">
                    <span class="cliente-opt-nome">${cliente.nome} ${matriculaStr}</span>
                </div>
                ${badgeHtml}
            `;
            dropdown.appendChild(item);
        });
    }

    dropdown.style.display = 'block';
    lucide.createIcons();
}

/**
 * Seleciona um cliente da lista suspensa
 */
function selecionarCliente(cliente) {
    clienteAtual.id = cliente.id;
    
    const searchInput = document.getElementById('cliente-search-input');
    const btnLimpar = document.getElementById('btn-limpar-cliente');
    const dropdown = document.getElementById('cliente-dropdown-results');

    if (searchInput) {
        searchInput.value = cliente.id === 0 ? '' : cliente.nome;
    }

    if (btnLimpar) {
        btnLimpar.style.display = cliente.id === 0 ? 'none' : 'flex';
    }

    if (dropdown) {
        dropdown.style.display = 'none';
    }

    setAssociadoState(cliente.is_associado);
}

/**
 * Limpa a seleção do cliente
 */
function limparClienteSelecionado() {
    const clientePadrao = clientesData.find(c => c.id === 0) || { id: 0, is_associado: false };
    selecionarCliente(clientePadrao);
}


/**
 * Atualiza o estado visual da chave toggle, badge e recalcula os totais
 */
function setAssociadoState(isAssociado) {
    clienteAtual.associado = isAssociado;

    const toggleBtn = document.getElementById('client-toggle');
    const toggleLabel = document.getElementById('client-association-label');
    const badge = document.getElementById('badge-desconto');

    if (toggleBtn) {
        toggleBtn.checked = isAssociado;
    }

    if (toggleLabel) {
        toggleLabel.textContent = isAssociado ? "Cliente associado" : "Cliente não associado";
    }

    if (badge) {
        badge.style.display = isAssociado ? 'inline-flex' : 'none';
    }

    renderizarTotais();
}

// Fechar dropdown de clientes ao clicar fora do componente
document.addEventListener('click', (e) => {
    const combobox = document.querySelector('.cliente-combobox');
    const dropdown = document.getElementById('cliente-dropdown-results');
    if (dropdown && combobox && !combobox.contains(e.target)) {
        dropdown.style.display = 'none';
    }
});

/**
 * Renderiza os totais de Subtotal, Desconto e Total
 */
function renderizarTotais() {
    const subtotal = carrinho.reduce((acc, i) => acc + i.preco * i.quantidade, 0);

    const totalLiquido = carrinho.reduce((acc, i) => {
        const unitPrice = clienteAtual.associado ? (i.preco_associado !== undefined ? i.preco_associado : i.preco) : i.preco;
        return acc + unitPrice * i.quantidade;
    }, 0);

    const descontoValor = subtotal - totalLiquido;

    const fmt = v => 'R$ ' + v.toFixed(2).replace('.', ',');

    const elSubtotal = document.getElementById('val-subtotal');
    const elTotal = document.getElementById('val-total');
    const linhaDesc = document.getElementById('linha-desconto');
    const labelDesc = document.getElementById('label-desconto');
    const valDesc = document.getElementById('val-desconto');

    if (elSubtotal) elSubtotal.textContent = fmt(subtotal);
    if (elTotal) elTotal.textContent = fmt(totalLiquido);

    if (linhaDesc && labelDesc && valDesc) {
        if (clienteAtual.associado && descontoValor > 0) {
            linhaDesc.style.display = 'flex';
            labelDesc.textContent = `Desconto Associado`;
            valDesc.textContent = `− ${fmt(descontoValor)}`;
        } else {
            linhaDesc.style.display = 'none';
        }
    }
}

/**
 * Atualiza a interface completa do carrinho
 */
function updateCartUI() {
    const totais = document.getElementById('totais');

    if (carrinho.length === 0) {
        if (emptyCartState) emptyCartState.style.display = 'flex';
        if (cartItemsList) cartItemsList.style.display = 'none';
        if (totais) totais.style.display = 'none';
        
        if (checkoutBtn) {
            checkoutBtn.disabled = true;
            checkoutBtn.classList.remove('active');
        }
    } else {
        if (emptyCartState) emptyCartState.style.display = 'none';
        if (cartItemsList) cartItemsList.style.display = 'flex';
        if (totais) totais.style.display = 'block';

        if (cartItemsList) {
            cartItemsList.innerHTML = "";

            carrinho.forEach(item => {
                const unitPrice = clienteAtual.associado ? (item.preco_associado !== undefined ? item.preco_associado : item.preco) : item.preco;
                const subtotalItem = unitPrice * item.quantidade;
                const li = document.createElement('li');
                li.className = 'cart-item';
                
                li.innerHTML = `
                    <div class="cart-item-details">
                        <span class="cart-item-name">${item.nome}</span>
                        <span class="cart-item-price">R$ ${subtotalItem.toFixed(2).replace('.', ',')} (${item.quantidade}x R$ ${unitPrice.toFixed(2).replace('.', ',')})</span>
                    </div>
                    <div class="cart-item-actions">
                        <div class="quantity-control">
                            <button class="qty-btn" type="button" onclick="alterQtd(${item.produto_id}, -1)">
                                <i data-lucide="minus" style="width:12px;height:12px;"></i>
                            </button>
                            <span class="qty-val">${item.quantidade}</span>
                            <button class="qty-btn" type="button" onclick="alterQtd(${item.produto_id}, 1)">
                                <i data-lucide="plus" style="width:12px;height:12px;"></i>
                            </button>
                        </div>
                        <button class="remove-item-btn" type="button" onclick="removeFromCart(${item.produto_id})" title="Remover">
                            <i data-lucide="trash-2" style="width:14px;height:14px;"></i>
                        </button>
                    </div>
                `;
                
                cartItemsList.appendChild(li);
            });
        }

        if (checkoutBtn) {
            checkoutBtn.disabled = false;
            checkoutBtn.classList.add('active');
        }
    }

    renderizarTotais();
    lucide.createIcons();
}

/**
 * Serializa os itens do carrinho e envia o formulário de venda
 */
function finalizarVenda() {
    if (carrinho.length === 0) return;

    const inputCarrinho = document.getElementById('input-carrinho');
    const inputClienteId = document.getElementById('input-cliente-id');
    const inputObs = document.getElementById('input-obs');
    const obsInput = document.getElementById('obs-input');
    const formVenda = document.getElementById('form-venda');

    if (!inputCarrinho || !formVenda) return;

    inputCarrinho.value = JSON.stringify(carrinho.map(i => ({
        produto_id: i.produto_id,
        nome: i.nome,
        preco: i.preco,
        quantidade: i.quantidade
    })));

    if (inputClienteId) inputClienteId.value = clienteAtual.id;
    if (inputObs && obsInput) inputObs.value = obsInput.value;

    formVenda.submit();
}

/**
 * Event Listeners e inicialização
 */

if (searchInput) {
    searchInput.addEventListener('input', (e) => {
        currentSearch = e.target.value;
        pdvCurrentPage = 1;
        renderProducts();
    });
}

const searchBtn = document.getElementById('search-btn');
if (searchBtn) {
    searchBtn.addEventListener('click', () => {
        currentSearch = searchInput ? searchInput.value : "";
        pdvCurrentPage = 1;
        renderProducts();
    });
}

categoryButtons.forEach(button => {
    button.addEventListener('click', () => {
        categoryButtons.forEach(btn => btn.classList.remove('active'));
        button.classList.add('active');
        
        currentCategory = button.getAttribute('data-category');
        pdvCurrentPage = 1;
        renderProducts();
    });
});

document.addEventListener('DOMContentLoaded', () => {
    lucide.createIcons();
    renderProducts();
    updateCartUI();
});
