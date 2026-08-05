import enum
import uuid
from datetime import datetime
from sqlalchemy import Enum, ForeignKey, String, DateTime
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base, TimestampMixin, UUIDMixin


class SecretType(str, enum.Enum):
    api_key = "api_key"
    private_key = "private_key"
    hsm_ref = "hsm_ref"
    oauth_secret = "oauth_secret"


class EventType(str, enum.Enum):
    login_anomaly = "login_anomaly"
    key_leak_suspected = "key_leak_suspected"
    siem_alert = "siem_alert"
    brute_force = "brute_force"
    permission_escalation = "permission_escalation"


class SecuritySeverity(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class SecretMetadata(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "secrets_metadata"

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    secret_type: Mapped[SecretType] = mapped_column(
        Enum(SecretType, native_enum=False), nullable=False
    )
    storage_ref: Mapped[str] = mapped_column(String(255), nullable=False)
    last_rotated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class KeyRotation(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "key_rotations"

    secret_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("secrets_metadata.id"), nullable=False
    )
    rotated_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    reason: Mapped[str | None] = mapped_column(String(255), nullable=True)


class SecurityEvent(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "security_events"

    organization_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=True
    )
    event_type: Mapped[EventType] = mapped_column(
        Enum(EventType, native_enum=False), nullable=False
    )
    severity: Mapped[SecuritySeverity] = mapped_column(
        Enum(SecuritySeverity, native_enum=False), nullable=False
    )
    source: Mapped[str | None] = mapped_column(String(100), nullable=True)
    details: Mapped[dict] = mapped_column(JSONB, default={}, nullable=False)
    detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)