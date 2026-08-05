import enum
import uuid
from datetime import datetime
from sqlalchemy import Boolean, Enum, ForeignKey, Numeric, String, DateTime
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_class import Base, TimestampMixin, UUIDMixin


class TriggerType(str, enum.Enum):
    schedule = "schedule"
    on_chain_event = "on_chain_event"
    threshold = "threshold"
    webhook = "webhook"


class ActionType(str, enum.Enum):
    transfer = "transfer"
    rebalance = "rebalance"
    notify = "notify"
    contract_call = "contract_call"


class ScheduledTransferStatus(str, enum.Enum):
    active = "active"
    paused = "paused"
    completed = "completed"
    cancelled = "cancelled"


class RunLogStatus(str, enum.Enum):
    success = "success"
    failed = "failed"
    skipped = "skipped"


class AutomationRule(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "automation_rules"

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    trigger_type: Mapped[TriggerType] = mapped_column(
        Enum(TriggerType, native_enum=False), nullable=False
    )
    trigger_config: Mapped[dict] = mapped_column(JSONB, nullable=False)
    action_type: Mapped[ActionType] = mapped_column(
        Enum(ActionType, native_enum=False), nullable=False
    )
    action_config: Mapped[dict] = mapped_column(JSONB, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class ScheduledTransfer(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "scheduled_transfers"

    wallet_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("wallets.id"), nullable=False
    )
    destination_address: Mapped[str] = mapped_column(String(128), nullable=False)
    token_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tokens.id"), nullable=False
    )
    amount: Mapped[int] = mapped_column(Numeric(78, 0), nullable=False)
    schedule_cron: Mapped[str | None] = mapped_column(String(100), nullable=True)
    next_run_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[ScheduledTransferStatus] = mapped_column(
        Enum(ScheduledTransferStatus, native_enum=False), default=ScheduledTransferStatus.active, nullable=False
    )


class AutomationRunLog(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "automation_run_logs"

    automation_rule_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("automation_rules.id"), nullable=False
    )
    status: Mapped[RunLogStatus] = mapped_column(
        Enum(RunLogStatus, native_enum=False), nullable=False
    )
    output: Mapped[dict] = mapped_column(JSONB, default={}, nullable=False)
    run_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)