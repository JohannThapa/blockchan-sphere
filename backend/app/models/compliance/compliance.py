import enum
import uuid
from datetime import date, datetime
from sqlalchemy import Date, Enum, Float, ForeignKey, String, DateTime
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base, TimestampMixin, UUIDMixin


class KYCStatus(str, enum.Enum):
    not_started = "not_started"
    pending = "pending"
    verified = "verified"
    rejected = "rejected"


class ScreeningType(str, enum.Enum):
    ofac = "ofac"
    sanctions = "sanctions"
    pep = "pep"


class ScreeningResult(str, enum.Enum):
    clear = "clear"
    match = "match"
    review_required = "review_required"


class RiskCategory(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class AlertSeverity(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class AlertStatus(str, enum.Enum):
    open = "open"
    reviewing = "reviewing"
    closed = "closed"
    escalated = "escalated"


class KYCRecord(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "kyc_records"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    organization_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=True
    )
    provider: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[KYCStatus] = mapped_column(
        Enum(KYCStatus, native_enum=False), default=KYCStatus.not_started, nullable=False
    )
    document_ref: Mapped[str | None] = mapped_column(String(255), nullable=True)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class AMLScreening(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "aml_screenings"

    address: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    screening_type: Mapped[ScreeningType] = mapped_column(
        Enum(ScreeningType, native_enum=False), nullable=False
    )
    result: Mapped[ScreeningResult] = mapped_column(
        Enum(ScreeningResult, native_enum=False), nullable=False
    )
    matched_entity: Mapped[str | None] = mapped_column(String(255), nullable=True)
    screened_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class WalletRiskScore(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "wallet_risk_scores"

    address: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    chain_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("chains.id"), nullable=False
    )
    risk_score: Mapped[float] = mapped_column(Float, nullable=False)
    risk_category: Mapped[RiskCategory] = mapped_column(
        Enum(RiskCategory, native_enum=False), nullable=False
    )
    factors: Mapped[dict] = mapped_column(JSONB, default={}, nullable=False)
    computed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class BlacklistEntry(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "blacklist_entries"

    address: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    chain_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("chains.id"), nullable=False
    )
    reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
    source: Mapped[str | None] = mapped_column(String(100), nullable=True)
    added_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )


class TransactionMonitoringAlert(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "transaction_monitoring_alerts"

    tx_hash: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    rule_triggered: Mapped[str] = mapped_column(String(255), nullable=False)
    severity: Mapped[AlertSeverity] = mapped_column(
        Enum(AlertSeverity, native_enum=False), nullable=False
    )
    status: Mapped[AlertStatus] = mapped_column(
        Enum(AlertStatus, native_enum=False), default=AlertStatus.open, nullable=False
    )
    assigned_to_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )


class ComplianceReport(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "compliance_reports"

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )
    report_type: Mapped[str] = mapped_column(String(100), nullable=False)
    period_start: Mapped[date] = mapped_column(Date, nullable=False)
    period_end: Mapped[date] = mapped_column(Date, nullable=False)
    file_ref: Mapped[str | None] = mapped_column(String(255), nullable=True)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)