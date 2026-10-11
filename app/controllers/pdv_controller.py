# ============================================================
# controllers/pdv_controller.py — Ponto de Venda

# O PDV funciona assim:
# 1. GET /pdv        → tela com produtos + campo de cliente
# 2. O carrinho vive inteiro no JavaScript (sessionStorage)
# 3. POST /pdv/finalizar → recebe um JSON com os itens
#                          cria Venda + ItensVenda + baixa estoque
# ============================================================

import json
import math
from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database import get_db
from app.models.venda import Venda, ItemVenda, PagamentoVenda
from app.models.produto import Produto
from app.models.cliente import Cliente
from app.models.usuarios import Usuario
from app.models.movimentacao import Movimentacao, TipoMovimentacao
from app.auth import get_usuario_logado

router = APIRouter(prefix="/pdv", tags=["PDV"])
templates = Jinja2Templates(directory="app/templates")

DESCONTO_ASSOCIADO = 10.0  # percentual fixo


@router.get("/")
def tela_pdv(
    request: Request,
    db: Session = Depends(get_db),
    usuario = Depends(get_usuario_logado)
):
    """
    Carrega a tela do PDV com todos os produtos ativos
    e a lista de clientes para o campo de busca.
    """
    produtos  = (
        db.query(Produto)
        .filter(Produto.ativo == True, Produto.estoque_atual > 0)
        .order_by(Produto.nome)
        .all()
    )
    clientes  = (
        db.query(Cliente)
        .filter(Cliente.ativo == True)
        .order_by(Cliente.nome)
        .all()
    )

    return templates.TemplateResponse(
        request,
        "home.html",
        {
            "request":             request,
            "usuario":             usuario,
            "produtos":            produtos,
            "clientes":            clientes,
            "desconto_associado":  DESCONTO_ASSOCIADO,
        }
    )


@router.post("/finalizar")
def finalizar_venda(
    request: Request,
    carrinho_json: str    = Form(...),        # JSON serializado pelo JS
    cliente_id: int       = Form(0),          # 0 = sem cliente identificado
    observacao: str       = Form(""),
    desconto_manual: float = Form(0.0),       # Valor do desconto manual inserido
    desconto_tipo: str    = Form("reais"),    # "reais" ou "porcentagem"
    pagamentos_json: str  = Form("[]"),       # JSON com 1 ou 2 formas de pagamento
    db: Session           = Depends(get_db),
    usuario               = Depends(get_usuario_logado)
):
    """
    Recebe o carrinho como JSON, valida estoque, calcula desconto manual,
    valida 1 ou 2 formas de pagamento e persiste a venda.
    """
    try:
        itens = json.loads(carrinho_json)
    except (json.JSONDecodeError, ValueError):
        return RedirectResponse(url="/pdv?erro=json", status_code=302)

    if not itens:
        return RedirectResponse(url="/pdv?erro=vazio", status_code=302)

    # Busca o cliente e verifica se é associado
    cliente = None
    is_associado = False

    if cliente_id:
        cliente = db.query(Cliente).filter(
            Cliente.id == cliente_id,
            Cliente.ativo == True
        ).first()

        if cliente and cliente.is_associado:
            is_associado = True

    # ── Valida estoque e calcula totais ──────────────────────
    total_bruto = 0.0
    subtotal_base = 0.0
    itens_validados = []

    for item in itens:
        produto = db.query(Produto).filter(
            Produto.id == item["produto_id"],
            Produto.ativo == True
        ).with_for_update().first()

        if not produto:
            return RedirectResponse(
                url=f"/pdv?erro=produto_inexistente&id={item['produto_id']}",
                status_code=302
            )

        qtd = int(item["quantidade"])

        if qtd <= 0:
            return RedirectResponse(url="/pdv?erro=quantidade", status_code=302)

        if produto.estoque_atual < qtd:
            return RedirectResponse(
                url=f"/pdv?erro=estoque&produto={produto.nome}",
                status_code=302
            )

        preco_unitario = (
            produto.preco_associado
            if (is_associado and produto.preco_associado is not None)
            else produto.preco
        )

        subtotal_bruto = produto.preco * qtd
        subtotal_liquido_item = preco_unitario * qtd

        total_bruto += subtotal_bruto
        subtotal_base += subtotal_liquido_item

        itens_validados.append({
            "produto":        produto,
            "quantidade":     qtd,
            "preco_unitario": preco_unitario,
            "produto_nome":   produto.nome,
        })

    # ── Validação e cálculo do desconto manual ────────────────
    valor_desconto_manual = 0.0
    if desconto_manual > 0:
        if desconto_tipo == "porcentagem":
            if desconto_manual > 100.0:
                return RedirectResponse(url="/pdv?erro=desconto_acima_limite", status_code=302)
            valor_desconto_manual = round(subtotal_base * (desconto_manual / 100.0), 2)
        else:
            if desconto_manual > subtotal_base:
                return RedirectResponse(url="/pdv?erro=desconto_acima_limite", status_code=302)
            valor_desconto_manual = round(desconto_manual, 2)

    total_liquido = round(max(0.0, subtotal_base - valor_desconto_manual), 2)
    desconto_total = round(total_bruto - total_liquido, 2)
    desconto_percentual = round((desconto_total / total_bruto * 100), 1) if total_bruto > 0 else 0.0

    # ── Validação das formas de pagamento (Sprint 3) ─────────
    try:
        pagamentos_data = json.loads(pagamentos_json) if pagamentos_json else []
    except (json.JSONDecodeError, ValueError):
        pagamentos_data = []

    # Se nenhum pagamento foi enviado no JSON, default para Dinheiro (1 forma)
    if not pagamentos_data:
        pagamentos_data = [{
            "forma_pagamento": "DINHEIRO",
            "valor": total_liquido,
            "valor_recebido": total_liquido,
            "troco": 0.0
        }]

    if len(pagamentos_data) > 2:
        return RedirectResponse(url="/pdv?erro=max_duas_formas", status_code=302)

    soma_pagamentos = 0.0
    pagamentos_validados = []

    for p in pagamentos_data:
        forma = str(p.get("forma_pagamento", "")).strip().upper()
        if not forma:
            forma = "DINHEIRO"
        
        try:
            val = round(float(p.get("valor", 0.0)), 2)
        except (ValueError, TypeError):
            val = 0.0

        if val <= 0:
            return RedirectResponse(url="/pdv?erro=valor_pagamento_invalido", status_code=302)

        soma_pagamentos += val

        val_rec = None
        troco = 0.0
        if "DINHEIRO" in forma:
            try:
                val_rec = round(float(p.get("valor_recebido", val)), 2)
            except (ValueError, TypeError):
                val_rec = val
            
            if val_rec < val:
                return RedirectResponse(url="/pdv?erro=dinheiro_insuficiente", status_code=302)
            troco = round(val_rec - val, 2)

        pagamentos_validados.append({
            "forma_pagamento": forma,
            "valor":           val,
            "valor_recebido":  val_rec,
            "troco":           troco
        })

    # Valida que a soma dos pagamentos é igual ao total líquido da venda
    if abs(soma_pagamentos - total_liquido) > 0.05:
        return RedirectResponse(url=f"/pdv?erro=soma_pagamentos_invalida&total={total_liquido}&pago={soma_pagamentos}", status_code=302)

    # ── Persiste tudo em uma única transação ─────────────────
    try:
        venda = Venda(
            cliente_id          = cliente_id or None,
            usuario_id          = usuario.get("id"),
            desconto_percentual = desconto_percentual,
            desconto_manual     = valor_desconto_manual,
            desconto_tipo       = desconto_tipo,
            total_bruto         = round(total_bruto, 2),
            total_liquido       = round(total_liquido, 2),
            observacao          = observacao or None,
        )
        db.add(venda)
        db.flush()  # gera o venda.id sem commitar ainda

        for item in itens_validados:
            db.add(ItemVenda(
                venda_id       = venda.id,
                produto_id     = item["produto"].id,
                produto_nome   = item["produto_nome"],
                quantidade     = item["quantidade"],
                preco_unitario = item["preco_unitario"],
            ))
            
            # Baixa o estoque do produto
            item["produto"].estoque_atual -= item["quantidade"]
            
            # Registra a movimentação de saída para o Dashboard
            db.add(Movimentacao(
                tipo           = TipoMovimentacao.SAIDA,
                quantidade     = item["quantidade"],
                preco_unitario = item["preco_unitario"],
                observacao     = f"Venda PDV #{venda.id}",
                produto_id     = item["produto"].id,
                usuario_id     = usuario.get("id")
            ))

        for pag in pagamentos_validados:
            db.add(PagamentoVenda(
                venda_id        = venda.id,
                forma_pagamento = pag["forma_pagamento"],
                valor           = pag["valor"],
                valor_recebido  = pag["valor_recebido"],
                troco           = pag["troco"],
            ))

        db.commit()
    except Exception as e:
        db.rollback()
        return RedirectResponse(url="/pdv?erro=transacao", status_code=302)

    return RedirectResponse(
        url=f"/pdv/venda/{venda.id}?sucesso=ok",
        status_code=302
    )


@router.get("/venda/{venda_id}")
def detalhe_venda(
    venda_id: int,
    request: Request,
    db: Session = Depends(get_db),
    usuario = Depends(get_usuario_logado)
):
    """Comprovante da venda — exibido imediatamente após finalizar."""
    venda = db.query(Venda).filter(Venda.id == venda_id).first()

    if not venda:
        return RedirectResponse(url="/pdv", status_code=302)

    return templates.TemplateResponse(
        request,
        "historico_venda/comprovante.html",
        {"request": request, "usuario": usuario, "venda": venda}
    )


@router.get("/historico")
def historico_vendas(
    request: Request,
    busca: str = "",
    ordem: str = "recentes",
    pagina: int = 1,
    por_pagina: int = 10,
    db: Session = Depends(get_db),
    usuario = Depends(get_usuario_logado)
):
    """Histórico de todas as vendas com busca, ordenação e paginação."""
    query = (
        db.query(Venda)
        .outerjoin(Cliente, Venda.cliente_id == Cliente.id)
        .outerjoin(Usuario, Venda.usuario_id == Usuario.id)
    )

    if busca:
        busca_limpa = busca.strip().replace("#", "")
        filtros = [
            Cliente.nome.ilike(f"%{busca}%"),
            Usuario.nome.ilike(f"%{busca}%"),
        ]
        if busca_limpa.isdigit():
            filtros.append(Venda.id == int(busca_limpa))
        query = query.filter(or_(*filtros))

    # Ordenação
    if ordem == "antigas":
        query = query.order_by(Venda.criado_em.asc())
    elif ordem == "maior_valor":
        query = query.order_by(Venda.total_liquido.desc())
    elif ordem == "menor_valor":
        query = query.order_by(Venda.total_liquido.asc())
    else:
        ordem = "recentes"
        query = query.order_by(Venda.criado_em.desc())

    total_vendas = query.count()

    pagina = max(pagina, 1)
    por_pagina = max(por_pagina, 1)

    total_paginas = math.ceil(total_vendas / por_pagina) if total_vendas else 1
    if pagina > total_paginas:
        pagina = total_paginas

    offset = (pagina - 1) * por_pagina
    vendas = query.offset(offset).limit(por_pagina).all()

    return templates.TemplateResponse(
        request,
        "historico_venda/historico.html",
        {
            "request":      request,
            "usuario":      usuario,
            "vendas":       vendas,
            "busca":        busca,
            "ordem":        ordem,
            "pagina":       pagina,
            "por_pagina":   por_pagina,
            "total_paginas": total_paginas,
            "total_vendas":  total_vendas,
        }
    )