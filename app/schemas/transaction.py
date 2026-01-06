from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from app.models.models import TransactionType

class TransactionBase(BaseModel):
    amount: float = Field(..., gt=0, example=150.50, description="Valor da transação (deve ser positivo)")
    type: TransactionType = Field(..., example="deposit", description="Tipo da operação (deposit ou withdrawal)")
    description: Optional[str] = Field(None, example="Pagamento de serviço", description="Descrição opcional")

class TransactionCreate(TransactionBase):
    account_id: int = Field(..., example=1, description="ID da conta onde a transação será realizada")

class TransferCreate(BaseModel):
    source_account_id: int = Field(..., example=1, description="ID da conta de origem (sua conta)")
    destination_account_number: str = Field(..., example="CC-0002-01", description="Número da conta de destino")
    amount: float = Field(..., gt=0, example=200.00, description="Valor a ser transferido")
    description: str = Field("Transferência bancária", example="Presente", description="Motivo da transferência")

class TransactionInDBBase(TransactionBase):
    id: int
    account_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class Transaction(TransactionInDBBase):
    pass
