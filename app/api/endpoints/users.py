from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.api import deps
from app.services.user import UserService
from app.schemas.user import User, UserCreate

router = APIRouter()

@router.post("/", response_model=User, summary="Registrar novo cliente")
async def create_user(
    *,
    db: AsyncSession = Depends(get_db),
    user_in: UserCreate
) -> Any:
    """
    Cadastra um novo usuário no sistema. 
    Ao se registrar, uma **Conta Corrente** inicial é criada automaticamente para o usuário.
    """
    user = await UserService.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )
    return await UserService.create_user(db, user_in=user_in)

@router.get("/me", response_model=User, summary="Consultar meu perfil")
async def read_user_me(
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Retorna os dados do usuário que está atualmente autenticado via token JWT.
    """
    return current_user
