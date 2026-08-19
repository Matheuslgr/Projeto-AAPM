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

// Filtros Atuais
let currentSearch = "";
let currentCategory = "all";

/**
 * Renderiza o grid de produtos com base nos filtros atuais
 */
function renderProducts() {
    if (!productsGrid) return;
    productsGrid.innerHTML = "";
    
    const filteredProducts = productsData.filter(product => {
        const matchesSearch = product.name.toLowerCase().includes(currentSearch.toLowerCase());
        const matchesCategory = currentCategory === "all" || product.category === currentCategory;
        return matchesSearch && matchesCategory;
    });

    if (filteredProducts.length === 0) {
        productsGrid.innerHTML = `
            <div style="grid-column: 1/-1; text-align: center; color: var(--text-muted); padding: 40px;">
                Nenhum produto encontrado.
            </div>
        `;
        return;
    }

    filteredProducts.forEach(product => {
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

/**
 * Atualiza cliente selecionado e ativa/desativa automaticamente a chave toggle
 */
function atualizarCliente(select) {
    const opt = select.options[select.selectedIndex];
    clienteAtual.id = parseInt(opt.value);
    const isAssociado = opt.dataset.associado === 'true';

    setAssociadoState(isAssociado);
}

/**
 * Evento acionado ao alternar manualmente o switch toggle
 */
function toggleAssociadoManual(checkbox) {
    setAssociadoState(checkbox.checked);
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

/**
 * Renderiza os totais de Subtotal, Desconto e Total
 */
function renderizarTotais() {
    const subtotal = carrinho.reduce((acc, i) => acc + i.preco * i.quantidade, 0);

    const pctDesconto = typeof DESCONTO_PCT !== 'undefined' ? DESCONTO_PCT : 10.0;
    const descontoValor = clienteAtual.associado ? subtotal * (pctDesconto / 100) : 0;
    const total = subtotal - descontoValor;

    const fmt = v => 'R$ ' + v.toFixed(2).replace('.', ',');

    const elSubtotal = document.getElementById('val-subtotal');
    const elTotal = document.getElementById('val-total');
    const linhaDesc = document.getElementById('linha-desconto');
    const labelDesc = document.getElementById('label-desconto');
    const valDesc = document.getElementById('val-desconto');

    if (elSubtotal) elSubtotal.textContent = fmt(subtotal);
    if (elTotal) elTotal.textContent = fmt(total);

    if (linhaDesc && labelDesc && valDesc) {
        if (clienteAtual.associado && descontoValor > 0) {
            linhaDesc.style.display = 'flex';
            labelDesc.textContent = `Desconto (${pctDesconto}%)`;
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
                const subtotalItem = item.preco * item.quantidade;
                const li = document.createElement('li');
                li.className = 'cart-item';
                
                li.innerHTML = `
                    <div class="cart-item-details">
                        <span class="cart-item-name">${item.nome}</span>
                        <span class="cart-item-price">R$ ${subtotalItem.toFixed(2).replace('.', ',')} (${item.quantidade}x R$ ${item.preco.toFixed(2).replace('.', ',')})</span>
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
        renderProducts();
    });
}

const searchBtn = document.getElementById('search-btn');
if (searchBtn) {
    searchBtn.addEventListener('click', () => {
        currentSearch = searchInput ? searchInput.value : "";
        renderProducts();
    });
}

categoryButtons.forEach(button => {
    button.addEventListener('click', () => {
        categoryButtons.forEach(btn => btn.classList.remove('active'));
        button.classList.add('active');
        
        currentCategory = button.getAttribute('data-category');
        renderProducts();
    });
});

document.addEventListener('DOMContentLoaded', () => {
    lucide.createIcons();
    renderProducts();
    updateCartUI();
});
