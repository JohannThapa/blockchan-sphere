import enum
import uuid
from datetime import datetime
from sqlalchemy import Enum, Float, ForeignKey, Numeric, String, DateTime
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base, TimestampMixin, UUIDMixin


class RebalanceTriggeredBy(str, enum.Enum):
    manual = "manual"
    ai_automation = "ai_automation"


class RebalanceStatus(str, enum.Enum):
    pending = "pending"
    executing = "executing"
    completed = "completed"
    failed = "failed"


class TreasuryAccount(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "treasury_accounts"

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )
    chain_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("chains.id"), nullable=False
    )
    wallet_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("wallets.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)


class TreasuryAllocation(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "treasury_allocations"

    treasury_account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("treasury_accounts.id"), nullable=False
    )
    asset_token_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tokens.id"), nullable=False
    )
    target_pct: Mapped[float] = mapped_column(Float, nullable=False)
    current_pct: Mapped[float | None] = mapped_column(Float, nullable=True)


class TreasuryRebalanceEvent(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "treasury_rebalance_events"

    treasury_account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("treasury_accounts.id"), nullable=False
    )
    triggered_by: Mapped[RebalanceTriggeredBy] = mapped_column(
        Enum(RebalanceTriggeredBy, native_enum=False), nullable=False
    )
    status: Mapped[RebalanceStatus] = mapped_column(
        Enum(RebalanceStatus, native_enum=False), default=RebalanceStatus.pending, nullable=False
    )
    tx_hashes: Mapped[list] = mapped_column(JSONB, default=[], nullable=False)
    executed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class TreasuryRiskAssessment(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "treasury_risk_assessments"

    treasury_account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("treasury_accounts.id"), nullable=False
    )
    ai_model_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ai_models.id"), nullable=False
    )
    risk_score: Mapped[float] = mapped_column(Float, nullable=False)
    var_95: Mapped[float | None] = mapped_column(Numeric(78, 2), nullable=True)