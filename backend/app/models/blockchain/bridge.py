import enum
import uuid
from datetime import datetime
from sqlalchemy import Enum, ForeignKey, Numeric, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base, TimestampMixin, UUIDMixin


class BridgeStatus(str, enum.Enum):
    initiated = "initiated"
    relaying = "relaying"
    completed = "completed"
    failed = "failed"


class Bridge(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "bridges"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    source_chain_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("chains.id"), nullable=False
    )
    destination_chain_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("chains.id"), nullable=False
    )
    protocol: Mapped[str | None] = mapped_column(String(100), nullable=True)
    contract_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("contracts.id"), nullable=True
    )


class BridgeTransaction(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "bridge_transactions"

    bridge_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bridges.id"), nullable=False
    )
    source_tx_hash: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    destination_tx_hash: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True)
    from_address: Mapped[str] = mapped_column(String(128), nullable=False)
    to_address: Mapped[str] = mapped_column(String(128), nullable=False)
    token_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tokens.id"), nullable=False
    )
    amount: Mapped[int] = mapped_column(Numeric(78, 0), nullable=False)
    status: Mapped[BridgeStatus] = mapped_column(
        Enum(BridgeStatus, native_enum=False), default=BridgeStatus.initiated, nullable=False
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)