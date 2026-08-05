from app.api.routes.auth.login import router as auth_router
from app.api.routes.auth.users import router as user_router
from app.api.routes.auth.private import router as private_router
from app.api.routes.auth.identity import router as identity_router

__all__ = ["auth_router", "user_router", "private_router", "identity_router"]
