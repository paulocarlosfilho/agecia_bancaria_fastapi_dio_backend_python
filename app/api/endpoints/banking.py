from typing import Any, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.api import deps
from app.services.banking import BankingService
from app.schemas.transaction import Transaction, TransactionCreate, TransferCreate
from app.schemas.account import Account, AccountUpdate, AccountCreate
from app.models.models import User

router = APIRouter()

@router.get("/accounts", response_model=List[Account], summary="Listar todas as contas")
async def get_accounts(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Retorna uma lista de todas as contas ativas vinculadas ao usuário autenticado.
    Exibe saldo, tipo de conta (Corrente/Poupança) e apelido.
    """
    return await BankingService.get_user_accounts(db, user_id=current_user.id)

@router.post("/accounts", response_model=Account, summary="Criar nova conta")
async def create_account(
    account_in: AccountCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Cria uma nova conta bancária para o usuário.
    - **account_type**: 'checking' (Corrente) ou 'savings' (Poupança).
    - A numeração é gerada automaticamente (Ex: CC-0001-01).
    """
    return await BankingService.create_account(db, user_id=current_user.id, account_in=account_in)

@router.get("/accounts/{account_id}", response_model=Account, summary="Ver detalhes da conta")
async def get_account(
    account_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Busca informações detalhadas de uma conta específica pelo seu ID.
    O usuário deve ser o proprietário da conta.
    """
    return await BankingService.get_account(db, account_id=account_id, user_id=current_user.id)

@router.patch("/accounts/{account_id}", response_model=Account, summary="Atualizar apelido da conta")
async def update_account(
    account_id: int,
    account_in: AccountUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Permite alterar o apelido (nickname) de uma conta para facilitar a identificação.
    """
    return await BankingService.update_account(
        db, account_id=account_id, user_id=current_user.id, nickname=account_in.nickname
    )

@router.delete("/accounts/{account_id}", summary="Encerrar conta")
async def close_account(
    account_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Desativa uma conta bancária. 
    **Nota**: A conta só pode ser encerrada se o saldo for exatamente R$ 0,00.
    """
    await BankingService.deactivate_account(db, account_id=account_id, user_id=current_user.id)
    return {"detail": "Account closed successfully"}

@router.post("/transactions", response_model=Transaction, summary="Realizar Depósito ou Saque")
async def create_transaction(
    *,
    db: AsyncSession = Depends(get_db),
    transaction_in: TransactionCreate,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Executa uma operação financeira simples:
    - **deposit**: Adiciona fundos à conta.
    - **withdrawal**: Remove fundos (Sujeito a limite de R$ 500/dia e saldo disponível).
    """
    return await BankingService.create_transaction(
        db, transaction_in=transaction_in, user_id=current_user.id
    )

@router.post("/transfer", response_model=Transaction, summary="Transferência entre contas")
async def transfer(
    *,
    db: AsyncSession = Depends(get_db),
    transfer_in: TransferCreate,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Transfere valores entre duas contas.
    - A conta de origem deve pertencer ao usuário autenticado.
    - A conta de destino pode ser de qualquer usuário (via número da conta).
    """
    return await BankingService.transfer(
        db, transfer_in=transfer_in, user_id=current_user.id
    )

@router.get("/statement/{account_id}", response_model=List[Transaction], summary="Consultar Extrato")
async def get_statement(
    account_id: int,
    skip: int = Query(0, ge=0, description="Número de registros para pular"),
    limit: int = Query(100, ge=1, le=1000, description="Máximo de registros por página"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Retorna o histórico de transações de uma conta.
    Inclui depósitos, saques e transferências realizadas ou recebidas.
    """
    return await BankingService.get_statement(
        db, account_id=account_id, user_id=current_user.id, skip=skip, limit=limit
    )
