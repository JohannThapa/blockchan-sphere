# app/utils/audit.py
from fastapi import Request
from app.services.auth_service.identity import create_audit_log
from app.schemas.identity import AuditLogCreate

async def log_action(
    session,
    actor_user_id,
    organization_id,
    action,
    resource_type,
    resource_id,
    ip_address=None,
    metadata=None,
):
    log_in = AuditLogCreate(
        organization_id=organization_id,
        actor_user_id=actor_user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        ip_address=ip_address,
        metadata=metadata or {},
    )
    create_audit_log(session, log_in)