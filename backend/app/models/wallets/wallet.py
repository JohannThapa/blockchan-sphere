import enum
import uuid
from datetime import datetime
from sqlalchemy import Boolean, Enum, ForeignKey, Integer, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin, UUIDMixin


class WalletType(str, enum.Enum):
    hd = "hd"
    hardware = "hardware"
    multisig = "multisig"
    smart = "smart"
    cold = "cold"
    hot = "hot"


class Wallet(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "wallets"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    organization_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=True
    )
    wallet_type: Mapped[WalletType] = mapped_column(
        Enum(WalletType, native_enum=False), nullable=False
    )
    label: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    addresses: Mapped[list["WalletAddress"]] = relationship(back_populates="wallet")
    signers: Mapped[list["WalletSigner"]] = relationship(back_populates="wallet")
    connections: Mapped[list["WalletConnection"]] = relationship(back_populates="wallet")


class WalletAddress(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "wallet_addresses"

    wallet_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("wallets.id"), nullable=False
    )
    chain_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("chains.id"), nullable=False
    )
    address: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    derivation_path: Mapped[str | None] = mapped_column(String(100), nullable=True)
    is_watch_only: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    wallet: Mapped["Wallet"] = relationship(back_populates="addresses")


class WalletSigner(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "wallet_signers"

    wallet_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("wallets.id"), nullable=False
    )
    signer_address: Mapped[str] = mapped_column(String(128), nullable=False)
    weight: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    added_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    wallet: Mapped["Wallet"] = relationship(back_populates="signers")


class WalletConnection(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "wallet_connections"

    wallet_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("wallets.id"), nullable=False
    )
    dapp_origin: Mapped[str] = mapped_column(String(255), nullable=False)
    session_topic: Mapped[str | None] = mapped_column(String(255), index=True, nullable=True)
    connected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    wallet: Mapped["Wallet"] = relationship(back_populates="connections")