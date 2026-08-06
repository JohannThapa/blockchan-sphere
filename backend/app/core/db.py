from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

import app.models
from app.core.config import settings
from app.models.users.user import (
    Organization,
    Permission,
    PlanTier,
    RolePermission,
    User,
    UserCreate,
    UserRole,
)
from app.schemas.identity import PermissionCreate, RolePermissionCreate
from app.services.auth_service.identity import (
    assign_permission_to_role,
    create_permission,
    create_user,
    get_user_by_email,
)

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))


def init_db(session: Session) -> None:
    default_org_slug = "default-org"
    org = session.scalars(
        select(Organization).where(Organization.slug == default_org_slug)
    ).first()

    if not org:
        org = Organization(
            name="Default Organization",
            slug=default_org_slug,
            plan_tier=PlanTier.enterprise,
            is_active=True,
        )
        session.add(org)
        session.commit()
        session.refresh(org)

    user = session.scalars(
        select(User).where(User.email == settings.FIRST_SUPERUSER)
    ).first()

    if not user:
        user_in = UserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
            role=UserRole.owner,
            organization_id=org.id,
        )
        user = create_user(session=session, user_in=user_in)

    default_perms = [
        ("org.create", "Create organization"),
        ("org.list", "List organizations"),
        ("org.read", "Read organization"),
        ("org.update", "Update organization"),
        ("org.delete", "Delete organization"),
        ("user.create", "Create user"),
        ("user.list", "List users"),
        ("user.read", "Read user"),
        ("user.update", "Update user"),
        ("user.delete", "Delete user"),
        ("auth_identity.create", "Add auth identity"),
        ("auth_identity.list", "List auth identities"),
        ("auth_identity.delete", "Delete auth identity"),
        ("device.create", "Add device"),
        ("device.list", "List devices"),
        ("device.update", "Update device"),
        ("device.delete", "Delete device"),
        ("api_key.create", "Create API key"),
        ("api_key.list", "List API keys"),
        ("api_key.read", "Read API key"),
        ("api_key.update", "Update API key"),
        ("api_key.delete", "Delete API key"),
        ("permission.create", "Create permission"),
        ("permission.list", "List permissions"),
        ("role_permission.assign", "Assign permission to role"),
        ("role_permission.remove", "Remove permission from role"),
        ("audit_log.create", "Create audit log"),
        ("audit_log.list", "List audit logs"),
        ("address.label", "Label a blockchain address"),
        ("chain.sync", "Trigger on-demand chain sync"),
    ]

    for code, desc in default_perms:
        perm = session.scalars(
            select(Permission).where(Permission.code == code)
        ).first()
        if not perm:
            perm = create_permission(
                session, PermissionCreate(code=code, description=desc)
            )

    all_perms = list(session.scalars(select(Permission)).all())

    for perm in all_perms:
        existing = session.scalars(
            select(RolePermission).where(
                RolePermission.role == UserRole.owner,
                RolePermission.permission_id == perm.id,
            )
        ).first()
        if not existing:
            assign_permission_to_role(
                session,
                RolePermissionCreate(role=UserRole.owner, permission_id=perm.id),
            )

    admin_exclude = {
        "org.delete",
        "user.delete",
        "permission.create",
        "role_permission.assign",
        "role_permission.remove",
    }
    for perm in all_perms:
        if perm.code in admin_exclude:
            continue
        existing = session.scalars(
            select(RolePermission).where(
                RolePermission.role == UserRole.admin,
                RolePermission.permission_id == perm.id,
            )
        ).first()
        if not existing:
            assign_permission_to_role(
                session,
                RolePermissionCreate(role=UserRole.admin, permission_id=perm.id),
            )

    session.commit()
