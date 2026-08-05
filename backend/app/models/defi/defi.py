import enum
import uuid
from datetime import datetime
from sqlalchemy import Enum, Float, ForeignKey, Numeric, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base, TimestampMixin, UUIDMixin


class LendingSide(str, enum.Enum):
    supply = "supply"
    borrow = "borrow"


class StakingPosition(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "staking_positions"

    wallet_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("wallets.id"), nullable=False
    )
    protocol: Mapped[str] = mapped_column(String(100), nullable=False)
    token_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tokens.id"), nullable=False
    )
    staked_amount: Mapped[int] = mapped_column(Numeric(78, 0), nullable=False)
    rewards_earned: Mapped[int] = mapped_column(Numeric(78, 0), default=0, nullable=False)
    apr: Mapped[float | None] = mapped_column(Float, nullable=True)
    staked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    unstaked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class LiquidityPool(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "liquidity_pools"

    chain_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("chains.id"), nullable=False
    )
    protocol: Mapped[str] = mapped_column(String(100), nullable=False)
    pool_address: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    token_a_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tokens.id"), nullable=False
    )
    token_b_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tokens.id"), nullable=False
    )
    tvl: Mapped[float | None] = mapped_column(Numeric(78, 2), nullable=True)
    apr: Mapped[float | None] = mapped_column(Float, nullable=True)


class LiquidityPosition(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "liquidity_positions"

    wallet_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("wallets.id"), nullable=False
    )
    pool_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("liquidity_pools.id"), nullable=False
    )
    lp_token_amount: Mapped[int] = mapped_column(Numeric(78, 0), nullable=False)
    share_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    entered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class LendingPosition(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "lending_positions"

    wallet_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("wallets.id"), nullable=False
    )
    protocol: Mapped[str] = mapped_column(String(100), nullable=False)
    side: Mapped[LendingSide] = mapped_column(
        Enum(LendingSide, native_enum=False), nullable=False
    )
    asset_token_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tokens.id"), nullable=False
    )
    amount: Mapped[int] = mapped_column(Numeric(78, 0), nullable=False)
    health_factor: Mapped[float | None] = mapped_column(Float, nullable=True)