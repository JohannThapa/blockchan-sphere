from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import (
    SessionDep, CurrentUser, CurrentSuperuser, PermissionDep,
    check_organization_access, require_permission,
)
from sqlmodel import Session, select
from app.models.users.user import AuthIdentity, Permission, RolePermission, User, Organization, APIKey, UserDevice, UserRole
from app.schemas.identity import (
    OrganizationCreate, OrganizationUpdate, OrganizationRead,
    UserCreate, UserUpdate, UserRead,
    AuthIdentityCreate, AuthIdentityRead,
    UserDeviceCreate, UserDeviceUpdate, UserDeviceRead,
    APIKeyCreate, APIKeyUpdate, APIKeyRead, APIKeyWithPlain,
    PermissionCreate, PermissionRead,
    RolePermissionCreate, RolePermissionRead,
    AuditLogRead, AuditLogCreate,
)
from app.services.auth_service.identity import (
    create_organization, get_organization, get_organization_by_slug,
    update_organization, delete_organization, list_organizations,
    create_user, get_user, get_user_by_email, update_user, delete_user, list_users,
    create_auth_identity, get_auth_identities_by_user, delete_auth_identity,
    create_user_device, get_user_devices, update_user_device, delete_user_device,
    create_api_key, get_api_key, update_api_key, delete_api_key, list_api_keys,
    create_permission, get_permission_by_code, list_permissions,
    assign_permission_to_role, remove_permission_from_role, get_permissions_for_role,
    create_audit_log, list_audit_logs,
)

router = APIRouter(prefix="/identity", tags=["Identity & Access"])


# ---------- Organizations ----------
@router.post("/organizations", response_model=OrganizationRead)
def create_org(
    session: SessionDep,
    org_in: OrganizationCreate,
    current_user: CurrentSuperuser,  # only superusers can create orgs
):
    if get_organization_by_slug(session, org_in.slug):
        raise HTTPException(400, "Organization with this slug already exists")
    return create_organization(session, org_in)


@router.get("/organizations", response_model=List[OrganizationRead])
def list_orgs(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
):
    # Only allow superusers to list all orgs; regular users can only see their own org
    if current_user.is_superuser:
        return list_organizations(session, skip, limit)
    # For non-superusers, return only their own organization
    if current_user.organization_id:
        org = get_organization(session, current_user.organization_id)
        return [org] if org else []
    return []


@router.get("/organizations/{org_id}", response_model=OrganizationRead)
def get_org(
    session: SessionDep,
    org_id: UUID,
    current_user: CurrentUser,
):
    org = get_organization(session, org_id)
    if not org:
        raise HTTPException(404, "Organization not found")
    check_organization_access(current_user, org_id)
    return org


@router.put("/organizations/{org_id}", response_model=OrganizationRead)
def update_org(
    session: SessionDep,
    org_id: UUID,
    org_in: OrganizationUpdate,
    current_user: CurrentSuperuser,  # restrict to superusers
):
    org = get_organization(session, org_id)
    if not org:
        raise HTTPException(404, "Organization not found")
    return update_organization(session, org, org_in)


@router.delete("/organizations/{org_id}", status_code=204)
def delete_org(
    session: SessionDep,
    org_id: UUID,
    current_user: CurrentSuperuser,
):
    if not delete_organization(session, org_id):
        raise HTTPException(404, "Organization not found")


# ---------- Users ----------
@router.post("/users", response_model=UserRead)
def create_new_user(
    session: SessionDep,
    user_in: UserCreate,
    current_user: CurrentUser,
):
    # Only allow creation if user has permission and within same org (or superuser)
    require_permission(session, current_user, "user.create")
    if not current_user.is_superuser:
        # Non-superusers can only create users in their own org
        if user_in.organization_id is None:
            user_in.organization_id = current_user.organization_id
        elif user_in.organization_id != current_user.organization_id:
            raise HTTPException(403, "Cannot create user in another organization")
    if get_user_by_email(session, user_in.email):
        raise HTTPException(400, "User with this email already exists")
    return create_user(session, user_in)


@router.get("/users", response_model=List[UserRead])
def list_all_users(
    session: SessionDep,
    current_user: CurrentUser,
    org_id: Optional[UUID] = None,
    skip: int = 0,
    limit: int = 100,
):
    require_permission(session, current_user, "user.list")
    # If user is not superuser, force filter by their organization
    if not current_user.is_superuser:
        org_id = current_user.organization_id
    # If org_id is still None, return empty (should not happen)
    return list_users(session, org_id, skip, limit)


@router.get("/users/me", response_model=UserRead)
def read_current_user(current_user: CurrentUser):
    return current_user


@router.get("/users/{user_id}", response_model=UserRead)
def get_user_by_id(
    session: SessionDep,
    user_id: UUID,
    current_user: CurrentUser,
):
    require_permission(session, current_user, "user.read")
    user = get_user(session, user_id)
    if not user:
        raise HTTPException(404, "User not found")
    check_organization_access(current_user, user.organization_id)
    return user


@router.put("/users/{user_id}", response_model=UserRead)
def update_existing_user(
    session: SessionDep,
    user_id: UUID,
    user_in: UserUpdate,
    current_user: CurrentUser,
):
    require_permission(session, current_user, "user.update")
    user = get_user(session, user_id)
    if not user:
        raise HTTPException(404, "User not found")
    check_organization_access(current_user, user.organization_id)
    # Prevent non-superusers from changing is_superuser or role to owner?
    if not current_user.is_superuser:
        if user_in.is_superuser is not None:
            raise HTTPException(403, "Cannot change superuser status")
        if user_in.role == UserRole.owner:
            raise HTTPException(403, "Cannot assign owner role")
    return update_user(session, user, user_in)


@router.delete("/users/{user_id}", status_code=204)
def delete_existing_user(
    session: SessionDep,
    user_id: UUID,
    current_user: CurrentUser,
):
    require_permission(session, current_user, "user.delete")
    user = get_user(session, user_id)
    if not user:
        raise HTTPException(404, "User not found")
    check_organization_access(current_user, user.organization_id)
    if user_id == current_user.id:
        raise HTTPException(400, "Cannot delete yourself")
    if not delete_user(session, user_id):
        raise HTTPException(404, "User not found")


# ---------- Auth Identities ----------
@router.post("/auth-identities", response_model=AuthIdentityRead)
def add_auth_identity(
    session: SessionDep,
    ident_in: AuthIdentityCreate,
    current_user: CurrentUser,
):
    require_permission(session, current_user, "auth_identity.create")
    # Ensure the user exists and belongs to same org
    user = get_user(session, ident_in.user_id)
    if not user:
        raise HTTPException(404, "User not found")
    check_organization_access(current_user, user.organization_id)
    return create_auth_identity(session, ident_in)


@router.get("/auth-identities/user/{user_id}", response_model=List[AuthIdentityRead])
def list_user_auth_identities(
    session: SessionDep,
    user_id: UUID,
    current_user: CurrentUser,
):
    require_permission(session, current_user, "auth_identity.list")
    user = get_user(session, user_id)
    if not user:
        raise HTTPException(404, "User not found")
    check_organization_access(current_user, user.organization_id)
    return get_auth_identities_by_user(session, user_id)


@router.delete("/auth-identities/{identity_id}", status_code=204)
def remove_auth_identity(
    session: SessionDep,
    identity_id: UUID,
    current_user: CurrentUser,
):
    require_permission(session, current_user, "auth_identity.delete")
    ident = session.get(AuthIdentity, identity_id)
    if not ident:
        raise HTTPException(404, "Auth identity not found")
    user = get_user(session, ident.user_id)
    if not user:
        raise HTTPException(404, "User not found")
    check_organization_access(current_user, user.organization_id)
    if not delete_auth_identity(session, identity_id):
        raise HTTPException(404, "Auth identity not found")


# ---------- User Devices ----------
@router.post("/devices", response_model=UserDeviceRead)
def add_device(
    session: SessionDep,
    device_in: UserDeviceCreate,
    current_user: CurrentUser,
):
    require_permission(session, current_user, "device.create")
    user = get_user(session, device_in.user_id)
    if not user:
        raise HTTPException(404, "User not found")
    check_organization_access(current_user, user.organization_id)
    return create_user_device(session, device_in)


@router.get("/devices/user/{user_id}", response_model=List[UserDeviceRead])
def list_devices(
    session: SessionDep,
    user_id: UUID,
    current_user: CurrentUser,
):
    require_permission(session, current_user, "device.list")
    user = get_user(session, user_id)
    if not user:
        raise HTTPException(404, "User not found")
    check_organization_access(current_user, user.organization_id)
    return get_user_devices(session, user_id)


@router.put("/devices/{device_id}", response_model=UserDeviceRead)
def update_device(
    session: SessionDep,
    device_id: UUID,
    device_in: UserDeviceUpdate,
    current_user: CurrentUser,
):
    require_permission(session, current_user, "device.update")
    dev = session.get(UserDevice, device_id)
    if not dev:
        raise HTTPException(404, "Device not found")
    user = get_user(session, dev.user_id)
    if not user:
        raise HTTPException(404, "User not found")
    check_organization_access(current_user, user.organization_id)
    return update_user_device(session, dev, device_in)


@router.delete("/devices/{device_id}", status_code=204)
def remove_device(
    session: SessionDep,
    device_id: UUID,
    current_user: CurrentUser,
):
    require_permission(session, current_user, "device.delete")
    dev = session.get(UserDevice, device_id)
    if not dev:
        raise HTTPException(404, "Device not found")
    user = get_user(session, dev.user_id)
    if not user:
        raise HTTPException(404, "User not found")
    check_organization_access(current_user, user.organization_id)
    if not delete_user_device(session, device_id):
        raise HTTPException(404, "Device not found")


# ---------- API Keys ----------
@router.post("/api-keys", response_model=APIKeyWithPlain)
def create_new_api_key(
    session: SessionDep,
    key_in: APIKeyCreate,
    current_user: CurrentUser,
):
    require_permission(session, current_user, "api_key.create")
    # Verify org access
    org = get_organization(session, key_in.organization_id)
    if not org:
        raise HTTPException(404, "Organization not found")
    check_organization_access(current_user, key_in.organization_id)
    db_key, plain = create_api_key(session, key_in)
    return APIKeyWithPlain(**db_key.model_dump(), plain_key=plain)


@router.get("/api-keys", response_model=List[APIKeyRead])
def list_api_keys_endpoint(
    session: SessionDep,
    current_user: CurrentUser,
    org_id: Optional[UUID] = None,
    skip: int = 0,
    limit: int = 100,
):
    require_permission(session, current_user, "api_key.list")
    # If user not superuser, force org_id to their org
    if not current_user.is_superuser:
        org_id = current_user.organization_id
        if org_id is None:
            raise HTTPException(403, "User has no organization")
    else:
        if org_id is None:
            raise HTTPException(400, "org_id required for superusers")
    return list_api_keys(session, org_id, skip, limit)


@router.get("/api-keys/{key_id}", response_model=APIKeyRead)
def get_api_key_by_id(
    session: SessionDep,
    key_id: UUID,
    current_user: CurrentUser,
):
    require_permission(session, current_user, "api_key.read")
    key = get_api_key(session, key_id)
    if not key:
        raise HTTPException(404, "API key not found")
    check_organization_access(current_user, key.organization_id)
    return key


@router.put("/api-keys/{key_id}", response_model=APIKeyRead)
def update_api_key_endpoint(
    session: SessionDep,
    key_id: UUID,
    key_in: APIKeyUpdate,
    current_user: CurrentUser,
):
    require_permission(session, current_user, "api_key.update")
    key = get_api_key(session, key_id)
    if not key:
        raise HTTPException(404, "API key not found")
    check_organization_access(current_user, key.organization_id)
    return update_api_key(session, key, key_in)


@router.delete("/api-keys/{key_id}", status_code=204)
def delete_api_key_endpoint(
    session: SessionDep,
    key_id: UUID,
    current_user: CurrentUser,
):
    require_permission(session, current_user, "api_key.delete")
    key = get_api_key(session, key_id)
    if not key:
        raise HTTPException(404, "API key not found")
    check_organization_access(current_user, key.organization_id)
    if not delete_api_key(session, key_id):
        raise HTTPException(404, "API key not found")


# ---------- Permissions & RolePermissions ----------
@router.post("/permissions", response_model=PermissionRead)
def create_new_permission(
    session: SessionDep,
    perm_in: PermissionCreate,
    current_user: CurrentSuperuser,  # only superusers can create permissions
):
    if get_permission_by_code(session, perm_in.code):
        raise HTTPException(400, "Permission code already exists")
    return create_permission(session, perm_in)


@router.get("/permissions", response_model=List[PermissionRead])
def list_all_permissions(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
):
    require_permission(session, current_user, "permission.list")
    return list_permissions(session, skip, limit)


@router.post("/role-permissions", response_model=RolePermissionRead)
def assign_permission(
    session: SessionDep,
    rp_in: RolePermissionCreate,
    current_user: CurrentSuperuser,  # restrict to superusers
):
    # Check that permission exists
    perm = session.get(Permission, rp_in.permission_id)
    if not perm:
        raise HTTPException(404, "Permission not found")
    existing = session.exec(
        select(RolePermission).where(
            RolePermission.role == rp_in.role,
            RolePermission.permission_id == rp_in.permission_id
        )
    ).first()
    if existing:
        raise HTTPException(400, "Assignment already exists")
    return assign_permission_to_role(session, rp_in)


@router.delete("/role-permissions", status_code=204)
def remove_permission(
    session: SessionDep,
    role: UserRole,
    permission_id: UUID,
    current_user: CurrentSuperuser,
):
    if not remove_permission_from_role(session, role, permission_id):
        raise HTTPException(404, "Assignment not found")


# ---------- Audit Logs ----------
@router.post("/audit-logs", response_model=AuditLogRead)
def create_audit_log_endpoint(
    session: SessionDep,
    log_in: AuditLogCreate,
    current_user: CurrentUser,
):
    require_permission(session, current_user, "audit_log.create")
    # If org_id provided, check access
    if log_in.organization_id:
        check_organization_access(current_user, log_in.organization_id)
    return create_audit_log(session, log_in)


@router.get("/audit-logs", response_model=List[AuditLogRead])
def list_audit_logs_endpoint(
    session: SessionDep,
    current_user: CurrentUser,
    org_id: Optional[UUID] = None,
    actor_id: Optional[UUID] = None,
    resource_type: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
):
    require_permission(session, current_user, "audit_log.list")
    if not current_user.is_superuser:
        org_id = current_user.organization_id
    if org_id:
        check_organization_access(current_user, org_id)
    return list_audit_logs(session, org_id, actor_id, resource_type, skip, limit)