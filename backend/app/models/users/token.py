import enum
import uuid
from datetime import datetime
from sqlalchemy import BigInteger, Enum, ForeignKey, Index, Integer, Numeric, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin, UUIDMixin


class TokenStandard(str, enum.Enum):
    erc20 = "erc20"
    erc721 = "erc721"
    erc1155 = "erc1155"
    native = "native"
    spl = "spl"
    non_evm = "non_evm"


class AirdropStatus(str, enum.Enum):
    draft = "draft"
    active = "active"
    closed = "closed"


class Token(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "tokens"

    chain_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("chains.id"), nullable=False
    )
    contract_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("contracts.id"), nullable=True
    )
    symbol: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    decimals: Mapped[int] = mapped_column(Integer, default=18, nullable=False)
    standard: Mapped[TokenStandard] = mapped_column(
        Enum(TokenStandard, native_enum=False), nullable=False
    )
    total_supply: Mapped[int | None] = mapped_column(Numeric(78, 0), nullable=True)


class TokenBalance(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "token_balances"
    __table_args__ = (
        Index("uq_addr_token_block", "address_id", "token_id", "block_number", unique=True),
    )

    address_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("addresses.id"), nullable=False
    )
    token_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tokens.id"), nullable=False
    )
    balance: Mapped[int] = mapped_column(Numeric(78, 0), default=0, nullable=False)
    block_number: Mapped[int] = mapped_column(BigInteger, nullable=False)


class TokenTransfer(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "token_transfers"

    token_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tokens.id"), nullable=False
    )
    tx_hash: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    log_index: Mapped[int] = mapped_column(Integer, nullable=False)
    from_address: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    to_address: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    amount: Mapped[int] = mapped_column(Numeric(78, 0), nullable=False)


class TokenVestingSchedule(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "token_vesting_schedules"

    token_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tokens.id"), nullable=False
    )
    beneficiary_address: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    total_amount: Mapped[int] = mapped_column(Numeric(78, 0), nullable=False)
    released_amount: Mapped[int] = mapped_column(Numeric(78, 0), default=0, nullable=False)
    cliff_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    start_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class Airdrop(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "airdrops"

    token_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tokens.id"), nullable=False
    )
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    snapshot_block: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    merkle_root: Mapped[str | None] = mapped_column(String(128), nullable=True)
    status: Mapped[AirdropStatus] = mapped_column(
        Enum(AirdropStatus, native_enum=False), default=AirdropStatus.draft, nullable=False
    )


class AirdropClaim(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "airdrop_claims"

    airdrop_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("airdrops.id"), nullable=False
    )
    address: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    amount: Mapped[int] = mapped_column(Numeric(78, 0), nullable=False)
    tx_hash: Mapped[str | None] = mapped_column(String(128), nullable=True)
    claimed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)