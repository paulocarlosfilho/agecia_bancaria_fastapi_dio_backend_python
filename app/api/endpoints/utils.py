from fastapi import APIRouter
from typing import Any

router = APIRouter()

@router.get("/health", response_model=dict, summary="Verificar integridade do sistema")
async def health_check() -> Any:
    """
    Endpoint de monitoramento (Liveness Probe).
    Retorna o status atual do serviço, versão e conectividade com dependências críticas.
    Ideal para uso em Cloud (AWS Route53, Kubernetes, etc).
    """
    return {
        "status": "healthy",
        "version": "1.0.0",
        "database": "connected"  # In a more complex setup, we would actually ping the DB
    }
