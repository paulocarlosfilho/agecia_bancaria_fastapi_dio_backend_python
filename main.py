from fastapi import FastAPI, Request, status
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.cors import CORSMiddleware
import os

from app.api.api import api_router
from app.core.config import settings
from app.models.base import Base
from app.db.session import engine

description = """
🚀 **Banco Moderno API** - Sistema Bancário Profissional Assíncrono.

Esta API foi construída com **FastAPI** para oferecer uma experiência bancária robusta, segura e extremamente rápida.

### Você será capaz de fazer:
* **Gestão de Clientes**: Registrar novos usuários e gerenciar perfis.
* **Múltiplas Contas**: Criar contas Correntes (CC) e Poupança (CP) dinamicamente.
* **Operações Financeiras**:
    * Realizar depósitos imediatos.
    * Efetuar saques com validação de saldo e limites de segurança.
    * Transferir fundos entre contas com garantia de transação.
* **Extratos Detalhados**: Consultar histórico de transações com paginação de alta performance.
* **Segurança Bancária**: Autenticação via JWT com proteção de rotas sensíveis.

---

"""

tags_metadata = [
    {
        "name": "Authentication",
        "description": "🔑 **Segurança em primeiro lugar**. Obtenha seu token de acesso para desbloquear as operações bancárias.",
    },
    {
        "name": "User Management",
        "description": "👤 **Gestão de Clientes**. Cadastre-se no nosso banco e consulte seus dados cadastrais.",
    },
    {
        "name": "Banking Operations",
        "description": "💰 **O Coração do Banco**. Onde a mágica acontece: contas, transferências, saques e depósitos.",
    },
    {
        "name": "System Health",
        "description": "🛠️ **Monitoramento**. Ferramentas técnicas para garantir que o banco nunca fique fora do ar.",
    },
]

app = FastAPI(
    title="Banco Moderno API 🏦",
    description=description,
    version="2.0.0",
    openapi_tags=tags_metadata,
    openapi_url=f"/api/v1/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Custom Exception Handlers for "Bonitinho" Errors
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.status_code,
                "message": exc.detail,
                "type": "http_error"
            }
        },
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    # Format validation errors into a single readable string
    messages = []
    for error in errors:
        loc = " -> ".join([str(x) for x in error["loc"][1:]])
        msg = error["msg"]
        messages.append(f"{loc}: {msg}" if loc else msg)
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error": {
                "code": 422,
                "message": "Erro de validação: " + "; ".join(messages),
                "type": "validation_error"
            }
        },
    )

# Templates
templates = Jinja2Templates(directory="app/templates")

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

@app.on_event("startup")
async def startup():
    # In a real production environment, you should use Alembic for migrations.
    # We create the tables on startup for ease of setup.
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

app.include_router(api_router, prefix="/api/v1")

# Serve static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return RedirectResponse(url="/login")

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("auth/login.html", {"request": request})

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("auth/register.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    return templates.TemplateResponse("dashboard/index.html", {"request": request})
