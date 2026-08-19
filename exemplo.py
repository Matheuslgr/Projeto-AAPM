aside class="carrinho-col">

        <div class="carrinho-header">🛒 Carrinho</div>

        <!-- Seleção de cliente -->
        <div class="cliente-section">
            <label>Cliente</label>
            <select class="cliente-select"
                    id="select-cliente"
                    onchange="atualizarCliente(this)">
                <option value="0" data-associado="false">
                    Sem identificação (sem desconto)
                </option>
                {% for c in clientes %}
                <option value="{{ c.id }}"
                        data-associado="{{ 'true' if c.is_associado else 'false' }}">
                    {{ c.nome }}
                    {% if c.matricula %}({{ c.matricula }}){% endif %}
                    {% if c.is_associado %} — ASSOCIADO{% endif %}
                </option>
                {% endfor %}
            </select>

            <!--
                Badge aparece via JS quando um associado é selecionado.
                desconto_associado vem do template (10.0)
            -->
            <div class="desconto-badge" id="badge-desconto" style="display:none">
                ✓ {{ desconto_associado|int }}% de desconto aplicado
            </div>
        </div>

        <!-- Lista de itens -->
        <div class="carrinho-itens" id="lista-carrinho">
            <div class="carrinho-vazio" id="msg-vazio">
                <span class="carrinho-vazio-icon">🛒</span>
                Clique nos produtos para adicionar
            </div>
        </div>

        <!-- Totais e finalização -->
        <div class="carrinho-footer">
            <div class="totais" id="totais" style="display:none">
                <div class="total-linha">
                    <span>Subtotal</span>
                    <span id="val-subtotal">R$ 0,00</span>
                </div>
                <div class="total-linha desconto" id="linha-desconto" style="display:none">
                    <span id="label-desconto">Desconto (0%)</span>
                    <span id="val-desconto">— R$ 0,00</span>
                </div>
                <div class="total-linha final">
                    <span>Total</span>
                    <span id="val-total">R$ 0,00</span>
                </div>
            </div>

            <textarea class="obs-input"
                      id="obs-input"
                      rows="2"
                      placeholder="Observação (opcional)..."></textarea>

            <!--
                O form envia:
                - carrinho_json: array serializado em JSON pelo JS
                - cliente_id: id do cliente selecionado (0 = balcão)
                - observacao: texto livre
            -->
            <form id="form-venda" action="/pdv/finalizar" method="post">
                <input type="hidden" name="carrinho_json" id="input-carrinho">
                <input type="hidden" name="cliente_id"   id="input-cliente-id" value="0">
                <input type="hidden" name="observacao"   id="input-obs">
                <button class="btn-finalizar"
                        id="btn-finalizar"
                        type="button"
                        disabled
                        onclick="finalizarVenda()">
                    Finalizar venda
                </button>
            </form>
        </div>
    </aside>
</div>

<script>
// ============================================================
// Estado do carrinho — array de objetos
// ============================================================
// Cada item: { produto_id, nome, preco, quantidade, estoque_max }
// ============================================================

let carrinho = [];
let clienteAtual = { id: 0, associado: false };
const DESCONTO_PCT = {{ desconto_associado }};  // vem do template

// ── Adicionar produto ao carrinho ────────────────────────────

function adicionarAoCarrinho(card) {
    const id       = parseInt(card.dataset.id);
    const nome     = card.dataset.nome;
    const preco    = parseFloat(card.dataset.preco);
    const estoque  = parseInt(card.dataset.estoque);

    const existente = carrinho.find(i => i.produto_id === id);

    if (existente) {
        // Produto já está no carrinho — aumenta a quantidade se tiver estoque
        if (existente.quantidade < existente.estoque_max) {
            existente.quantidade++;
        } else {
            alert(`Estoque máximo atingido: ${existente.estoque_max} unidade(s).`);
            return;
        }
    } else {
        // Produto novo no carrinho
        carrinho.push({ produto_id: id, nome, preco, quantidade: 1, estoque_max: estoque });
    }

    renderizarCarrinho();
}

// ── Alterar quantidade ────────────────────────────────────────

function alterarQtd(produtoId, delta) {
    const item = carrinho.find(i => i.produto_id === produtoId);
    if (!item) return;

    item.quantidade += delta;

    // Remove o item se a quantidade chegar a zero
    if (item.quantidade <= 0) {
        removerItem(produtoId);
        return;
    }

    // Limita pelo estoque disponível
    if (item.quantidade > item.estoque_max) {
        item.quantidade = item.estoque_max;
    }

    renderizarCarrinho();
}

function removerItem(produtoId) {
    carrinho = carrinho.filter(i => i.produto_id !== produtoId);
    renderizarCarrinho();
}

// ── Atualizar cliente selecionado ─────────────────────────────

function atualizarCliente(select) {
    const opt = select.options[select.selectedIndex];
    clienteAtual.id        = parseInt(opt.value);
    clienteAtual.associado = opt.dataset.associado === 'true';

    // Exibe ou esconde o badge de desconto
    const badge = document.getElementById('badge-desconto');
    badge.style.display = clienteAtual.associado ? 'inline-flex' : 'none';

    // Recalcula os totais com o novo desconto
    renderizarTotais();
}

// ── Renderizar lista do carrinho ──────────────────────────────

function renderizarCarrinho() {
    const lista    = document.getElementById('lista-carrinho');
    const vazio    = document.getElementById('msg-vazio');
    const totais   = document.getElementById('totais');
    const btnFinal = document.getElementById('btn-finalizar');

    if (carrinho.length === 0) {
        lista.innerHTML = '';
        lista.appendChild(vazio);
        vazio.style.display = 'flex';
        totais.style.display = 'none';
        btnFinal.disabled = true;
        return;
    }

    vazio.style.display = 'none';
    totais.style.display = 'block';
    btnFinal.disabled = false;

    lista.innerHTML = '';

    carrinho.forEach(item => {
        const subtotal = item.preco * item.quantidade;
        const div = document.createElement('div');
        div.className = 'item-carrinho';
        div.innerHTML = `
            <div style="flex:1">
                <div class="item-nome">${item.nome}</div>
                <div class="item-preco-unit">
                    R$ ${item.preco.toFixed(2).replace('.', ',')} / un.
                </div>
            </div>
            <div class="item-qty-ctrl">
                <button class="qty-btn"
                        onclick="alterarQtd(${item.produto_id}, -1)">−</button>
                <span class="qty-value">${item.quantidade}</span>
                <button class="qty-btn"
                        onclick="alterarQtd(${item.produto_id}, +1)">+</button>
            </div>
            <div class="item-subtotal">
                R$ ${subtotal.toFixed(2).replace('.', ',')}
            </div>
            <button class="item-remover"
                    onclick="removerItem(${item.produto_id})"
                    title="Remover">×</button>
        `;
        lista.appendChild(div);
    });

    renderizarTotais();
}

// ── Calcular e exibir totais ──────────────────────────────────

function renderizarTotais() {
    const subtotal = carrinho.reduce(
        (acc, i) => acc + i.preco * i.quantidade, 0
    );

    const descontoValor  = clienteAtual.associado
        ? subtotal * (DESCONTO_PCT / 100)
        : 0;
    const total = subtotal - descontoValor;

    const fmt = v => 'R$ ' + v.toFixed(2).replace('.', ',');

    document.getElementById('val-subtotal').textContent = fmt(subtotal);
    document.getElementById('val-total').textContent    = fmt(total);

    const linhaDesc  = document.getElementById('linha-desconto');
    const labelDesc  = document.getElementById('label-desconto');
    const valDesc    = document.getElementById('val-desconto');

    if (clienteAtual.associado && descontoValor > 0) {
        linhaDesc.style.display  = 'flex';
        labelDesc.textContent    = `Desconto (${DESCONTO_PCT}%)`;
        valDesc.textContent      = `− ${fmt(descontoValor)}`;
    } else {
        linhaDesc.style.display = 'none';
    }
}

// ── Submeter a venda ──────────────────────────────────────────

function finalizarVenda() {
    if (carrinho.length === 0) return;

    // Serializa o carrinho para o campo oculto
    document.getElementById('input-carrinho').value =
        JSON.stringify(carrinho.map(i => ({
            produto_id: i.produto_id,
            nome:       i.nome,
            preco:      i.preco,
            quantidade: i.quantidade,
        })));

    document.getElementById('input-cliente-id').value = clienteAtual.id;
    document.getElementById('input-obs').value =
        document.getElementById('obs-input').value;

    document.getElementById('form-venda').submit();
}

// ── Filtro de busca de produtos ───────────────────────────────

document.getElementById('busca-produto').addEventListener('input', function () {
    const termo = this.value.toLowerCase().trim();
    document.querySelectorAll('.produto-card').forEach(card => {
        const nome = card.dataset.nomeLower || '';
        card.style.display = nome.includes(termo) ? '' : 'none';
    });
});
</script>
</body>
</html>