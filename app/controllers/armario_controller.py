# controllers/armario_controller.py — CRUD de Armários e Agendamentos

from fastapi import APIRouter, Depends, Request, Form, HTTPException, Query, Body
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from datetime import datetime, date
from typing import Optional

from app.database import get_db
from app.models.armario import Armario
from app.auth import get_admin

router = APIRouter(prefix="/armarios", tags=["Armários"])

BLOCOS_DISPONIVEIS = [
    "Bloco A",
    "Bloco B",
    "Bloco C",
]


templates = Jinja2Templates(directory="app/templates")

def formatar_data(dt: Optional[date]) -> Optional[str]:
    """Converte objeto date em string DD/MM/YYYY para exibição."""
    if dt:
        return dt.strftime("%d/%m/%Y")
    return None

def parse_data(dt_str: Optional[str]) -> Optional[date]:
    """Converte string YYYY-MM-DD ou DD/MM/YYYY em objeto date."""
    if not dt_str:
        return None
    dt_str = dt_str.strip()
    if not dt_str:
        return None
    try:
        if "-" in dt_str:
            return datetime.strptime(dt_str, "%Y-%m-%d").date()
        elif "/" in dt_str:
            return datetime.strptime(dt_str, "%d/%m/%Y").date()
    except ValueError:
        pass
    return None


# ============================================================
# TELA PRINCIPAL (LISTAGEM DE ARMÁRIOS)
# ============================================================

@router.get("", response_class=HTMLResponse)
@router.get("/", response_class=HTMLResponse)
def listar_armarios(
    request: Request,
    db: Session = Depends(get_db),
    admin = Depends(get_admin)
):
    """
    Exibe a tela de Agendamento de Armários.
    Carrega as estatísticas (Total, Disponíveis, Ocupados) e os cartões.
    """
    armarios = db.query(Armario).filter(Armario.ativo == True).order_by(Armario.numero).all()

    total = len(armarios)
    disponiveis = sum(1 for a in armarios if a.status == "Livre")
    ocupados = sum(1 for a in armarios if a.status == "Ocupado")

    return templates.TemplateResponse(
        request,
        "armarios/index.html",
        {
            "request": request,
            "usuario": admin,
            "armarios": armarios,
            "total": total,
            "disponiveis": disponiveis,
            "ocupados": ocupados,
        }
    )


# ============================================================
# API JSON DE BUSCA E FILTRAGEM
# ============================================================

@router.get("/api/listar")
def api_listar_armarios(
    q: Optional[str] = Query(None),
    filtro: Optional[str] = Query("todos"),
    db: Session = Depends(get_db),
    admin = Depends(get_admin)
):
    """Retorna lista de armários em JSON filtrados por busca e status."""
    query = db.query(Armario).filter(Armario.ativo == True)

    # Filtragem por status
    if filtro == "disponiveis":
        query = query.filter(Armario.status == "Livre")
    elif filtro == "ocupados":
        query = query.filter(Armario.status == "Ocupado")

    # Filtragem por texto de busca (número, localização, aluno)
    if q and q.strip():
        termo = f"%{q.strip()}%"
        query = query.filter(
            or_(
                Armario.numero.ilike(termo),
                Armario.localizacao.ilike(termo),
                Armario.aluno_nome.ilike(termo),
                Armario.turma.ilike(termo)
            )
        )

    armarios = query.order_by(Armario.numero).all()

    # Estatísticas globais (independentes do filtro de busca atual)
    todos_armarios = db.query(Armario).filter(Armario.ativo == True).all()
    total = len(todos_armarios)
    disponiveis = sum(1 for a in todos_armarios if a.status == "Livre")
    ocupados = sum(1 for a in todos_armarios if a.status == "Ocupado")

    armarios_data = []
    for a in armarios:
        armarios_data.append({
            "id": a.id,
            "numero": a.numero,
            "localizacao": a.localizacao,
            "status": a.status,
            "aluno_nome": a.aluno_nome or "",
            "turma": a.turma or "",
            "contato": a.contato or "",
            "data_inicio": formatar_data(a.data_inicio),
            "data_inicio_raw": a.data_inicio.strftime("%Y-%m-%d") if a.data_inicio else "",
            "data_termino": formatar_data(a.data_termino),
            "data_termino_raw": a.data_termino.strftime("%Y-%m-%d") if a.data_termino else "",
            "observacoes": a.observacoes or "",
        })

    return {
        "sucesso": True,
        "stats": {
            "total": total,
            "disponiveis": disponiveis,
            "ocupados": ocupados,
        },
        "armarios": armarios_data
    }


# ============================================================
# API JSON DETALHES DE UM ARMÁRIO
# ============================================================

@router.get("/{armario_id}")
def obter_armario(
    armario_id: int,
    db: Session = Depends(get_db),
    admin = Depends(get_admin)
):
    armario = db.query(Armario).filter(Armario.id == armario_id, Armario.ativo == True).first()
    if not armario:
        raise HTTPException(status_code=404, detail="Armário não encontrado")

    return {
        "sucesso": True,
        "armario": {
            "id": armario.id,
            "numero": armario.numero,
            "localizacao": armario.localizacao,
            "status": armario.status,
            "aluno_nome": armario.aluno_nome or "",
            "turma": armario.turma or "",
            "contato": armario.contato or "",
            "data_inicio": formatar_data(armario.data_inicio),
            "data_inicio_raw": armario.data_inicio.strftime("%Y-%m-%d") if armario.data_inicio else "",
            "data_termino": formatar_data(armario.data_termino),
            "data_termino_raw": armario.data_termino.strftime("%Y-%m-%d") if armario.data_termino else "",
            "observacoes": armario.observacoes or "",
        }
    }


# ============================================================
# CADASTRO DE NOVO ARMÁRIO
# ============================================================

@router.post("/novo")
def criar_armario(
    request: Request,
    numero: str = Form(...),
    localizacao: str = Form(...),
    db: Session = Depends(get_db),
    admin = Depends(get_admin)
):
    num_clean = numero.strip()
    loc_clean = localizacao.strip()

    if not num_clean or not loc_clean:
        return JSONResponse(
            status_code=400,
            content={"sucesso": False, "mensagem": "Número e Localização são obrigatórios."}
        )

    if loc_clean not in BLOCOS_DISPONIVEIS:
        return JSONResponse(
            status_code=400,
            content={"sucesso": False, "mensagem": "Selecione uma localização válida: Bloco A, Bloco B ou Bloco C."}
        )

    existente = db.query(Armario).filter(
        Armario.numero.ilike(num_clean)
    ).first()

    if existente:
        if not existente.ativo:
            db.delete(existente)
            db.commit()
        else:
            return JSONResponse(
                status_code=400,
                content={"sucesso": False, "mensagem": f"O armário Nº {num_clean} já está cadastrado."}
            )

    novo_armario = Armario(
        numero=num_clean,
        localizacao=loc_clean,
        status="Livre"
    )
    db.add(novo_armario)
    db.commit()
    db.refresh(novo_armario)

    # Resposta flexível (AJAX vs Form tradicional)
    if "application/json" in request.headers.get("accept", "") or request.headers.get("x-requested-with") == "XMLHttpRequest":
        return {"sucesso": True, "mensagem": "Armário criado com sucesso!", "id": novo_armario.id}

    return RedirectResponse(url="/armarios?criado=ok", status_code=302)


# ============================================================
# RESERVA / AGENDAMENTO DE ARMÁRIO
# ============================================================

@router.post("/{armario_id}/reservar")
def reservar_armario(
    armario_id: int,
    request: Request,
    aluno_nome: str = Form(...),
    turma: Optional[str] = Form(None),
    contato: Optional[str] = Form(None),
    data_inicio: str = Form(...),
    data_termino: str = Form(...),
    observacoes: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    admin = Depends(get_admin)
):
    armario = db.query(Armario).filter(Armario.id == armario_id, Armario.ativo == True).first()
    if not armario:
        return JSONResponse(status_code=404, content={"sucesso": False, "mensagem": "Armário não encontrado."})

    if not aluno_nome.strip():
        return JSONResponse(status_code=400, content={"sucesso": False, "mensagem": "O nome do aluno é obrigatório."})

    dt_inicio = parse_data(data_inicio)
    dt_termino = parse_data(data_termino)

    if not dt_inicio or not dt_termino:
        return JSONResponse(status_code=400, content={"sucesso": False, "mensagem": "Datas de início e término válidas são obrigatórias."})

    if dt_termino < dt_inicio:
        return JSONResponse(status_code=400, content={"sucesso": False, "mensagem": "A data término não pode ser anterior à data de início."})

    armario.status = "Ocupado"
    armario.aluno_nome = aluno_nome.strip()
    armario.turma = turma.strip() if turma else None
    armario.contato = contato.strip() if contato else None
    armario.data_inicio = dt_inicio
    armario.data_termino = dt_termino
    armario.observacoes = observacoes.strip() if observacoes else None

    db.commit()

    if "application/json" in request.headers.get("accept", "") or request.headers.get("x-requested-with") == "XMLHttpRequest":
        return {"sucesso": True, "mensagem": f"Armário Nº {armario.numero} reservado para {armario.aluno_nome}!"}

    return RedirectResponse(url="/armarios?reservado=ok", status_code=302)


# ============================================================
# LIBERAÇÃO DE ARMÁRIO (REMOVER RESERVA)
# ============================================================

@router.post("/{armario_id}/liberar")
def liberar_armario(
    armario_id: int,
    request: Request,
    db: Session = Depends(get_db),
    admin = Depends(get_admin)
):
    armario = db.query(Armario).filter(Armario.id == armario_id, Armario.ativo == True).first()
    if not armario:
        return JSONResponse(status_code=404, content={"sucesso": False, "mensagem": "Armário não encontrado."})

    armario.status = "Livre"
    armario.aluno_nome = None
    armario.turma = None
    armario.contato = None
    armario.data_inicio = None
    armario.data_termino = None
    armario.observacoes = None

    db.commit()

    if "application/json" in request.headers.get("accept", "") or request.headers.get("x-requested-with") == "XMLHttpRequest":
        return {"sucesso": True, "mensagem": f"Armário Nº {armario.numero} liberado com sucesso!"}

    return RedirectResponse(url="/armarios?liberado=ok", status_code=302)


# ============================================================
# EXCLUSÃO DE ARMÁRIO
# ============================================================

@router.post("/{armario_id}/excluir")
def excluir_armario(
    armario_id: int,
    request: Request,
    db: Session = Depends(get_db),
    admin = Depends(get_admin)
):
    armario = db.query(Armario).filter(Armario.id == armario_id).first()
    if not armario:
        return JSONResponse(status_code=404, content={"sucesso": False, "mensagem": "Armário não encontrado."})

    db.delete(armario)
    db.commit()

    if "application/json" in request.headers.get("accept", "") or request.headers.get("x-requested-with") == "XMLHttpRequest":
        return {"sucesso": True, "mensagem": f"Armário Nº {armario.numero} removido com sucesso!"}

    return RedirectResponse(url="/armarios?excluido=ok", status_code=302)
