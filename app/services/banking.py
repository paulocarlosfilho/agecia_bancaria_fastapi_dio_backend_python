from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from datetime import datetime, time as dt_time
from fastapi import HTTPException, status
from app.models.models import Account, Transaction, TransactionType, User, AccountType
from app.schemas.transaction import TransactionCreate, TransferCreate
from app.schemas.account import AccountCreate as AccountCreateSchema
from app.core.logging import logger

class BankingService:
    # Business Rules (DIO Challenge Compliance)
    WITHDRAWAL_LIMIT_PER_DAY = 3
    MAX_WITHDRAWAL_AMOUNT = 500.0

    @staticmethod
    async def get_account(db: AsyncSession, account_id: int, user_id: int) -> Account:
        logger.info(f"Fetching account {account_id} for user {user_id}")
        result = await db.execute(
            select(Account).filter(
                Account.id == account_id, 
                Account.owner_id == user_id,
                Account.is_active == 1
            )
        )
        account = result.scalars().first()
        if not account:
            logger.warning(f"Account {account_id} not found or inactive for user {user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account not found, inactive or not owned by user"
            )
        return account

    @staticmethod
    async def get_account_by_number(db: AsyncSession, account_number: str) -> Account:
        result = await db.execute(
            select(Account).filter(
                Account.account_number == account_number,
                Account.is_active == 1
            )
        )
        account = result.scalars().first()
        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Destination account {account_number} not found or inactive"
            )
        return account

    @staticmethod
    async def get_user_accounts(db: AsyncSession, user_id: int) -> List[Account]:
        logger.info(f"Fetching all active accounts for user {user_id}")
        result = await db.execute(
            select(Account).filter(Account.owner_id == user_id, Account.is_active == 1)
        )
        return result.scalars().all()

    @staticmethod
    async def update_account(db: AsyncSession, account_id: int, user_id: int, nickname: str) -> Account:
        account = await BankingService.get_account(db, account_id, user_id)
        account.nickname = nickname
        await db.commit()
        await db.refresh(account)
        return account

    @staticmethod
    async def deactivate_account(db: AsyncSession, account_id: int, user_id: int) -> bool:
        account = await BankingService.get_account(db, account_id, user_id)
        if account.balance != 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot close an account with remaining balance. Please withdraw or transfer first."
            )
        account.is_active = 0
        await db.commit()
        return True

    @staticmethod
    async def create_account(db: AsyncSession, user_id: int, account_in: AccountCreateSchema) -> Account:
        logger.info(f"Creating new {account_in.account_type} account for user {user_id}")
        
        # Determine prefix and count existing accounts of this type for this user
        prefix = "CC" if account_in.account_type == AccountType.CHECKING else "CP"
        
        result = await db.execute(
            select(func.count(Account.id)).filter(
                Account.owner_id == user_id,
                Account.account_type == account_in.account_type
            )
        )
        count = result.scalar()
        suffix = count + 1
        
        account_number = f"{prefix}-{user_id:04d}-{suffix:02d}"
        
        new_account = Account(
            account_number=account_number,
            account_type=account_in.account_type,
            owner_id=user_id,
            balance=0.0
        )
        db.add(new_account)
        try:
            await db.commit()
            await db.refresh(new_account)
            logger.info(f"Account {new_account.account_number} created for user {user_id}")
            return new_account
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to create account: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not create new account"
            )

    @staticmethod
    async def create_transaction(
        db: AsyncSession, 
        transaction_in: TransactionCreate, 
        user_id: int
    ) -> Transaction:
        logger.info(f"Creating {transaction_in.type} of {transaction_in.amount} for account {transaction_in.account_id}")
        account = await BankingService.get_account(db, transaction_in.account_id, user_id)

        if transaction_in.type == TransactionType.WITHDRAWAL:
            # Rule 1: Max amount per withdrawal
            if transaction_in.amount > BankingService.MAX_WITHDRAWAL_AMOUNT:
                logger.warning(f"Withdrawal amount {transaction_in.amount} exceeds limit of {BankingService.MAX_WITHDRAWAL_AMOUNT}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Maximum withdrawal amount is ${BankingService.MAX_WITHDRAWAL_AMOUNT}"
                )

            # Rule 2: Daily limit of withdrawals
            today_start = datetime.combine(datetime.now().date(), dt_time.min)
            result = await db.execute(
                select(func.count(Transaction.id)).filter(
                    Transaction.account_id == transaction_in.account_id,
                    Transaction.type == TransactionType.WITHDRAWAL,
                    Transaction.created_at >= today_start
                )
            )
            withdrawals_today = result.scalar()
            if withdrawals_today >= BankingService.WITHDRAWAL_LIMIT_PER_DAY:
                logger.warning(f"Daily withdrawal limit reached for account {account.id}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Daily withdrawal limit of {BankingService.WITHDRAWAL_LIMIT_PER_DAY} reached"
                )

            # Rule 3: Insufficient balance
            if account.balance < transaction_in.amount:
                logger.warning(f"Insufficient balance for withdrawal: account {account.id}, balance {account.balance}, requested {transaction_in.amount}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Insufficient balance"
                )
            account.balance -= transaction_in.amount
        else:
            account.balance += transaction_in.amount

        transaction = Transaction(
            account_id=transaction_in.account_id,
            amount=transaction_in.amount,
            type=transaction_in.type
        )
        
        db.add(transaction)
        await db.commit()
        await db.refresh(transaction)
        logger.info(f"Transaction {transaction.id} created successfully")
        return transaction

    @staticmethod
    async def transfer(
        db: AsyncSession,
        transfer_in: TransferCreate,
        user_id: int
    ) -> Transaction:
        logger.info(f"Initiating transfer of {transfer_in.amount} from {transfer_in.source_account_id} to {transfer_in.destination_account_number}")
        
        source_account = await BankingService.get_account(db, transfer_in.source_account_id, user_id)
        dest_account = await BankingService.get_account_by_number(db, transfer_in.destination_account_number)

        if source_account.id == dest_account.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot transfer to the same account"
            )

        if source_account.balance < transfer_in.amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient balance for transfer"
            )

        # Execute transfer
        source_account.balance -= transfer_in.amount
        dest_account.balance += transfer_in.amount

        # Create transaction records
        tx_source = Transaction(
            account_id=source_account.id,
            amount=transfer_in.amount,
            type=TransactionType.WITHDRAWAL,
            description=f"Transfer to {dest_account.account_number}: {transfer_in.description}"
        )
        tx_dest = Transaction(
            account_id=dest_account.id,
            amount=transfer_in.amount,
            type=TransactionType.DEPOSIT,
            description=f"Transfer from {source_account.account_number}: {transfer_in.description}"
        )

        db.add(tx_source)
        db.add(tx_dest)
        
        try:
            await db.commit()
            await db.refresh(tx_source)
            logger.info(f"Transfer successful: TX {tx_source.id}")
            return tx_source
        except Exception as e:
            await db.rollback()
            logger.error(f"Transfer failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Transfer failed due to an internal error"
            )

    @staticmethod
    async def get_statement(
        db: AsyncSession, 
        account_id: int, 
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ):
        account = await BankingService.get_account(db, account_id, user_id)
        result = await db.execute(
            select(Transaction)
            .filter(Transaction.account_id == account_id)
            .order_by(Transaction.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
