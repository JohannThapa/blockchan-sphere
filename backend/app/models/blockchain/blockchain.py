import enum
import uuid
from datetime import datetime
from sqlalchemy import BigInteger, Boolean, Enum, ForeignKey, Index, Integer, Numeric, String, DateTime  # pyright: ignore[reportMissingImports]
from sqlalchemy.dialects.postgresql import UUID  # pyright: ignore[reportMissingImports]
from sqlalchemy.orm import Mapped, mapped_column, relationship  # pyright: ignore[reportMissingImports]
from app.models.base import Base, TimestampMixin, UUIDMixin


class ChainType(str, enum.Enum):
    evm = "evm"
    bitcoin = "bitcoin"
    solana = "solana"
    cosmos = "cosmos"
    move = "move"
    ton = "ton"


class TxStatus(str, enum.Enum):
    pending = "pending"
    success = "success"
    failed = "failed"
    reverted = "reverted"


class TxType(str, enum.Enum):
    transfer = "transfer"
    contract_call = "contract_call"
    contract_creation = "contract_creation"
    bridge = "bridge"
    swap = "swap"


class AddressType(str, enum.Enum):
    eoa = "eoa"
    contract = "contract"
    unknown = "unknown"


class Chain(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "chains"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    chain_type: Mapped[ChainType] = mapped_column(
        Enum(ChainType, native_enum=False), nullable=False
    )
    chain_id_numeric: Mapped[int | None] = mapped_column(Integer, nullable=True)
    rpc_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    explorer_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    native_symbol: Mapped[str | None] = mapped_column(String(20), nullable=True)
    is_testnet: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class Block(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "blocks"
    __table_args__ = (Index("uq_chain_block_number", "chain_id", "block_number", unique=True),)

    chain_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("chains.id"), nullable=False
    )
    block_number: Mapped[int] = mapped_column(BigInteger, index=True, nullable=False)
    block_hash: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    parent_hash: Mapped[str | None] = mapped_column(String(128), nullable=True)
    tx_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    block_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class Transaction(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "transactions"
    __table_args__ = (Index("uq_chain_tx_hash", "chain_id", "tx_hash", unique=True),)

    chain_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("chains.id"), nullable=False
    )
    tx_hash: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    block_number: Mapped[int | None] = mapped_column(BigInteger, index=True, nullable=True)
    from_address: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    to_address: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True)
    value: Mapped[int] = mapped_column(Numeric(78, 0), default=0, nullable=False)
    gas_used: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    gas_price: Mapped[int | None] = mapped_column(Numeric(78, 0), nullable=True)
    status: Mapped[TxStatus] = mapped_column(
        Enum(TxStatus, native_enum=False), nullable=False
    )
    tx_type: Mapped[TxType | None] = mapped_column(
        Enum(TxType, native_enum=False), nullable=True
    )
    raw_payload_ref: Mapped[str | None] = mapped_column(String(255), nullable=True)


class Address(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "addresses"
    __table_args__ = (Index("uq_chain_address", "chain_id", "address", unique=True),)

    chain_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("chains.id"), nullable=False
    )
    address: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    address_type: Mapped[AddressType] = mapped_column(
        Enum(AddressType, native_enum=False), default=AddressType.unknown, nullable=False
    )
    label: Mapped[str | None] = mapped_column(String(255), nullable=True)
    first_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)