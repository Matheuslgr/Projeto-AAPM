// ============================================================================
// HOME.JS - Lógica do PDV, Carrinho, Desconto Manual e Pagamentos Múltiplos
// ============================================================================

// Carrega os dados passados pelo backend no elemento #pdv-data
const pdvDataElement = document.getElementById('pdv-data');
const pdvData = pdvDataElement ? JSON.parse(pdvDataElement.textContent) : { desconto_associado: 10.0, produtos: [] };

const DESCONTO_PCT = pdvData.desconto_associado || 10.0;
const productsData = pdvData.produtos || [];
const clientesData = pdvData.clientes || [
    { id: 0, nome: "Sem identificação (sem desconto)", matricula: "", is_associado: false }
];

// Estado Principal
let carrinho = [];
let clienteAtual = { id: 0, associado: false };

// Estado do Desconto Manual
let descontoManual = 0.0;
let descontoTipo = "reais"; // "reais" ou "porcentagem"

// Estado das Formas de Pagamento
let modoDuasFormas = false;

// 1 Forma de Pagamento
let formaUnica = "DINHEIRO"; // 'DINHEIRO', 'CARTAO', 'PIX'
let cartaoSubtipo = "DEBITO"; // 'DEBITO', 'CREDITO'
let dinheiroRecebido = 0.0;
let dinheiroRecebidoManual = false; // flag se o operador já digitou valor

// 2 Formas de Pagamento
let duploForma1 = "CARTAO_DEBITO";
let duploValor1 = 0.0;
let duploRecebido1 = 0.0;

let duploForma2 = "DINHEIRO";
let duploValor2 = 0.0;
let duploRecebido2 = 0.0;

// Elementos do DOM
const productsGrid = document.getElementById('products-grid');
const searchInput = document.getElementById('search-input');
const categoryButtons = document.querySelectorAll('.category-btn');
const emptyCartState = document.getElementById('empty-cart-state');
const cartItemsList = document.getElementById('cart-items-list');
const cartCountBadge = document.getElementById('cart-count-badge');
const checkoutBtn = document.getElementById('checkout-btn');

// Filtros e Paginação do Grid PDV
let currentSearch = "";
let currentCategory = "all";
let pdvCurrentPage = 1;
const PDV_ITEMS_PER_PAGE = 14;

/**
 * Formata um número como moeda brasileira (R$ 0,00)
 */
function formatMoeda(valor) {
    if (isNaN(valor) || valor === null || valor === undefined) valor = 0;
    return 'R$ ' + Number(valor).toFixed(2).replace('.', ',');
}

/**
 * Renderiza o grid de produtos com base nos filtros e paginação
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

    if (pdvCurrentPage > totalPages) pdvCurrentPage = totalPages;
    if (pdvCurrentPage < 1) pdvCurrentPage = 1;

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
                <span class="product-price">${formatMoeda(product.price)}</span>
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
 * Paginação do PDV
 */
function changePdvPage(newPage) {
    pdvCurrentPage = newPage;
    renderProducts();
    const pdvSection = document.querySelector('.pdv-section');
    if (pdvSection) {
        pdvSection.scrollTo({ top: 0, behavior: 'smooth' });
    }
}

function renderPdvPagination(totalItems, totalPages) {
    const paginationEl = document.getElementById('pdv-pagination');
    if (!paginationEl) return;

    if (totalItems <= PDV_ITEMS_PER_PAGE) {
        paginationEl.style.display = 'none';
        paginationEl.innerHTML = '';
        return;
    }

    paginationEl.style.display = 'flex';

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
            Página <strong>${pdvCurrentPage}</strong> de <strong>${totalPages}</strong> &bull; Total: <strong>${totalItems}</strong> produtos
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
            preco_associado: (product.preco_associado !== undefined && product.preco_associado !== null) ? product.preco_associado : product.price,
            quantidade: 1,
            estoque_max: product.estoque_max || 9999
        });
    }

    dinheiroRecebidoManual = false;
    updateCartUI();
}

/**
 * Altera quantidade no carrinho
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

    dinheiroRecebidoManual = false;
    updateCartUI();
}

/**
 * Remove do carrinho
 */
function removeFromCart(productId) {
    carrinho = carrinho.filter(i => i.produto_id !== productId);
    dinheiroRecebidoManual = false;
    updateCartUI();
}

/**
 * Cálculos do carrinho (totais, descontos e validações)
 */
function calcularTotais() {
    const subtotalBruto = carrinho.reduce((acc, i) => acc + (i.preco * i.quantidade), 0);

    const subtotalBase = carrinho.reduce((acc, i) => {
        const unitPrice = clienteAtual.associado ? i.preco_associado : i.preco;
        return acc + (unitPrice * i.quantidade);
    }, 0);

    const descontoClube = subtotalBruto - subtotalBase;

    let descontoManualValor = 0.0;
    let descontoInvalido = false;

    if (descontoManual > 0) {
        if (descontoTipo === 'porcentagem') {
            if (descontoManual > 100) {
                descontoInvalido = true;
                descontoManualValor = subtotalBase;
            } else {
                descontoManualValor = (subtotalBase * (descontoManual / 100));
            }
        } else {
            if (descontoManual > subtotalBase) {
                descontoInvalido = true;
                descontoManualValor = subtotalBase;
            } else {
                descontoManualValor = descontoManual;
            }
        }
    }

    descontoManualValor = Math.round(descontoManualValor * 100) / 100;

    let totalLiquido = Math.max(0, subtotalBase - (descontoInvalido ? 0 : descontoManualValor));
    totalLiquido = Math.round(totalLiquido * 100) / 100;

    return {
        subtotalBruto,
        subtotalBase,
        descontoClube,
        descontoManualValor,
        totalLiquido,
        descontoInvalido
    };
}

/**
 * Atualiza o Desconto Manual pelo input
 */
function atualizarDescontoManual(val) {
    const num = parseFloat(val);
    descontoManual = (!isNaN(num) && num >= 0) ? num : 0.0;
    updateCartUI(false);
}

/**
 * Alterna entre desconto em R$ ou %
 */
function mudarTipoDesconto(tipo) {
    descontoTipo = tipo;
    
    const btnReais = document.getElementById('btn-tipo-reais');
    const btnPct = document.getElementById('btn-tipo-pct');
    const labelTipo = document.getElementById('label-tipo-desconto');
    const inputDesc = document.getElementById('input-desconto');

    if (btnReais) btnReais.classList.toggle('active', tipo === 'reais');
    if (btnPct) btnPct.classList.toggle('active', tipo === 'porcentagem');
    if (labelTipo) labelTipo.textContent = tipo === 'reais' ? 'Desconto (R$)' : 'Desconto (%)';

    if (inputDesc) {
        inputDesc.placeholder = tipo === 'reais' ? '0,00' : '0%';
        inputDesc.max = tipo === 'porcentagem' ? '100' : '';
    }

    updateCartUI(false);
}

/**
 * Alterna entre 1 Forma ou 2 Formas de Pagamento
 */
function toggleModoDuasFormas(checked) {
    modoDuasFormas = checked;

    const boxUnico = document.getElementById('modo-pagamento-unico');
    const boxDuplo = document.getElementById('modo-pagamento-duplo');

    if (boxUnico) boxUnico.style.display = checked ? 'none' : 'block';
    if (boxDuplo) boxDuplo.style.display = checked ? 'block' : 'none';

    if (checked) {
        // Inicializa divisão 50% ou automática no modo 2 formas
        const totais = calcularTotais();
        if (totais.totalLiquido > 0) {
            duploValor1 = Math.round((totais.totalLiquido / 2) * 100) / 100;
            duploValor2 = Math.round((totais.totalLiquido - duploValor1) * 100) / 100;
            
            const inpVal1 = document.getElementById('duplo-valor-1');
            const inpVal2 = document.getElementById('duplo-valor-2');
            if (inpVal1) inpVal1.value = duploValor1.toFixed(2);
            if (inpVal2) inpVal2.value = duploValor2.toFixed(2);
        }
        atualizarPagamentoDuplo();
    } else {
        updateCartUI(false);
    }
}

/**
 * Seleciona a Forma de Pagamento no Modo Único
 */
function selecionarFormaUnica(forma) {
    formaUnica = forma;

    document.querySelectorAll('.payment-tab').forEach(t => t.classList.remove('active'));
    
    const tabDinheiro = document.getElementById('tab-dinheiro');
    const tabCartao = document.getElementById('tab-cartao');
    const tabPix = document.getElementById('tab-pix');

    if (forma === 'DINHEIRO' && tabDinheiro) tabDinheiro.classList.add('active');
    if (forma === 'CARTAO' && tabCartao) tabCartao.classList.add('active');
    if (forma === 'PIX' && tabPix) tabPix.classList.add('active');

    const detDinheiro = document.getElementById('detalhes-dinheiro');
    const detCartao = document.getElementById('detalhes-cartao');
    const detPix = document.getElementById('detalhes-pix');

    if (detDinheiro) detDinheiro.style.display = forma === 'DINHEIRO' ? 'block' : 'none';
    if (detCartao) detCartao.style.display = forma === 'CARTAO' ? 'block' : 'none';
    if (detPix) detPix.style.display = forma === 'PIX' ? 'block' : 'none';

    validarVenda();
}

/**
 * Seleciona Subtipo do Cartão (Débito ou Crédito)
 */
function selecionarSubtipoCartao(subtipo) {
    cartaoSubtipo = subtipo;
    const btnDeb = document.getElementById('subtab-debito');
    const btnCred = document.getElementById('subtab-credito');

    if (btnDeb) btnDeb.classList.toggle('active', subtipo === 'DEBITO');
    if (btnCred) btnCred.classList.toggle('active', subtipo === 'CREDITO');

    validarVenda();
}

/**
 * Atualiza o valor recebido em dinheiro pelo operador
 */
function atualizarDinheiroRecebido(val) {
    const num = parseFloat(val);
    dinheiroRecebido = (!isNaN(num) && num >= 0) ? num : 0.0;
    dinheiroRecebidoManual = true;

    const totais = calcularTotais();
    renderStatusDinheiro(totais.totalLiquido, dinheiroRecebido);
    validarVenda();
}

/**
 * Preenche o valor recebido ao clicar em um botão de cédula rápida
 */
function setDinheiroRapido(valor) {
    dinheiroRecebido = valor;
    dinheiroRecebidoManual = true;

    const inp = document.getElementById('input-recebido');
    if (inp) inp.value = valor.toFixed(2);

    const totais = calcularTotais();
    renderStatusDinheiro(totais.totalLiquido, dinheiroRecebido);
    validarVenda();
}

/**
 * Renderiza os botões de valores rápidos de cédula
 */
function renderQuickCashButtons(totalLiquido) {
    const container = document.getElementById('quick-cash-buttons');
    if (!container) return;

    if (totalLiquido <= 0) {
        container.innerHTML = '';
        return;
    }

    const valoresSugeridos = new Set();
    // Valor exato
    valoresSugeridos.add(totalLiquido);

    // Próximo múltiplo de 5 ou 10
    const prox5 = Math.ceil(totalLiquido / 5) * 5;
    if (prox5 > totalLiquido) valoresSugeridos.add(prox5);

    const prox10 = Math.ceil(totalLiquido / 10) * 10;
    if (prox10 > totalLiquido && prox10 !== prox5) valoresSugeridos.add(prox10);

    // Cédulas comuns (50, 100, 200)
    [50, 100, 200].forEach(cedula => {
        if (cedula >= totalLiquido) valoresSugeridos.add(cedula);
    });

    const ordenados = Array.from(valoresSugeridos).sort((a, b) => a - b).slice(0, 5);

    container.innerHTML = ordenados.map(v => `
        <button type="button" class="quick-cash-btn" onclick="setDinheiroRapido(${v})">
            ${formatMoeda(v)}
        </button>
    `).join('');
}

/**
 * Atualiza o box "FALTAM" ou "TROCO" no pagamento em dinheiro
 */
function renderStatusDinheiro(totalLiquido, recebido) {
    const labelStatus = document.getElementById('label-status-dinheiro');
    const valStatus = document.getElementById('val-status-dinheiro');
    const boxStatus = document.getElementById('box-status-dinheiro');

    if (!labelStatus || !valStatus || !boxStatus) return;

    const dif = recebido - totalLiquido;

    if (dif >= 0) {
        labelStatus.textContent = 'TROCO';
        valStatus.textContent = formatMoeda(dif);
        boxStatus.className = 'campo-status-dinheiro troco-verde';
    } else {
        labelStatus.textContent = 'FALTAM';
        valStatus.textContent = formatMoeda(Math.abs(dif));
        boxStatus.className = 'campo-status-dinheiro falta-vermelha';
    }
}

/**
 * Atualiza o cálculo do modo 2 formas de pagamento
 */
function atualizarPagamentoDuplo(alteradoPor) {
    const select1 = document.getElementById('duplo-forma-1');
    const select2 = document.getElementById('duplo-forma-2');
    const inpVal1 = document.getElementById('duplo-valor-1');
    const inpVal2 = document.getElementById('duplo-valor-2');
    const boxExtra1 = document.getElementById('duplo-dinheiro-extra-1');
    const boxExtra2 = document.getElementById('duplo-dinheiro-extra-2');

    if (select1) duploForma1 = select1.value;
    if (select2) duploForma2 = select2.value;

    const totais = calcularTotais();
    const total = totais.totalLiquido;

    if (alteradoPor === '1' && inpVal1) {
        const v1 = parseFloat(inpVal1.value) || 0.0;
        duploValor1 = v1;
        duploValor2 = Math.max(0, Math.round((total - v1) * 100) / 100);
        if (inpVal2) inpVal2.value = duploValor2.toFixed(2);
    } else if (alteradoPor === '2' && inpVal2) {
        const v2 = parseFloat(inpVal2.value) || 0.0;
        duploValor2 = v2;
        duploValor1 = Math.max(0, Math.round((total - v2) * 100) / 100);
        if (inpVal1) inpVal1.value = duploValor1.toFixed(2);
    } else {
        if (inpVal1) duploValor1 = parseFloat(inpVal1.value) || 0.0;
        if (inpVal2) duploValor2 = parseFloat(inpVal2.value) || 0.0;
    }

    // Toggle campos extras se for dinheiro
    if (boxExtra1) boxExtra1.style.display = duploForma1 === 'DINHEIRO' ? 'block' : 'none';
    if (boxExtra2) boxExtra2.style.display = duploForma2 === 'DINHEIRO' ? 'block' : 'none';

    if (duploForma1 === 'DINHEIRO') atualizarDinheiroDuplo(1);
    if (duploForma2 === 'DINHEIRO') atualizarDinheiroDuplo(2);

    renderResumoDuplo(total);
    validarVenda();
}

/**
 * Atualiza o dinheiro recebido na forma dupla
 */
function atualizarDinheiroDuplo(index) {
    const total = index === 1 ? duploValor1 : duploValor2;
    const inp = document.getElementById(`duplo-recebido-${index}`);
    const rec = parseFloat(inp ? inp.value : 0) || 0;
    
    if (index === 1) duploRecebido1 = rec;
    if (index === 2) duploRecebido2 = rec;

    const labelStatus = document.getElementById(`duplo-label-status-${index}`);
    const valStatus = document.getElementById(`duplo-val-status-${index}`);
    const boxStatus = document.getElementById(`duplo-status-${index}`);

    if (!labelStatus || !valStatus || !boxStatus) return;

    const dif = rec - total;
    if (dif >= 0) {
        labelStatus.textContent = 'TROCO';
        valStatus.textContent = formatMoeda(dif);
        boxStatus.className = 'campo-status-dinheiro compact troco-verde';
    } else {
        labelStatus.textContent = 'FALTAM';
        valStatus.textContent = formatMoeda(Math.abs(dif));
        boxStatus.className = 'campo-status-dinheiro compact falta-vermelha';
    }

    validarVenda();
}

/**
 * Renderiza o resumo de validação das 2 formas de pagamento
 */
function renderResumoDuplo(totalLiquido) {
    const resumoEl = document.getElementById('duplo-resumo-validacao');
    if (!resumoEl) return;

    const soma = Math.round((duploValor1 + duploValor2) * 100) / 100;
    const dif = Math.round((totalLiquido - soma) * 100) / 100;

    if (Math.abs(dif) < 0.01 && totalLiquido > 0) {
        resumoEl.innerHTML = `
            <div class="status-badge-sucesso">
                <i data-lucide="check-circle" style="width:14px;height:14px;"></i>
                <span>Soma fecha o total exatamente: <strong>${formatMoeda(soma)}</strong></span>
            </div>
        `;
    } else if (dif > 0) {
        resumoEl.innerHTML = `
            <div class="status-badge-erro">
                <i data-lucide="alert-circle" style="width:14px;height:14px;"></i>
                <span>Soma das parcelas: <strong>${formatMoeda(soma)}</strong> &bull; Faltam <strong>${formatMoeda(dif)}</strong></span>
            </div>
        `;
    } else {
        resumoEl.innerHTML = `
            <div class="status-badge-erro">
                <i data-lucide="alert-circle" style="width:14px;height:14px;"></i>
                <span>Soma das parcelas: <strong>${formatMoeda(soma)}</strong> &bull; Excede o total em <strong>${formatMoeda(Math.abs(dif))}</strong></span>
            </div>
        `;
    }
    lucide.createIcons();
}

/**
 * Validação geral e habilitação do botão de finalizar venda
 */
function validarVenda() {
    const totais = calcularTotais();
    const btn = document.getElementById('checkout-btn');
    if (!btn) return;

    // Regra 1: Carrinho não pode estar vazio
    if (carrinho.length === 0) {
        btn.disabled = true;
        btn.classList.remove('active');
        return;
    }

    // Regra 2: Desconto não pode ser maior que o subtotal
    if (totais.descontoInvalido) {
        btn.disabled = true;
        btn.classList.remove('active');
        return;
    }

    // Regra 3: Validações de Pagamento
    if (!modoDuasFormas) {
        // Modo 1 Forma
        if (formaUnica === 'DINHEIRO') {
            // Se dinheiro, o recebido deve cobrir o total
            if (dinheiroRecebido < totais.totalLiquido) {
                btn.disabled = true;
                btn.classList.remove('active');
                return;
            }
        }
    } else {
        // Modo 2 Formas
        const soma = Math.round((duploValor1 + duploValor2) * 100) / 100;
        if (Math.abs(soma - totais.totalLiquido) > 0.01 || duploValor1 <= 0 || duploValor2 <= 0) {
            btn.disabled = true;
            btn.classList.remove('active');
            return;
        }

        // Se forma 1 for dinheiro
        if (duploForma1 === 'DINHEIRO' && duploRecebido1 < duploValor1) {
            btn.disabled = true;
            btn.classList.remove('active');
            return;
        }

        // Se forma 2 for dinheiro
        if (duploForma2 === 'DINHEIRO' && duploRecebido2 < duploValor2) {
            btn.disabled = true;
            btn.classList.remove('active');
            return;
        }
    }

    // Se passou em todas as regras: Habilitar botão laranja
    btn.disabled = false;
    btn.classList.add('active');
}

/**
 * Atualiza toda a Interface do Carrinho
 */
function updateCartUI(resetDinheiro = true) {
    const totais = calcularTotais();
    const totalItens = carrinho.reduce((acc, i) => acc + i.quantidade, 0);

    // 1. Atualizar Badge do Carrinho
    if (cartCountBadge) {
        cartCountBadge.textContent = totalItens;
        cartCountBadge.style.display = totalItens > 0 ? 'inline-flex' : 'none';
    }

    const totaisBloco = document.getElementById('totais');
    const pagBloco = document.getElementById('pagamento-container');

    if (carrinho.length === 0) {
        if (emptyCartState) emptyCartState.style.display = 'flex';
        if (cartItemsList) {
            cartItemsList.style.display = 'none';
            cartItemsList.innerHTML = '';
        }
        if (totaisBloco) totaisBloco.style.display = 'none';
        if (pagBloco) pagBloco.style.display = 'none';
        
        validarVenda();
        return;
    }

    if (emptyCartState) emptyCartState.style.display = 'none';
    if (cartItemsList) cartItemsList.style.display = 'flex';
    if (totaisBloco) totaisBloco.style.display = 'block';
    if (pagBloco) pagBloco.style.display = 'block';

    // 2. Renderizar Lista de Itens do Carrinho (Design idêntico ao protótipo)
    if (cartItemsList) {
        cartItemsList.innerHTML = "";
        carrinho.forEach(item => {
            const unitPrice = clienteAtual.associado ? item.preco_associado : item.preco;
            const subtotalItem = unitPrice * item.quantidade;
            const li = document.createElement('li');
            li.className = 'cart-item-card';

            const restante = item.estoque_max - item.quantidade;

            li.innerHTML = `
                <div class="cart-item-top">
                    <span class="cart-item-title" title="${item.nome}">${item.nome}</span>
                    <div class="cart-item-controls">
                        <button class="cart-qty-btn" type="button" onclick="alterQtd(${item.produto_id}, -1)">
                            <i data-lucide="minus"></i>
                        </button>
                        <span class="cart-qty-num">${item.quantidade}</span>
                        <button class="cart-qty-btn ${restante <= 0 ? 'disabled' : ''}" type="button" 
                                onclick="alterQtd(${item.produto_id}, 1)" ${restante <= 0 ? 'disabled' : ''}>
                            <i data-lucide="plus"></i>
                        </button>
                        <button class="cart-del-btn" type="button" onclick="removeFromCart(${item.produto_id})" title="Remover produto">
                            <i data-lucide="trash-2"></i>
                        </button>
                    </div>
                </div>
                <div class="cart-item-bottom">
                    <span class="cart-item-calc">
                        ${formatMoeda(unitPrice)} &times; ${item.quantidade} = <strong>${formatMoeda(subtotalItem)}</strong>
                    </span>
                </div>
            `;
            cartItemsList.appendChild(li);
        });
    }

    // 3. Renderizar Totais e Desconto
    const elSubtotalOriginal = document.getElementById('linha-subtotal-original');
    const elSubtotalVal = document.getElementById('val-subtotal');
    const elTotal = document.getElementById('val-total');
    const alertaDescErro = document.getElementById('desconto-alerta-erro');
    const btnTotalTxt = document.getElementById('btn-total-txt');

    if (elSubtotalOriginal && elSubtotalVal) {
        if (totais.descontoClube > 0 || totais.descontoManualValor > 0) {
            elSubtotalOriginal.style.display = 'flex';
            elSubtotalVal.textContent = formatMoeda(totais.subtotalBruto);
        } else {
            elSubtotalOriginal.style.display = 'none';
        }
    }

    if (alertaDescErro) {
        alertaDescErro.style.display = totais.descontoInvalido ? 'block' : 'none';
    }

    if (elTotal) elTotal.textContent = formatMoeda(totais.totalLiquido);
    if (btnTotalTxt) btnTotalTxt.textContent = formatMoeda(totais.totalLiquido);

    // 4. Atualizar Valores de Pagamento
    if (!dinheiroRecebidoManual && resetDinheiro) {
        dinheiroRecebido = 0.0;
        const inpRec = document.getElementById('input-recebido');
        if (inpRec) inpRec.value = '0.00';
    }

    renderStatusDinheiro(totais.totalLiquido, dinheiroRecebido);
    renderQuickCashButtons(totais.totalLiquido);

    if (modoDuasFormas) {
        atualizarPagamentoDuplo();
    }

    validarVenda();
    lucide.createIcons();
}

/**
 * Serializa os itens e pagamentos e envia o formulário de venda
 */
function finalizarVenda() {
    if (carrinho.length === 0) return;

    const totais = calcularTotais();
    if (totais.descontoInvalido) {
        alert("O desconto informado não pode ser maior que o subtotal da venda.");
        return;
    }

    // Montar o array de pagamentos
    let pagamentosArray = [];

    if (!modoDuasFormas) {
        let formaFinal = formaUnica;
        if (formaUnica === 'CARTAO') {
            formaFinal = cartaoSubtipo === 'CREDITO' ? 'CARTAO_CREDITO' : 'CARTAO_DEBITO';
        }

        let troco = 0.0;
        let recebido = null;
        if (formaFinal === 'DINHEIRO') {
            recebido = dinheiroRecebido;
            troco = Math.max(0, Math.round((recebido - totais.totalLiquido) * 100) / 100);
        }

        pagamentosArray.push({
            forma_pagamento: formaFinal,
            valor: totais.totalLiquido,
            valor_recebido: recebido,
            troco: troco
        });
    } else {
        let troco1 = 0.0;
        let rec1 = null;
        if (duploForma1 === 'DINHEIRO') {
            rec1 = duploRecebido1;
            troco1 = Math.max(0, Math.round((rec1 - duploValor1) * 100) / 100);
        }

        let troco2 = 0.0;
        let rec2 = null;
        if (duploForma2 === 'DINHEIRO') {
            rec2 = duploRecebido2;
            troco2 = Math.max(0, Math.round((rec2 - duploValor2) * 100) / 100);
        }

        pagamentosArray.push({
            forma_pagamento: duploForma1,
            valor: duploValor1,
            valor_recebido: rec1,
            troco: troco1
        });

        pagamentosArray.push({
            forma_pagamento: duploForma2,
            valor: duploValor2,
            valor_recebido: rec2,
            troco: troco2
        });
    }

    // Preencher campos hidden
    const inputCarrinho = document.getElementById('input-carrinho');
    const inputClienteId = document.getElementById('input-cliente-id');
    const inputObs = document.getElementById('input-obs');
    const inputDescManual = document.getElementById('input-desconto-manual');
    const inputDescTipo = document.getElementById('input-desconto-tipo');
    const inputPagamentos = document.getElementById('input-pagamentos');
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
    if (inputDescManual) inputDescManual.value = descontoManual;
    if (inputDescTipo) inputDescTipo.value = descontoTipo;
    if (inputPagamentos) inputPagamentos.value = JSON.stringify(pagamentosArray);

    // Efeito de loading no botão
    const checkoutBtn = document.getElementById('checkout-btn');
    if (checkoutBtn) {
        checkoutBtn.disabled = true;
        checkoutBtn.innerHTML = `
            <i data-lucide="loader" class="btn-spinner"></i>
            <span>Processando venda...</span>
        `;
        lucide.createIcons();
    }

    formVenda.submit();
}

/**
 * Dropdown e Autocomplete de Clientes
 */
function abrirDropdownClientes() {
    const input = document.getElementById('cliente-search-input');
    filtrarClientes(input ? input.value : '');
}

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
            const badgeHtml = isAssociado ? `<span class="badge-opt-associado">✓ CLUBE MARTPaper</span>` : '';

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

function selecionarCliente(cliente) {
    clienteAtual.id = cliente.id;
    
    const input = document.getElementById('cliente-search-input');
    const btnLimpar = document.getElementById('btn-limpar-cliente');
    const dropdown = document.getElementById('cliente-dropdown-results');

    if (input) input.value = cliente.id === 0 ? '' : cliente.nome;
    if (btnLimpar) btnLimpar.style.display = cliente.id === 0 ? 'none' : 'flex';
    if (dropdown) dropdown.style.display = 'none';

    setAssociadoState(cliente.is_associado);
}

function limparClienteSelecionado() {
    const clientePadrao = clientesData.find(c => c.id === 0) || { id: 0, is_associado: false };
    selecionarCliente(clientePadrao);
}

function setAssociadoState(isAssociado) {
    clienteAtual.associado = isAssociado;

    const toggleBtn = document.getElementById('client-toggle');
    const toggleLabel = document.getElementById('client-association-label');
    const badge = document.getElementById('badge-desconto');

    if (toggleBtn) toggleBtn.checked = isAssociado;
    if (toggleLabel) toggleLabel.textContent = isAssociado ? "Cliente Clube MARTPaper" : "Cliente não associado";
    if (badge) badge.style.display = isAssociado ? 'inline-flex' : 'none';

    updateCartUI();
}

document.addEventListener('click', (e) => {
    const combobox = document.querySelector('.cliente-combobox');
    const dropdown = document.getElementById('cliente-dropdown-results');
    if (dropdown && combobox && !combobox.contains(e.target)) {
        dropdown.style.display = 'none';
    }
});

// Event Listeners da barra de busca e categorias
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

// Inicialização da tela
document.addEventListener('DOMContentLoaded', () => {
    lucide.createIcons();
    renderProducts();
    updateCartUI();
});
