import enum
import uuid
from datetime import datetime, timezone
from typing import List, Optional

from pydantic import EmailStr
from sqlalchemy import DateTime, Index, String, Enum as SAEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, Relationship, SQLModel


def get_datetime_utc() -> datetime:
    return datetime.now(timezone.utc)


class UUIDMixin(SQLModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)


class TimestampMixin(SQLModel):
    created_at: datetime = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),
        nullable=False,
    )
    updated_at: datetime = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),
        nullable=False,
    )


class PlanTier(str, enum.Enum):
    free = "free"
    pro = "pro"
    enterprise = "enterprise"


class UserRole(str, enum.Enum):
    owner = "owner"
    admin = "admin"
    analyst = "analyst"
    compliance_officer = "compliance_officer"
    viewer = "viewer"


class AuthProvider(str, enum.Enum):
    password = "password"
    oauth_google = "oauth_google"
    oauth_github = "oauth_github"
    passkey = "passkey"
    siwe = "siwe"


class UserBase(SQLModel):
    """Shared base fields for User schema and DB model."""

    email: EmailStr = Field(unique=True, index=True)
    full_name: Optional[str] = None
    role: UserRole = Field(
        default=UserRole.viewer,
        sa_type=SAEnum(UserRole, native_enum=False),
    )
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)
    mfa_enabled: bool = Field(default=False)
    organization_id: Optional[uuid.UUID] = Field(
        default=None, foreign_key="organizations.id"
    )


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=128)
    full_name: Optional[str] = Field(default=None, max_length=255)


class UserUpdate(SQLModel):
    email: Optional[EmailStr] = Field(default=None, max_length=255)
    full_name: Optional[str] = Field(default=None, max_length=255)
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None
    mfa_enabled: Optional[bool] = None
    organization_id: Optional[uuid.UUID] = None
    password: Optional[str] = Field(default=None, min_length=8, max_length=128)


class UserUpdateMe(SQLModel):
    full_name: Optional[str] = Field(default=None, max_length=255)
    email: Optional[EmailStr] = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)


class User(UserBase, UUIDMixin, TimestampMixin, table=True):
    __tablename__ = "users"

    hashed_password: Optional[str] = Field(default=None, nullable=True)
    mfa_secret: Optional[str] = Field(default=None, nullable=True)

    # SQLModel Relationships
    organization: Optional["Organization"] = Relationship(back_populates="users")
    auth_identities: List["AuthIdentity"] = Relationship(back_populates="user")
    devices: List["UserDevice"] = Relationship(back_populates="user")
    items: List["Item"] = Relationship(back_populates="owner", cascade_delete=True)


class UserPublic(UserBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class UsersPublic(SQLModel):
    data: List[UserPublic]
    count: int


class Organization(UUIDMixin, TimestampMixin, SQLModel, table=True):
    __tablename__ = "organizations"

    name: str = Field(sa_type=String(255), nullable=False)
    slug: str = Field(sa_type=String(100), unique=True, index=True, nullable=False)
    plan_tier: PlanTier = Field(
        default=PlanTier.free,
        sa_type=SAEnum(PlanTier, native_enum=False),
        nullable=False,
    )
    is_active: bool = Field(default=True)

    users: List["User"] = Relationship(back_populates="organization")
    api_keys: List["APIKey"] = Relationship(back_populates="organization")
    audit_logs: List["AuditLog"] = Relationship(back_populates="organization")


class AuthIdentity(UUIDMixin, TimestampMixin, SQLModel, table=True):
    __tablename__ = "auth_identities"

    user_id: uuid.UUID = Field(foreign_key="users.id", nullable=False)
    user: Optional["User"] = Relationship(back_populates="auth_identities")

    provider: AuthProvider = Field(
        sa_type=SAEnum(AuthProvider, native_enum=False), nullable=False
    )
    provider_subject: str = Field(sa_type=String(255), nullable=False)
    provider_metadata: dict = Field(default_factory=dict, sa_type=JSONB)


class UserDevice(UUIDMixin, TimestampMixin, SQLModel, table=True):
    __tablename__ = "user_devices"

    user_id: uuid.UUID = Field(foreign_key="users.id", nullable=False)
    user: Optional["User"] = Relationship(back_populates="devices")

    device_fingerprint: str = Field(sa_type=String(255), index=True)
    user_agent: Optional[str] = Field(default=None, sa_type=String(512))
    last_ip: Optional[str] = Field(default=None, sa_type=String(64))
    is_trusted: bool = Field(default=False)
    last_seen_at: Optional[str] = Field(default=None)


class APIKey(UUIDMixin, TimestampMixin, SQLModel, table=True):
    __tablename__ = "api_keys"

    organization_id: uuid.UUID = Field(foreign_key="organizations.id", nullable=False)
    user_id: Optional[uuid.UUID] = Field(default=None, foreign_key="users.id")
    name: str = Field(sa_type=String(255), nullable=False)
    key_prefix: str = Field(sa_type=String(16), index=True, nullable=False)
    hashed_key: str = Field(sa_type=String(255), nullable=False)
    scopes: list = Field(default_factory=list, sa_type=JSONB)
    is_active: bool = Field(default=True)
    last_used_at: Optional[datetime] = Field(
        default=None, sa_type=DateTime(timezone=True)
    )
    expires_at: Optional[datetime] = Field(
        default=None, sa_type=DateTime(timezone=True)
    )

    organization: Optional["Organization"] = Relationship(back_populates="api_keys")


class Permission(UUIDMixin, TimestampMixin, SQLModel, table=True):
    __tablename__ = "permissions"

    code: str = Field(sa_type=String(100), unique=True, nullable=False)
    description: Optional[str] = Field(default=None, sa_type=String(255))


class RolePermission(UUIDMixin, TimestampMixin, SQLModel, table=True):
    __tablename__ = "role_permissions"
    __table_args__ = (
        Index("uq_role_permission", "role", "permission_id", unique=True),
    )

    role: UserRole = Field(sa_type=SAEnum(UserRole, native_enum=False), nullable=False)
    permission_id: uuid.UUID = Field(foreign_key="permissions.id", nullable=False)


class AuditLog(UUIDMixin, TimestampMixin, SQLModel, table=True):
    __tablename__ = "audit_logs"

    organization_id: Optional[uuid.UUID] = Field(
        default=None, foreign_key="organizations.id"
    )
    actor_user_id: Optional[uuid.UUID] = Field(default=None, foreign_key="users.id")
    action: str = Field(sa_type=String(100), index=True, nullable=False)
    resource_type: str = Field(sa_type=String(100), nullable=False)
    resource_id: str = Field(sa_type=String(255), nullable=False)
    ip_address: Optional[str] = Field(default=None, sa_type=String(64))
    metadata_: dict = Field(
        default_factory=dict,
        sa_column_kwargs={"name": "metadata"},
        sa_type=JSONB,
    )

    organization: Optional["Organization"] = Relationship(back_populates="audit_logs")


class ItemBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=255)


class ItemCreate(ItemBase):
    pass


class ItemUpdate(SQLModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=255)


class Item(ItemBase, UUIDMixin, TimestampMixin, table=True):
    __tablename__ = "items"

    owner_id: uuid.UUID = Field(
        foreign_key="users.id", nullable=False, ondelete="CASCADE"
    )
    owner: Optional[User] = Relationship(back_populates="items")


class ItemPublic(ItemBase):
    id: uuid.UUID
    owner_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class ItemsPublic(SQLModel):
    data: List[ItemPublic]
    count: int


class Message(SQLModel):
    message: str


class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(SQLModel):
    sub: Optional[str] = None


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=128)
