from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from app.auth import get_usuario_opcional, get_admin

from app.controllers import auth_controller
from app.controllers import usuario_controller
from app.controllers import categoria_controller
from app.controllers import produto_controller
from app.controllers import armario_controller

app = FastAPI(title="Projeto AAPM")

app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")

app.include_router(auth_controller.router)
app.include_router(usuario_controller.router)
app.include_router(categoria_controller.router)
app.include_router(produto_controller.router)
app.include_router(armario_controller.router)

from sqlalchemy.orm import Session
from app.database import get_db
from app.models.produto import Produto
from app.models.categoria import Categoria

@app.get("/")
def tela_inicial(
    request: Request,
    usuario = Depends(get_usuario_opcional),
    db: Session = Depends(get_db)
):
    #Tela não logado
    if usuario is None:
        return templates.TemplateResponse(
            request,
            "auth/login.html",
            {"request": request}
        )
    
    # Buscar produtos ativos cuja categoria também esteja ativa
    produtos = (
        db.query(Produto)
        .join(Categoria, Produto.categoria_id == Categoria.id)
        .filter(Produto.ativo == True, Categoria.ativo == True)
        .all()
    )
    categorias = db.query(Categoria).filter(Categoria.ativo == True).all()

    #logado - exibir a tela de funcionario
    return templates.TemplateResponse(
        request,
        "home.html",
        {
            "request": request, 
            "usuario": usuario,
            "produtos": produtos,
            "categorias": categorias
        }
    )

@app.get("/painel", response_class=HTMLResponse)
async def painel(
    request: Request,
    admin = Depends(get_admin)
):
    return templates.TemplateResponse(
        request,
        "painel/index.html",
        {"request": request, "usuario": admin}
    )


# Tratamento customizado para erros HTTP (401 / 403)
from fastapi.responses import PlainTextResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    # Tratamento específico para HTTPExceptions (401/403/404)
    status_code = exc.status_code
    # tentar obter usuário logado (opcional) para mostrar no header
    try:
        usuario = get_usuario_opcional(request)
    except Exception:
        usuario = None
    if status_code == 403:
        return templates.TemplateResponse(
            request,
            "errors/403.html",
            {"request": request, "detail": exc.detail, "usuario": usuario},
            status_code=403
        )
    if status_code == 401:
        return templates.TemplateResponse(
            request,
            "auth/login.html",
            {"request": request, "detail": exc.detail, "usuario": usuario},
            status_code=401
        )
    if status_code == 404:
        return templates.TemplateResponse(
            request,
            "errors/404.html",
            {"request": request, "detail": exc.detail, "usuario": usuario},
            status_code=404
        )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    # Fallback genérico para exceções não tratadas
    return PlainTextResponse(str(getattr(exc, 'detail', str(exc))), status_code=getattr(exc, 'status_code', 500))

