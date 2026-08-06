from fastapi import APIRouter
from app.api.routes.auth import auth_router, private_router, user_router, identity_router
from app.api.routes import items, utils
from app.api.routes.blockchain.blockchain import router as blockchain_router

from app.core.config import settings

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(private_router)
api_router.include_router(user_router)
api_router.include_router(identity_router)
api_router.include_router(blockchain_router)
api_router.include_router(items.router)
api_router.include_router(utils.router)

if settings.ENVIRONMENT == "local":
    api_router.include_router(private_router)