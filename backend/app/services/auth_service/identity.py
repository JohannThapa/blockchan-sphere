import uuid
from datetime import datetime, timezone
from typing import List, Optional, Tuple
from sqlmodel import Session, select, and_, func

from app.core.security import get_password_hash, verify_password
from app.models.users.user import (
    Organization, User, AuthIdentity, UserDevice, APIKey,
    Permission, RolePermission, AuditLog, UserRole,
)
from app.schemas.identity import (
    OrganizationCreate, OrganizationUpdate,
    UserCreate, UserUpdate,
    AuthIdentityCreate,
    UserDeviceCreate, UserDeviceUpdate,
    APIKeyCreate, APIKeyUpdate,
    PermissionCreate,
    RolePermissionCreate,
    AuditLogCreate,
)


def create_organization(session: Session, org_in: OrganizationCreate) -> Organization:
    db_org = Organization.model_validate(org_in)
    session.add(db_org)
    session.commit()
    session.refresh(db_org)
    return db_org


def get_organization(session: Session, org_id: uuid.UUID) -> Optional[Organization]:
    return session.get(Organization, org_id)


def get_organization_by_slug(session: Session, slug: str) -> Optional[Organization]:
    return session.exec(select(Organization).where(Organization.slug == slug)).first()


def update_organization(session: Session, db_org: Organization, org_in: OrganizationUpdate) -> Organization:
    update_data = org_in.model_dump(exclude_unset=True)
    db_org.sqlmodel_update(update_data)
    session.add(db_org)
    session.commit()
    session.refresh(db_org)
    return db_org


def delete_organization(session: Session, org_id: uuid.UUID) -> bool:
    org = get_organization(session, org_id)
    if not org:
        return False
    session.delete(org)
    session.commit()
    return True


def list_organizations(session: Session, skip: int = 0, limit: int = 100) -> List[Organization]:
    return session.exec(select(Organization).offset(skip).limit(limit)).all()


def create_user(session: Session, user_in: UserCreate) -> User:
    db_user = User.model_validate(
        user_in,
        update={"hashed_password": get_password_hash(user_in.password)}
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def get_user(session: Session, user_id: uuid.UUID) -> Optional[User]:
    return session.get(User, user_id)


def get_user_by_email(session: Session, email: str) -> Optional[User]:
    return session.exec(select(User).where(User.email == email)).first()


def update_user(session: Session, db_user: User, user_in: UserUpdate) -> User:
    update_data = user_in.model_dump(exclude_unset=True)
    if "password" in update_data:
        password = update_data.pop("password")
        update_data["hashed_password"] = get_password_hash(password)
    db_user.sqlmodel_update(update_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def delete_user(session: Session, user_id: uuid.UUID) -> bool:
    user = get_user(session, user_id)
    if not user:
        return False
    session.delete(user)
    session.commit()
    return True


def list_users(session: Session, org_id: Optional[uuid.UUID] = None, skip: int = 0, limit: int = 100) -> List[User]:
    stmt = select(User)
    if org_id:
        stmt = stmt.where(User.organization_id == org_id)
    return session.exec(stmt.offset(skip).limit(limit)).all()


def create_auth_identity(session: Session, identity_in: AuthIdentityCreate) -> AuthIdentity:
    db_ident = AuthIdentity.model_validate(identity_in)
    session.add(db_ident)
    session.commit()
    session.refresh(db_ident)
    return db_ident


def get_auth_identities_by_user(session: Session, user_id: uuid.UUID) -> List[AuthIdentity]:
    return session.exec(select(AuthIdentity).where(AuthIdentity.user_id == user_id)).all()


def delete_auth_identity(session: Session, identity_id: uuid.UUID) -> bool:
    ident = session.get(AuthIdentity, identity_id)
    if not ident:
        return False
    session.delete(ident)
    session.commit()
    return True


def create_user_device(session: Session, device_in: UserDeviceCreate) -> UserDevice:
    db_dev = UserDevice.model_validate(device_in)
    session.add(db_dev)
    session.commit()
    session.refresh(db_dev)
    return db_dev


def get_user_devices(session: Session, user_id: uuid.UUID) -> List[UserDevice]:
    return session.exec(select(UserDevice).where(UserDevice.user_id == user_id)).all()


def update_user_device(session: Session, db_dev: UserDevice, dev_in: UserDeviceUpdate) -> UserDevice:
    db_dev.sqlmodel_update(dev_in.model_dump(exclude_unset=True))
    session.add(db_dev)
    session.commit()
    session.refresh(db_dev)
    return db_dev


def delete_user_device(session: Session, device_id: uuid.UUID) -> bool:
    dev = session.get(UserDevice, device_id)
    if not dev:
        return False
    session.delete(dev)
    session.commit()
    return True


def generate_api_key_prefix() -> str:
    import secrets
    return f"cs_live_{secrets.token_hex(6)[:6]}"


def create_api_key(session: Session, key_in: APIKeyCreate) -> Tuple[APIKey, str]:
    import secrets
    raw_key = secrets.token_urlsafe(32)
    hashed = get_password_hash(raw_key)
    prefix = generate_api_key_prefix()
    db_key = APIKey(
        **key_in.model_dump(),
        key_prefix=prefix,
        hashed_key=hashed,
    )
    session.add(db_key)
    session.commit()
    session.refresh(db_key)
    return db_key, raw_key


def get_api_key(session: Session, key_id: uuid.UUID) -> Optional[APIKey]:
    return session.get(APIKey, key_id)


def get_api_key_by_prefix(session: Session, prefix: str) -> Optional[APIKey]:
    return session.exec(select(APIKey).where(APIKey.key_prefix == prefix)).first()


def update_api_key(session: Session, db_key: APIKey, key_in: APIKeyUpdate) -> APIKey:
    db_key.sqlmodel_update(key_in.model_dump(exclude_unset=True))
    session.add(db_key)
    session.commit()
    session.refresh(db_key)
    return db_key


def delete_api_key(session: Session, key_id: uuid.UUID) -> bool:
    key = get_api_key(session, key_id)
    if not key:
        return False
    session.delete(key)
    session.commit()
    return True


def list_api_keys(session: Session, org_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[APIKey]:
    return session.exec(select(APIKey).where(APIKey.organization_id == org_id).offset(skip).limit(limit)).all()


def authenticate_api_key(session: Session, raw_key: str) -> Optional[APIKey]:
    """
    Extract prefix from the raw key and verify the hash.
    Supports keys with multiple underscores (e.g., "cs_live_abc123").
    """
    # Find the first underscore that separates the prefix from the secret part.
    # The key format is: <prefix>_<secret> . The prefix may contain underscores,
    # but we defined it as "cs_live_xxxx" – actually we used f"cs_live_{token}"
    # So the separator is the first underscore after "cs_live".
    # To be safe, we'll take everything up to the first underscore as prefix?
    # Actually, we set prefix = "cs_live_xxxx" where xxxx is random, so the whole prefix is e.g. "cs_live_ab12"
    # and the raw key is "cs_live_ab12_rest".
    # So we need to split on the first underscore after "cs_live"? Better: we store the exact prefix, so we should
    # know the prefix length. Since we generate it ourselves, we can store prefix as the full string before the secret.
    # Our generate_api_key_prefix returns "cs_live_ab12". The raw key is "cs_live_ab12_rest" (two underscores).
    # So we can find the prefix by taking the first part up to the last underscore? Actually, we can just
    # try to find the APIKey by the prefix that matches the start of the raw key.
    # Simpler: we extract the prefix by splitting on '_' and joining the first two parts? But that's brittle.
    # Better: we know our prefix is always "cs_live_<6 chars>", so we can extract it.
    # Let's do a more generic: search for all APIKeys and verify the hash.
    # For performance, we could index by prefix but we need to know the exact prefix.
    # Since we generate prefix as "cs_live_xxxx", we can extract the first 13 characters? Not safe.
    # Let's just iterate through all active keys and verify? Not scalable.
    # The right approach: we store the full prefix, but when the client sends the key,
    # we don't know the prefix unless we parse the raw key.
    # We'll define the prefix as the part before the last underscore? Actually, we set
    # key_prefix = "cs_live_ab12" and raw_key = "cs_live_ab12_rest" (rest is the secret).
    # So to extract, we can take everything up to the last underscore? But there might be underscores in the secret.
    # The secret is base64url, which may include underscores. So we need to know the length of the prefix we generated.
    # We'll generate prefix as "cs_live_XXXXXX" where XXXXXX is 6 hex chars, length = 13.
    # So we can safely slice raw_key[:13] as prefix.
    prefix = raw_key[:13]  # "cs_live_XXXXXX"
    db_key = get_api_key_by_prefix(session, prefix)
    if not db_key or not db_key.is_active:
        return None
    if db_key.expires_at and db_key.expires_at < datetime.now(timezone.utc):
        return None
    # Verify the hash: the raw_key contains prefix + "_" + secret; but we stored hashed_key from the full raw_key.
    # In create_api_key we stored hashed_key = hash(raw_key). So we can verify by comparing raw_key with hash.
    verified, _ = verify_password(raw_key, db_key.hashed_key)
    if verified:
        db_key.last_used_at = datetime.now(timezone.utc)
        session.add(db_key)
        session.commit()
        session.refresh(db_key)
        return db_key
    return None


# ---------- Permission ----------
def create_permission(session: Session, perm_in: PermissionCreate) -> Permission:
    db_perm = Permission.model_validate(perm_in)
    session.add(db_perm)
    session.commit()
    session.refresh(db_perm)
    return db_perm


def get_permission_by_code(session: Session, code: str) -> Optional[Permission]:
    return session.exec(select(Permission).where(Permission.code == code)).first()


def list_permissions(session: Session, skip: int = 0, limit: int = 100) -> List[Permission]:
    return session.exec(select(Permission).offset(skip).limit(limit)).all()


def assign_permission_to_role(session: Session, rp_in: RolePermissionCreate) -> RolePermission:
    db_rp = RolePermission.model_validate(rp_in)
    session.add(db_rp)
    session.commit()
    session.refresh(db_rp)
    return db_rp


def remove_permission_from_role(session: Session, role: UserRole, permission_id: uuid.UUID) -> bool:
    stmt = select(RolePermission).where(
        and_(RolePermission.role == role, RolePermission.permission_id == permission_id)
    )
    rp = session.exec(stmt).first()
    if not rp:
        return False
    session.delete(rp)
    session.commit()
    return True


def get_permissions_for_role(session: Session, role: UserRole) -> List[Permission]:
    stmt = select(Permission).join(RolePermission).where(RolePermission.role == role)
    return session.exec(stmt).all()


def create_audit_log(session: Session, log_in: AuditLogCreate) -> AuditLog:
    db_log = AuditLog.model_validate(log_in)
    session.add(db_log)
    session.commit()
    session.refresh(db_log)
    return db_log


def list_audit_logs(
    session: Session,
    org_id: Optional[uuid.UUID] = None,
    actor_id: Optional[uuid.UUID] = None,
    resource_type: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
) -> List[AuditLog]:
    stmt = select(AuditLog)
    if org_id:
        stmt = stmt.where(AuditLog.organization_id == org_id)
    if actor_id:
        stmt = stmt.where(AuditLog.actor_user_id == actor_id)
    if resource_type:
        stmt = stmt.where(AuditLog.resource_type == resource_type)
    stmt = stmt.order_by(AuditLog.created_at.desc())
    return session.exec(stmt.offset(skip).limit(limit)).all()