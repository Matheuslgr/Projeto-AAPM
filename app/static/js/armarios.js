/* ==========================================================================
   AGENDAMENTO DE ARMÁRIOS — JS (Interactive Modals, Toasts & Confirmation)
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
    // Referências do DOM
    const searchInput = document.getElementById('searchInput');
    const filterBtns = document.querySelectorAll('.filter-btn');
    const armariosGrid = document.getElementById('armariosGrid');

    const totalStatEl = document.getElementById('totalStat');
    const disponiveisStatEl = document.getElementById('disponiveisStat');
    const ocupadosStatEl = document.getElementById('ocupadosStat');

    // Modais
    const modalNovoArmario = document.getElementById('modalNovoArmario');
    const modalArmarioDetails = document.getElementById('modalArmarioDetails');
    const modalConfirmacao = document.getElementById('modalConfirmacao');
    const toastContainer = document.getElementById('toastContainer');

    // Botões de Abertura/Fechamento
    const btnAbrirNovoArmario = document.getElementById('btnAbrirNovoArmario');
    const modalCloseBtns = document.querySelectorAll('.modal-close, [data-modal-close]');

    // Formulários
    const formNovoArmario = document.getElementById('formNovoArmario');

    // Estado local de filtros
    let filtroAtual = 'todos';
    let searchTimeout = null;
    let confirmResolver = null;

    // Inicializar ícones do Lucide
    if (window.lucide) {
        window.lucide.createIcons();
    }

    // --------------------------------------------------------------------------
    // SYSTEM: TOAST NOTIFICATIONS (Substitui os alerts nativos)
    // --------------------------------------------------------------------------
    function mostrarToast(mensagem, tipo = 'error') {
        if (!toastContainer) return;

        const toast = document.createElement('div');
        toast.className = `toast toast-${tipo}`;

        let iconName = 'alert-circle';
        if (tipo === 'success') iconName = 'check-circle-2';
        if (tipo === 'warning') iconName = 'alert-triangle';

        toast.innerHTML = `
            <div class="toast-icon">
                <i data-lucide="${iconName}" style="width: 20px; height: 20px;"></i>
            </div>
            <div class="toast-message">${mensagem}</div>
        `;

        toastContainer.appendChild(toast);

        if (window.lucide) {
            window.lucide.createIcons();
        }

        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(40px)';
            setTimeout(() => {
                toast.remove();
            }, 300);
        }, 3500);
    }

    // --------------------------------------------------------------------------
    // SYSTEM: MODAL DE CONFIRMAÇÃO PERSONALIZADO (Substitui os confirms nativos)
    // --------------------------------------------------------------------------
    function mostrarConfirmacao({ titulo = 'Confirmação', mensagem, btnTexto = 'Confirmar', btnClasse = 'btn-danger', icone = 'alert-triangle' }) {
        return new Promise((resolve) => {
            confirmResolver = resolve;

            const titleEl = document.getElementById('confirmTitle');
            const msgEl = document.getElementById('confirmMessage');
            const btnOk = document.getElementById('btnConfirmOk');
            const iconBox = document.getElementById('confirmIconBox');

            if (titleEl) titleEl.textContent = titulo;
            if (msgEl) msgEl.textContent = mensagem;

            if (btnOk) {
                btnOk.textContent = btnTexto;
                btnOk.className = `btn-modal ${btnClasse}`;
            }

            if (iconBox) {
                if (btnClasse === 'btn-success') {
                    iconBox.style.background = '#dcfce7';
                    iconBox.style.color = '#16a34a';
                    iconBox.innerHTML = '<i data-lucide="check-circle-2" style="width: 22px; height: 22px;"></i>';
                } else {
                    iconBox.style.background = '#fee2e2';
                    iconBox.style.color = '#dc2626';
                    iconBox.innerHTML = '<i data-lucide="alert-triangle" style="width: 22px; height: 22px;"></i>';
                }
                if (window.lucide) window.lucide.createIcons();
            }

            abrirModal(modalConfirmacao);
        });
    }

    // Eventos dos botões do Modal de Confirmação
    document.getElementById('btnConfirmOk')?.addEventListener('click', () => {
        fecharModal(modalConfirmacao);
        if (confirmResolver) confirmResolver(true);
    });

    document.getElementById('btnConfirmCancel')?.addEventListener('click', () => {
        fecharModal(modalConfirmacao);
        if (confirmResolver) confirmResolver(false);
    });

    document.getElementById('btnConfirmClose')?.addEventListener('click', () => {
        fecharModal(modalConfirmacao);
        if (confirmResolver) confirmResolver(false);
    });

    // --------------------------------------------------------------------------
    // MODAIS: ABRIR / FECHAR
    // --------------------------------------------------------------------------
    function abrirModal(modal) {
        if (modal) {
            modal.classList.add('active');
        }
    }

    function fecharModal(modal) {
        if (modal) {
            modal.classList.remove('active');
        }
    }

    function fecharModais() {
        document.querySelectorAll('.modal-overlay').forEach(m => m.classList.remove('active'));
    }

    btnAbrirNovoArmario?.addEventListener('click', () => {
        limparAlertasModais();
        formNovoArmario?.reset();
        abrirModal(modalNovoArmario);
    });

    modalCloseBtns.forEach(btn => {
        btn.addEventListener('click', fecharModais);
    });

    document.querySelectorAll('.modal-overlay').forEach(overlay => {
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) {
                fecharModais();
            }
        });
    });

    function limparAlertasModais() {
        document.querySelectorAll('.alert-banner').forEach(el => el.remove());
    }

    function exibirAlertaForm(formContainer, mensagem, tipo = 'danger') {
        limparAlertasModais();
        if (!formContainer) return;

        const alertBox = document.createElement('div');
        alertBox.className = `alert-banner alert-banner-${tipo}`;
        alertBox.innerHTML = `
            <i data-lucide="alert-circle" style="width:18px;height:18px;flex-shrink:0;"></i>
            <span>${mensagem}</span>
        `;
        formContainer.prepend(alertBox);

        if (window.lucide) {
            window.lucide.createIcons();
        }
    }

    // --------------------------------------------------------------------------
    // API: CARREGAR & ATUALIZAR ARMÁRIOS
    // --------------------------------------------------------------------------
    async function carregarArmarios() {
        const query = searchInput ? searchInput.value.trim() : '';
        const url = `/armarios/api/listar?filtro=${encodeURIComponent(filtroAtual)}&q=${encodeURIComponent(query)}`;

        try {
            const resp = await fetch(url, { headers: { 'Accept': 'application/json' } });
            if (!resp.ok) return;
            const data = await resp.json();

            if (data.sucesso) {
                renderizarEstatisticas(data.stats);
                renderizarGrid(data.armarios);
            }
        } catch (err) {
            console.error('Erro ao buscar armários:', err);
        }
    }

    function renderizarEstatisticas(stats) {
        if (totalStatEl) totalStatEl.textContent = stats.total;
        if (disponiveisStatEl) disponiveisStatEl.textContent = stats.disponiveis;
        if (ocupadosStatEl) ocupadosStatEl.textContent = stats.ocupados;
    }

    function renderizarGrid(armarios) {
        if (!armariosGrid) return;

        if (armarios.length === 0) {
            armariosGrid.innerHTML = `
                <div style="grid-column: 1 / -1; text-align: center; padding: 48px; color: #64748b;">
                    <p style="font-size: 16px; font-weight: 500;">Nenhum armário encontrado.</p>
                </div>
            `;
            return;
        }

        armariosGrid.innerHTML = armarios.map(a => {
            const isLivre = a.status === 'Livre';
            const statusClass = isLivre ? 'livre' : 'ocupado';
            const iconName = isLivre ? 'lock-keyhole-open' : 'lock-keyhole';
            const statusBadgeText = isLivre ? 'Livre' : 'Ocupado';

            return `
                <div class="armario-card ${statusClass}" data-id="${a.id}">
                    <div class="armario-card-top">
                        <i data-lucide="${iconName}" class="lock-icon" style="width: 20px; height: 20px;"></i>
                        <span class="status-badge">${statusBadgeText}</span>
                    </div>
                    <div class="armario-card-body">
                        <div class="numero">Nº ${a.numero}</div>
                        <div class="localizacao">${a.localizacao}</div>
                        ${!isLivre ? `<div class="aluno">${a.aluno_nome}</div>` : ''}
                    </div>
                </div>
            `;
        }).join('');

        if (window.lucide) {
            window.lucide.createIcons();
        }

        document.querySelectorAll('.armario-card').forEach(card => {
            card.addEventListener('click', () => {
                const id = card.getAttribute('data-id');
                abrirDetalhesArmario(id);
            });
        });
    }

    // --------------------------------------------------------------------------
    // CLIQUE NO CARD: ABRIR MODAL DE DETALHES / AGENDAMENTO
    // --------------------------------------------------------------------------
    async function abrirDetalhesArmario(armarioId) {
        limparAlertasModais();
        try {
            const resp = await fetch(`/armarios/${armarioId}`, { headers: { 'Accept': 'application/json' } });
            if (!resp.ok) return;
            const data = await resp.json();

            if (!data.sucesso || !data.armario) return;
            const arm = data.armario;

            const modalTitleEl = document.getElementById('detailsModalTitle');
            const modalStatusEl = document.getElementById('detailsModalStatus');
            const modalBodyEl = document.getElementById('detailsModalBody');

            if (!modalTitleEl || !modalStatusEl || !modalBodyEl) return;

            modalTitleEl.innerHTML = `Armário Nº ${arm.numero} <span class="loc-sub">— ${arm.localizacao}</span>`;

            if (arm.status === 'Ocupado') {
                // VISUALIZAÇÃO ARMÁRIO OCUPADO
                modalStatusEl.innerHTML = `Status: <span class="status-val-ocupado">Ocupado</span>`;

                modalBodyEl.innerHTML = `
                    <div class="details-list">
                        <div class="details-item"><span class="label">Aluno:</span> <span class="val">${arm.aluno_nome}</span></div>
                        <div class="details-item"><span class="label">Turma:</span> <span class="val">${arm.turma || '-'}</span></div>
                        <div class="details-item"><span class="label">Contato:</span> <span class="val">${arm.contato || '-'}</span></div>
                        <div class="details-item"><span class="label">Período:</span> <span class="val">${arm.data_inicio || ''} — ${arm.data_termino || ''}</span></div>
                        <div class="details-item"><span class="label">Observações:</span> <span class="val">${arm.observacoes || '-'}</span></div>
                    </div>
                    <div class="modal-actions space-between">
                        <button type="button" class="btn-modal btn-danger" id="btnExcluirArmario">
                            <i data-lucide="trash-2" style="width:16px;height:16px;"></i> Remover
                        </button>
                        <button type="button" class="btn-modal btn-success" id="btnLiberarArmario">
                            Liberar Armário
                        </button>
                    </div>
                `;

                if (window.lucide) window.lucide.createIcons();

                // Handler Liberar Armário (Substitui confirm nativo)
                document.getElementById('btnLiberarArmario')?.addEventListener('click', async () => {
                    const confirmou = await mostrarConfirmacao({
                        titulo: 'Liberar Armário',
                        mensagem: `Deseja liberar a reserva do Armário Nº ${arm.numero}?`,
                        btnTexto: 'Liberar Armário',
                        btnClasse: 'btn-success'
                    });
                    if (confirmou) {
                        await acaoArmario(`/armarios/${arm.id}/liberar`);
                    }
                });

                // Handler Excluir Armário (Substitui confirm nativo)
                document.getElementById('btnExcluirArmario')?.addEventListener('click', async () => {
                    const confirmou = await mostrarConfirmacao({
                        titulo: 'Excluir Armário',
                        mensagem: `Tem certeza que deseja excluir o Armário Nº ${arm.numero}?`,
                        btnTexto: 'Excluir',
                        btnClasse: 'btn-danger'
                    });
                    if (confirmou) {
                        await acaoArmario(`/armarios/${arm.id}/excluir`);
                    }
                });

            } else {
                // VISUALIZAÇÃO ARMÁRIO LIVRE / RESERVAR
                modalStatusEl.innerHTML = `Status: <span class="status-val-livre">Disponível</span>`;

                const hoje = new Date().toISOString().split('T')[0];

                modalBodyEl.innerHTML = `
                    <form id="formReservaModal">
                        <div id="formReservaAlert"></div>
                        <div class="form-group">
                            <label class="form-label">Nome do aluno <span class="req">*</span></label>
                            <input type="text" name="aluno_nome" class="form-control" required placeholder="Nome completo do aluno">
                        </div>

                        <div class="form-row">
                            <div class="form-group">
                                <label class="form-label">Turma</label>
                                <input type="text" name="turma" class="form-control" placeholder="Ex: Senai 2º Ano">
                            </div>
                            <div class="form-group">
                                <label class="form-label">Contato</label>
                                <input type="text" name="contato" class="form-control" placeholder="Ex: 11999999999">
                            </div>
                        </div>

                        <div class="form-row">
                            <div class="form-group">
                                <label class="form-label">Início <span class="req">*</span></label>
                                <input type="date" name="data_inicio" id="dtInicio" class="form-control" value="${hoje}" required>
                            </div>
                            <div class="form-group">
                                <label class="form-label">Término <span class="req">*</span></label>
                                <input type="date" name="data_termino" id="dtTermino" class="form-control" required>
                            </div>
                        </div>

                        <div class="form-group">
                            <label class="form-label">Observações</label>
                            <textarea name="observacoes" class="form-control" placeholder="Anotações sobre o agendamento..."></textarea>
                        </div>

                        <div class="modal-actions space-between">
                            <button type="button" class="btn-modal btn-secondary" id="btnExcluirArmarioLivre">
                                <i data-lucide="trash-2" style="width:16px;height:16px;"></i> Remover
                            </button>
                            <button type="submit" class="btn-modal btn-orange">
                                Confirmar Reserva
                            </button>
                        </div>
                    </form>
                `;

                if (window.lucide) window.lucide.createIcons();

                // Form Submit Reserva com Validação de Datas no Frontend
                const formReservaModal = document.getElementById('formReservaModal');
                formReservaModal?.addEventListener('submit', async (e) => {
                    e.preventDefault();

                    const dtInicioVal = document.getElementById('dtInicio')?.value;
                    const dtTerminoVal = document.getElementById('dtTermino')?.value;

                    if (dtInicioVal && dtTerminoVal && dtTerminoVal < dtInicioVal) {
                        const msgErro = 'A data término não pode ser anterior à data de início.';
                        exibirAlertaForm(formReservaModal, msgErro);
                        mostrarToast(msgErro, 'error');
                        return;
                    }

                    const formData = new FormData(formReservaModal);
                    await acaoFormArmario(`/armarios/${arm.id}/reservar`, formData, formReservaModal);
                });

                // Handler Excluir Armário Livre (Substitui confirm nativo)
                document.getElementById('btnExcluirArmarioLivre')?.addEventListener('click', async () => {
                    const confirmou = await mostrarConfirmacao({
                        titulo: 'Remover Armário',
                        mensagem: `Tem certeza que deseja remover o Armário Nº ${arm.numero}?`,
                        btnTexto: 'Remover',
                        btnClasse: 'btn-danger'
                    });
                    if (confirmou) {
                        await acaoArmario(`/armarios/${arm.id}/excluir`);
                    }
                });
            }

            abrirModal(modalArmarioDetails);

        } catch (err) {
            console.error('Erro ao carregar detalhes do armário:', err);
        }
    }

    // --------------------------------------------------------------------------
    // MÉTODOS DE AÇÃO AJAX (Criar, Reservar, Liberar, Excluir)
    // --------------------------------------------------------------------------
    async function acaoArmario(url) {
        try {
            const resp = await fetch(url, {
                method: 'POST',
                headers: { 'Accept': 'application/json', 'X-Requested-With': 'XMLHttpRequest' }
            });
            const data = await resp.json();
            if (resp.ok && data.sucesso) {
                fecharModais();
                mostrarToast(data.mensagem || 'Operação realizada com sucesso!', 'success');
                await carregarArmarios();
            } else {
                mostrarToast(data.mensagem || 'Erro ao realizar operação.', 'error');
            }
        } catch (err) {
            console.error('Erro na requisição:', err);
            mostrarToast('Falha na comunicação com o servidor.', 'error');
        }
    }

    async function acaoFormArmario(url, formData, formEl = null) {
        try {
            const resp = await fetch(url, {
                method: 'POST',
                headers: { 'Accept': 'application/json', 'X-Requested-With': 'XMLHttpRequest' },
                body: formData
            });
            const data = await resp.json();
            if (resp.ok && data.sucesso) {
                fecharModais();
                mostrarToast(data.mensagem || 'Operação realizada com sucesso!', 'success');
                await carregarArmarios();
            } else {
                const msg = data.mensagem || data.detail || 'Preencha todos os campos obrigatórios.';
                if (formEl) {
                    exibirAlertaForm(formEl, msg);
                }
                mostrarToast(msg, 'error');
            }
        } catch (err) {
            console.error('Erro na submissão do formulário:', err);
            mostrarToast('Falha na comunicação com o servidor.', 'error');
        }
    }

    // Submission form Criar Novo Armário
    formNovoArmario?.addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = new FormData(formNovoArmario);
        await acaoFormArmario('/armarios/novo', formData, formNovoArmario);
    });

    // --------------------------------------------------------------------------
    // FILTROS & BUSCA
    // --------------------------------------------------------------------------
    filterBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            filterBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            filtroAtual = btn.getAttribute('data-filter') || 'todos';
            carregarArmarios();
        });
    });

    searchInput?.addEventListener('input', () => {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            carregarArmarios();
        }, 300);
    });

    // Carregamento inicial de escuta de eventos nos cards existentes no HTML estático
    document.querySelectorAll('.armario-card').forEach(card => {
        card.addEventListener('click', () => {
            const id = card.getAttribute('data-id');
            abrirDetalhesArmario(id);
        });
    });
});
