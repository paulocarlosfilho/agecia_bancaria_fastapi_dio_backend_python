from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.models import User, Account, AccountType
from app.schemas.user import UserCreate
from app.core.security import get_password_hash

class UserService:
    @staticmethod
    async def create_user(db: AsyncSession, user_in: UserCreate) -> User:
        hashed_password = get_password_hash(user_in.password)
        db_user = User(
            email=user_in.email,
            full_name=user_in.full_name,
            hashed_password=hashed_password
        )
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        
        # Create a default checking account for the new user
        new_account = Account(
            account_number=f"CC-{db_user.id:04d}-01",
            account_type=AccountType.CHECKING,
            owner_id=db_user.id,
            balance=0.0
        )
        db.add(new_account)
        await db.commit()
        
        return db_user

    @staticmethod
    async def get_by_email(db: AsyncSession, email: str) -> User:
        result = await db.execute(select(User).filter(User.email == email))
        return result.scalars().first()
