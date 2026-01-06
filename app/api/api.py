from fastapi import APIRouter
from app.api.endpoints import login, users, banking, utils

api_router = APIRouter()
api_router.include_router(login.router, tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["User Management"])
api_router.include_router(banking.router, prefix="/banking", tags=["Banking Operations"])
api_router.include_router(utils.router, tags=["System Health"])
