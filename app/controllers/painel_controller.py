# controllers/painel_controller.py
# ============================================================
# Controller do Painel Administrativo / Dashboard
# 100% dos dados são calculados dinamicamente via banco de dados
# ============================================================

from datetime import datetime, date, timedelta
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func, extract, or_

from app.database import get_db
from app.models.movimentacao import Movimentacao, TipoMovimentacao
from app.models.produto import Produto
from app.models.armario import Armario
from app.models.usuarios import Usuario
from app.auth import get_admin

router = APIRouter(prefix="/painel", tags=["Painel"])
templates = Jinja2Templates(directory="app/templates")

DIAS_SEMANA = ["segunda-feira", "terça-feira", "quarta-feira", "quinta-feira", "sexta-feira", "sábado", "domingo"]
MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]


@router.get("", response_class=HTMLResponse)
@router.get("/", response_class=HTMLResponse)
def painel_administrativo(
    request: Request,
    admin = Depends(get_admin),
    db: Session = Depends(get_db)
):
    hoje = date.today()

    # ----------------------------------------------------------
    # 1. Movimentações do dia (Saídas = Vendas de Hoje)
    # ----------------------------------------------------------
    movs_hoje = db.query(Movimentacao).filter(
        Movimentacao.tipo == TipoMovimentacao.SAIDA,
        func.date(Movimentacao.criado_em) == hoje
    ).all()

    vendas_hoje = len(movs_hoje)
    total_hoje = sum(m.valor_total for m in movs_hoje)

    # ----------------------------------------------------------
    # 2. Movimentações totais (Todas as Vendas)
    # ----------------------------------------------------------
    movs_todas = db.query(Movimentacao).filter(
        Movimentacao.tipo == TipoMovimentacao.SAIDA
    ).all()

    total_vendas = len(movs_todas)
    total_geral = sum(m.valor_total for m in movs_todas)

    # Ticket médio: calcula baseado no dia de hoje (ou geral se hoje for 0)
    ticket_medio = (total_hoje / vendas_hoje) if vendas_hoje > 0 else ((total_geral / total_vendas) if total_vendas > 0 else 0.0)

    # ----------------------------------------------------------
    # 3. Status de Armários (Ocupação real do banco)
    # ----------------------------------------------------------
    armarios_total = db.query(Armario).filter(Armario.ativo == True).count()
    armarios_ocupados = db.query(Armario).filter(Armario.ativo == True, Armario.status == "Ocupado").count()
    armarios_pct = round((armarios_ocupados / armarios_total * 100)) if armarios_total > 0 else 0

    # ----------------------------------------------------------
    # 4. Produtos com Estoque Baixo (<= 5 unidades no banco)
    # ----------------------------------------------------------
    produtos_estoque_baixo = db.query(Produto).filter(
        Produto.ativo == True,
        Produto.estoque_atual <= 5
    ).order_by(Produto.estoque_atual.asc()).limit(5).all()

    # ----------------------------------------------------------
    # 5. Top 5 Produtos Mais Vendidos (Agrupamento real SQL)
    # ----------------------------------------------------------
    top_produtos_query = (
        db.query(
            Produto,
            func.sum(Movimentacao.quantidade).label("total_qtd"),
            func.sum(Movimentacao.quantidade * Movimentacao.preco_unitario).label("total_valor")
        )
        .join(Movimentacao, Movimentacao.produto_id == Produto.id)
        .filter(Movimentacao.tipo == TipoMovimentacao.SAIDA)
        .group_by(Produto.id)
        .order_by(func.sum(Movimentacao.quantidade).desc())
        .limit(5)
        .all()
    )

    top_produtos = []
    max_qtd = max([qtd for _, qtd, _ in top_produtos_query], default=1) if top_produtos_query else 1

    for prod, qtd, valor in top_produtos_query:
        qtd_val = int(qtd or 0)
        pct_val = int((qtd_val / max_qtd) * 100) if max_qtd > 0 else 0
        top_produtos.append({
            "id": prod.id,
            "nome": prod.nome,
            "imagem_path": prod.imagem_path,
            "total_qtd": qtd_val,
            "total_valor": float(valor or 0.0),
            "pct": max(pct_val, 12)
        })

    # ----------------------------------------------------------
    # 6. Vendas dos últimos 7 dias (Soma diária real SQL)
    # ----------------------------------------------------------
    vendas_7_dias_labels = []
    vendas_7_dias_valores = []

    for i in range(6, -1, -1):
        dia_alvo = hoje - timedelta(days=i)
        vendas_7_dias_labels.append(dia_alvo.strftime("%d/%m"))

        total_dia = db.query(func.sum(Movimentacao.quantidade * Movimentacao.preco_unitario)).filter(
            Movimentacao.tipo == TipoMovimentacao.SAIDA,
            func.date(Movimentacao.criado_em) == dia_alvo
        ).scalar() or 0.0

        vendas_7_dias_valores.append(round(float(total_dia), 2))

    # ----------------------------------------------------------
    # 7. Vendas por Hora (Horários de Pico reais 07h às 21h)
    # ----------------------------------------------------------
    horas_labels = [f"{h:02d}h" for h in range(7, 22)]
    vendas_por_hora_valores = []

    for h in range(7, 22):
        qtd_hora = db.query(func.sum(Movimentacao.quantidade)).filter(
            Movimentacao.tipo == TipoMovimentacao.SAIDA,
            extract('hour', Movimentacao.criado_em) == h
        ).scalar() or 0

        vendas_por_hora_valores.append(int(qtd_hora))

    # ----------------------------------------------------------
    # 8. Formas de Pagamento (Análise real de observações das vendas)
    # ----------------------------------------------------------
    val_dinheiro = 0.0
    val_cartao = 0.0
    val_pix = 0.0
    val_outros = 0.0

    for m in movs_todas:
        obs = (m.observacao or "").lower()
        if "pix" in obs:
            val_pix += m.valor_total
        elif "cart" in obs or "débito" in obs or "debito" in obs or "crédito" in obs or "credito" in obs:
            val_cartao += m.valor_total
        elif "dinheiro" in obs or "espécie" in obs or "especie" in obs:
            val_dinheiro += m.valor_total
        else:
            val_outros += m.valor_total

    total_pag_conhecido = val_dinheiro + val_cartao + val_pix + val_outros

    if total_pag_conhecido > 0:
        pct_dinheiro = round((val_dinheiro / total_pag_conhecido) * 100)
        pct_cartao = round((val_cartao / total_pag_conhecido) * 100)
        pct_pix = round((val_pix / total_pag_conhecido) * 100)
        pct_outros = round((val_outros / total_pag_conhecido) * 100)
    else:
        # Se não houver observações com palavra-chave específica, calcula com base nas vendas reais existentes
        pct_dinheiro = 0
        pct_cartao = 0
        pct_pix = 0
        pct_outros = 0

    # ----------------------------------------------------------
    # 9. Associados (% de vendas com desconto/preço de sócio)
    # ----------------------------------------------------------
    vendas_socio_count = db.query(Movimentacao).filter(
        Movimentacao.tipo == TipoMovimentacao.SAIDA,
        or_(
            Movimentacao.observacao.ilike("%sócio%"),
            Movimentacao.observacao.ilike("%socio%"),
            Movimentacao.observacao.ilike("%associado%")
        )
    ).count()

    pct_socio = round((vendas_socio_count / total_vendas) * 100) if total_vendas > 0 else 0

    # ----------------------------------------------------------
    # 10. Usuários Ativos
    # ----------------------------------------------------------
    usuarios_ativos_count = db.query(Usuario).filter(Usuario.ativo == True).count()

    # Formatação de data em PT-BR
    data_atual_str = f"{DIAS_SEMANA[hoje.weekday()]}, {hoje.day} de {MESES[hoje.month - 1]} de {hoje.year}"

    return templates.TemplateResponse(
        request,
        "painel/index.html",
        {
            "request": request,
            "usuario": admin,
            "vendas_hoje": vendas_hoje,
            "total_hoje": total_hoje,
            "total_geral": total_geral,
            "total_vendas": total_vendas,
            "ticket_medio": ticket_medio,
            "armarios_total": armarios_total,
            "armarios_ocupados": armarios_ocupados,
            "armarios_pct": armarios_pct,
            "produtos_estoque_baixo": produtos_estoque_baixo,
            "top_produtos": top_produtos,
            "vendas_7_dias_labels": vendas_7_dias_labels,
            "vendas_7_dias_valores": vendas_7_dias_valores,
            "horas_labels": horas_labels,
            "vendas_por_hora_valores": vendas_por_hora_valores,
            "val_dinheiro": val_dinheiro,
            "val_cartao": val_cartao,
            "val_pix": val_pix,
            "val_outros": val_outros,
            "pct_dinheiro": pct_dinheiro,
            "pct_cartao": pct_cartao,
            "pct_pix": pct_pix,
            "pct_outros": pct_outros,
            "total_pag_conhecido": total_pag_conhecido,
            "pct_socio": pct_socio,
            "usuarios_ativos_count": usuarios_ativos_count,
            "data_atual_str": data_atual_str,
        }
    )
