# app/schemas/identity.py
from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field

from app.models.users.user import PlanTier, UserRole, AuthProvider


# ---------- Organization ----------
class OrganizationBase(BaseModel):
    name: str
    slug: str
    plan_tier: PlanTier = PlanTier.free
    is_active: bool = True


class OrganizationCreate(OrganizationBase):
    pass


class OrganizationUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    plan_tier: Optional[PlanTier] = None
    is_active: Optional[bool] = None


class OrganizationRead(OrganizationBase):
    id: UUID
    created_at: datetime
    updated_at: datetime


# ---------- User ----------
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    role: UserRole = UserRole.viewer
    is_active: bool = True
    is_superuser: bool = False
    mfa_enabled: bool = False


class UserCreate(UserBase):
    password: str
    organization_id: Optional[UUID] = None


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None
    mfa_enabled: Optional[bool] = None
    password: Optional[str] = None
    organization_id: Optional[UUID] = None


class UserRead(UserBase):
    id: UUID
    organization_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime


# ---------- AuthIdentity ----------
class AuthIdentityBase(BaseModel):
    provider: AuthProvider
    provider_subject: str
    provider_metadata: Dict[str, Any] = {}


class AuthIdentityCreate(AuthIdentityBase):
    user_id: UUID


class AuthIdentityRead(AuthIdentityBase):
    id: UUID
    user_id: UUID
    created_at: datetime


# ---------- UserDevice ----------
class UserDeviceBase(BaseModel):
    device_fingerprint: str
    user_agent: Optional[str] = None
    last_ip: Optional[str] = None
    is_trusted: bool = False
    last_seen_at: Optional[datetime] = None


class UserDeviceCreate(UserDeviceBase):
    user_id: UUID


class UserDeviceUpdate(BaseModel):
    user_agent: Optional[str] = None
    last_ip: Optional[str] = None
    is_trusted: Optional[bool] = None
    last_seen_at: Optional[datetime] = None


class UserDeviceRead(UserDeviceBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime


# ---------- APIKey ----------
class APIKeyBase(BaseModel):
    name: str
    scopes: List[str] = []
    expires_at: Optional[datetime] = None


class APIKeyCreate(APIKeyBase):
    organization_id: UUID
    user_id: Optional[UUID] = None


class APIKeyUpdate(BaseModel):
    name: Optional[str] = None
    scopes: Optional[List[str]] = None
    is_active: Optional[bool] = None
    expires_at: Optional[datetime] = None


class APIKeyRead(APIKeyBase):
    id: UUID
    key_prefix: str
    is_active: bool
    last_used_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    organization_id: UUID
    user_id: Optional[UUID]


class APIKeyWithPlain(APIKeyRead):
    plain_key: str


# ---------- Permission ----------
class PermissionBase(BaseModel):
    code: str
    description: Optional[str] = None


class PermissionCreate(PermissionBase):
    pass


class PermissionRead(PermissionBase):
    id: UUID
    created_at: datetime
    updated_at: datetime


# ---------- RolePermission ----------
class RolePermissionBase(BaseModel):
    role: UserRole
    permission_id: UUID


class RolePermissionCreate(RolePermissionBase):
    pass


class RolePermissionRead(RolePermissionBase):
    id: UUID


# ---------- AuditLog ----------
class AuditLogBase(BaseModel):
    action: str
    resource_type: str
    resource_id: str
    ip_address: Optional[str] = None
    metadata: Dict[str, Any] = {}


class AuditLogCreate(AuditLogBase):
    organization_id: Optional[UUID] = None
    actor_user_id: Optional[UUID] = None


class AuditLogRead(AuditLogBase):
    id: UUID
    organization_id: Optional[UUID]
    actor_user_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime