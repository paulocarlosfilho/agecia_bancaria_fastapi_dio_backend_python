from typing import Optional
from pydantic import BaseModel, Field
import enum

class AccountType(str, enum.Enum):
    CHECKING = "checking"
    SAVINGS = "savings"

class AccountBase(BaseModel):
    account_number: Optional[str] = Field(None, example="CC-0001-01", description="Número único da conta")
    nickname: Optional[str] = Field(None, example="Minha Reserva", description="Apelido opcional para a conta")
    account_type: Optional[AccountType] = Field(AccountType.CHECKING, example="checking", description="Tipo da conta (Corrente ou Poupança)")

class AccountCreate(BaseModel):
    account_type: AccountType = Field(AccountType.CHECKING, example="checking", description="Tipo da conta a ser criada")

class AccountUpdate(BaseModel):
    nickname: Optional[str] = Field(None, example="Conta de Viagens", description="Novo apelido para a conta")

class AccountInDBBase(AccountBase):
    id: int
    balance: float
    is_active: int
    owner_id: int

    class Config:
        from_attributes = True

class Account(AccountInDBBase):
    pass
