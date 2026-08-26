# controllers/produto_controller.py — CRUD produtos AAPM SENAI
import math
import os
import shutil
from fastapi import APIRouter, Depends, Request, Form, UploadFile, File, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.produto import Produto
from app.models.categoria import Categoria
from app.auth import get_usuario_logado, get_admin

router = APIRouter(prefix="/produtos", tags=["Produtos"])

templates = Jinja2Templates(directory="app/templates")

# Pasta onde as imagens serão salvas dentro de /static
UPLOAD_DIR = "app/static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)  # cria a pasta se não existir


# ============================================================
# LISTAGEM
# ============================================================

@router.get("/")
def listar_produtos(
    request: Request,
    busca: str = "",
    categoria_id: int = 0,       # 0 = todas as categorias
    mostrar: str = "ativos",     # ativos ou inativos
    ordem: str = "nome_asc",     # nome_asc, nome_desc, preco_asc, preco_desc, estoque_asc, estoque_desc
    pagina: int = 1,
    por_pagina: int = 10,
    db: Session = Depends(get_db),
    admin = Depends(get_admin)
):
    mostrar = mostrar.lower()

    if mostrar == "inativos":
        query = db.query(Produto).filter(Produto.ativo == False)
    else:
        mostrar = "ativos"
        query = db.query(Produto).filter(Produto.ativo == True)

    if busca:
        query = query.filter(Produto.nome.ilike(f"%{busca}%"))

    if categoria_id:
        query = query.filter(Produto.categoria_id == categoria_id)

    # Ordenação
    if ordem == "nome_desc":
        query = query.order_by(Produto.nome.desc())
    elif ordem == "preco_asc":
        query = query.order_by(Produto.preco.asc())
    elif ordem == "preco_desc":
        query = query.order_by(Produto.preco.desc())
    elif ordem == "estoque_asc":
        query = query.order_by(Produto.estoque_atual.asc())
    elif ordem == "estoque_desc":
        query = query.order_by(Produto.estoque_atual.desc())
    else:
        ordem = "nome_asc"
        query = query.order_by(Produto.nome.asc())

    categorias = db.query(Categoria).filter(Categoria.ativo == True).order_by(Categoria.nome).all()

    total_produtos = query.count()

    pagina = max(pagina, 1)
    por_pagina = max(por_pagina, 1)

    total_paginas = math.ceil(total_produtos / por_pagina) if total_produtos else 1
    if pagina > total_paginas:
        pagina = total_paginas

    offset = (pagina - 1) * por_pagina
    produtos = query.offset(offset).limit(por_pagina).all()

    return templates.TemplateResponse(
        request,
        "produtos/index.html",
        {
            "request":        request,
            "usuario":        admin,
            "produtos":       produtos,
            "categorias":     categorias,
            "busca":          busca,
            "categoria_id":   categoria_id,
            "mostrar":        mostrar,
            "ordem":          ordem,
            "pagina":         pagina,
            "por_pagina":     por_pagina,
            "total_paginas":  total_paginas,
            "total_produtos": total_produtos,
        }
    )


# ============================================================
# CADASTRO
# ============================================================

@router.get("/novo")
def form_novo_produto(
    request: Request,
    db: Session = Depends(get_db),
    admin = Depends(get_admin)
):
    categorias = db.query(Categoria).filter(Categoria.ativo == True).all()

    return templates.TemplateResponse(
        request,
        "produtos/form.html",
        {
            "request":    request,
            "usuario":    admin,
            "editando":   None,
            "categorias": categorias
        }
    )


@router.post("/novo")
async def criar_produto(
    request: Request,
    nome: str                  = Form(...),
    preco: float               = Form(...),
    preco_associado: float     = Form(None),
    estoque_atual: int         = Form(...),
    categoria_id: int          = Form(0),   # 0 = sem categoria
    imagem: UploadFile         = File(None), # None = campo opcional
    db: Session                = Depends(get_db),
    admin                      = Depends(get_admin)
):
    categorias = db.query(Categoria).filter(Categoria.ativo == True).all()

    # Verifica duplicidade de nome
    if db.query(Produto).filter(Produto.nome.ilike(nome)).first():
        return templates.TemplateResponse(
            request,
            "produtos/form.html",
            {
                "request":    request,
                "usuario":    admin,
                "editando":   None,
                "categorias": categorias,
                "erro":       "Já existe um produto com este nome.",
                "valores":    {"nome": nome, "preco": preco, "preco_associado": preco_associado,
                               "estoque_atual": estoque_atual,
                               "categoria_id": categoria_id}
            },
            status_code=400
        )

    # Processa o upload da imagem
    imagem_path = await _salvar_imagem(imagem)

    produto = Produto(
        nome            = nome,
        preco           = preco,
        preco_associado = preco_associado,
        estoque_atual   = estoque_atual,
        categoria_id    = categoria_id or None,  # 0 vira NULL no banco
        imagem_path     = imagem_path,
    )

    db.add(produto)
    db.commit()

    return RedirectResponse(url="/produtos?criado=ok", status_code=302)


# ============================================================
# DETALHE
# ============================================================

@router.get("/{produto_id}")
def detalhe_produto(
    produto_id: int,
    request: Request,
    db: Session = Depends(get_db),
    usuario = Depends(get_usuario_logado)
):
    produto = db.query(Produto).filter(
        Produto.id == produto_id,
        Produto.ativo == True
    ).first()

    if not produto:
        return RedirectResponse(url="/produtos", status_code=302)

    return templates.TemplateResponse(
        request,
        "produtos/detalhe.html",
        {"request": request, "usuario": usuario, "produto": produto}
    )


# ============================================================
# EDIÇÃO
# ============================================================

@router.get("/{produto_id}/editar")
def form_editar_produto(
    produto_id: int,
    request: Request,
    db: Session = Depends(get_db),
    admin = Depends(get_admin)
):
    editando   = db.query(Produto).filter(Produto.id == produto_id).first()
    categorias = db.query(Categoria).filter(Categoria.ativo == True).all()

    if not editando:
        return RedirectResponse(url="/produtos", status_code=302)

    return templates.TemplateResponse(
        request,
        "produtos/form.html",
        {
            "request":    request,
            "usuario":    admin,
            "editando":   editando,
            "categorias": categorias
        }
    )


@router.post("/{produto_id}/editar")
async def editar_produto(
    produto_id: int,
    request: Request,
    nome: str                  = Form(...),
    preco: float               = Form(...),
    preco_associado: float     = Form(None),
    estoque_atual: int         = Form(...),
    categoria_id: int          = Form(0),
    imagem: UploadFile         = File(None),
    db: Session                = Depends(get_db),
    admin                      = Depends(get_admin)
):
    editando   = db.query(Produto).filter(Produto.id == produto_id).first()
    categorias = db.query(Categoria).filter(Categoria.ativo == True).all()

    if not editando:
        return RedirectResponse(url="/produtos", status_code=302)

    # Verifica conflito de nome com outro produto
    conflito = db.query(Produto).filter(
        Produto.nome.ilike(nome),
        Produto.id != produto_id
    ).first()

    if conflito:
        return templates.TemplateResponse(
            request,
            "produtos/form.html",
            {
                "request":    request,
                "usuario":    admin,
                "editando":   editando,
                "categorias": categorias,
                "erro":       "Já existe outro produto com este nome.",
            },
            status_code=400
        )

    # Processa nova imagem — só substitui se um arquivo foi enviado
    nova_imagem_path = await _salvar_imagem(imagem)
    if nova_imagem_path:
        # Remove a imagem antiga do disco para não acumular arquivos
        _remover_imagem(editando.imagem_path)
        editando.imagem_path = nova_imagem_path

    editando.nome            = nome
    editando.preco           = preco
    editando.preco_associado = preco_associado
    editando.estoque_atual   = estoque_atual
    editando.categoria_id    = categoria_id or None

    db.commit()

    return RedirectResponse(url="/produtos?editado=ok", status_code=302)


# ============================================================
# DESATIVAR
# ============================================================

@router.post("/{produto_id}/desativar")
def desativar_produto(
    produto_id: int,
    db: Session = Depends(get_db),
    admin = Depends(get_admin)
):
    produto = db.query(Produto).filter(Produto.id == produto_id).first()

    if produto:
        produto.ativo = False
        db.commit()

    return RedirectResponse(url="/produtos?desativado=ok", status_code=302)


# ============================================================
# REATIVAR
# ============================================================

@router.post("/{produto_id}/reativar")
def reativar_produto(
    produto_id: int,
    db: Session = Depends(get_db),
    admin = Depends(get_admin)
):
    produto = db.query(Produto).filter(Produto.id == produto_id).first()

    if produto:
        produto.ativo = True
        db.commit()

    return RedirectResponse(url="/produtos?reativado=ok", status_code=302)


# ============================================================
# TOGGLE ATIVO
# ============================================================

@router.post("/{produto_id}/toggle-ativo")
def toggle_ativo(
    produto_id: int,
    mostrar: str = Form("ativos"),
    busca: str = Form(""),
    categoria_id: int = Form(0),
    db: Session = Depends(get_db),
    admin = Depends(get_admin)
):
    produto = db.query(Produto).filter(Produto.id == produto_id).first()
    status = None

    if produto:
        produto.ativo = not produto.ativo
        db.commit()
        status = "reativado" if produto.ativo else "desativado"

    params = [f"mostrar={mostrar}"]
    if busca:
        params.append(f"busca={busca}")
    if categoria_id:
        params.append(f"categoria_id={categoria_id}")
    if status:
        params.append(f"{status}=ok")

    redirect_url = "/produtos"
    if params:
        redirect_url += "?" + "&".join(params)

    return RedirectResponse(url=redirect_url, status_code=302)


# ============================================================
# FUNÇÕES AUXILIARES DE IMAGEM
# ============================================================

async def _salvar_imagem(imagem: UploadFile | None) -> str | None:
    """
    Salva o arquivo enviado em /static/uploads/ e retorna
    o path relativo para guardar no banco.

    Retorna None se nenhum arquivo foi enviado ou se o
    arquivo enviado estiver vazio (campo deixado em branco).
    """
    # UploadFile com filename vazio = campo não preenchido
    if not imagem or not imagem.filename:
        return None

    # Valida a extensão — aceita apenas imagens
    extensoes_permitidas = {".jpg", ".jpeg", ".png", ".webp"}
    _, ext = os.path.splitext(imagem.filename.lower())

    if ext not in extensoes_permitidas:
        return None  # ignora silenciosamente — pode virar erro em produção

    # Garante nome de arquivo único usando o nome original
    # Em produção: use uuid4() para evitar colisões e exposição de nomes
    nome_arquivo = f"{imagem.filename}"
    caminho_completo = os.path.join(UPLOAD_DIR, nome_arquivo)

    # Salva o arquivo no disco
    with open(caminho_completo, "wb") as buffer:
        shutil.copyfileobj(imagem.file, buffer)

    # Retorna o path relativo ao /static (para montar a URL)
    return f"uploads/{nome_arquivo}"


def _remover_imagem(imagem_path: str | None) -> None:
    """Remove o arquivo de imagem do disco se ele existir."""
    if not imagem_path:
        return

    caminho = os.path.join("app/static", imagem_path)

    if os.path.exists(caminho):
        os.remove(caminho)