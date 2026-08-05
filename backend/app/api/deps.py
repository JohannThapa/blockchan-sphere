from collections.abc import Generator
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, APIKeyHeader
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError
from sqlmodel import Session
from typing import Optional
import uuid
from app.core import security
from app.core.config import settings
from app.core.db import engine
from app.models.users.user import TokenPayload, User
from app.services.auth_service.identity import authenticate_api_key, get_permissions_for_role

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def get_db() -> Generator[Session]:
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db)]
TokenDep = Annotated[str, Depends(reusable_oauth2)]
ApiKeyDep = Annotated[Optional[str], Depends(api_key_header)]


def get_current_user(session: SessionDep, token: TokenDep) -> User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except InvalidTokenError, ValidationError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user = session.get(User, token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user

def get_current_user_with_api_key(
    session: SessionDep,
    api_key: ApiKeyDep,
) -> User:
    """Authenticate using an API key (X-API-Key header). Returns the associated user."""
    if not api_key:
        raise HTTPException(status_code=401, detail="API Key required")
    key_obj = authenticate_api_key(session, api_key)
    if not key_obj:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    if not key_obj.user_id:
        raise HTTPException(status_code=401, detail="API key not bound to a user")
    user = session.get(User, key_obj.user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User inactive or not found")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
CurrentUserApiKey = Annotated[User, Depends(get_current_user_with_api_key)]


def get_current_active_superuser(current_user: CurrentUser) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="The user doesn't have enough privileges"
        )
    return current_user

def require_permission(
    session: SessionDep,
    current_user: CurrentUser,
    permission_code: str,
) -> None:
    """Raise 403 if current_user does not have the given permission."""
    if current_user.is_superuser:
        return
    # Get all permissions for the user's role
    perms = get_permissions_for_role(session, current_user.role)
    if any(p.code == permission_code for p in perms):
        return
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=f"Missing required permission: {permission_code}",
    )
def PermissionDep(permission_code: str):
    """Dependency that checks a specific permission."""
    async def _check(
        session: SessionDep,
        current_user: CurrentUser,
    ) -> None:
        require_permission(session, current_user, permission_code)
    return _check



def check_organization_access(
    user: User,
    resource_org_id: Optional[uuid.UUID],
) -> None:
    """
    Ensure the user belongs to the same organization as the resource.
    Superusers are exempt.
    """
    if user.is_superuser:
        return
    if not user.organization_id:
        raise HTTPException(403, "User is not assigned to any organization")
    if resource_org_id is None:
        # For resources that might be global (e.g., system settings), allow if admin?
        # For now, we'll treat null as "no org" and allow only superusers.
        raise HTTPException(403, "This resource is not organization-scoped")
    if user.organization_id != resource_org_id:
        raise HTTPException(403, "Access denied: resource belongs to another organization")

CurrentSuperuser = Annotated[User, Depends(get_current_active_superuser)]