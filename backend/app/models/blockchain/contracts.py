import enum
import uuid
from sqlalchemy import BigInteger, Boolean, Enum, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin, UUIDMixin


class ContractStandard(str, enum.Enum):
    erc20 = "erc20"
    erc721 = "erc721"
    erc1155 = "erc1155"
    proxy = "proxy"
    custom = "custom"
    non_evm = "non_evm"


class VerificationStatus(str, enum.Enum):
    unverified = "unverified"
    pending = "pending"
    verified = "verified"
    failed = "failed"


class Contract(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "contracts"

    chain_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("chains.id"), nullable=False
    )
    address: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    deployer_address: Mapped[str | None] = mapped_column(String(128), nullable=True)
    deployment_tx_hash: Mapped[str | None] = mapped_column(String(128), nullable=True)
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    standard: Mapped[ContractStandard] = mapped_column(
        Enum(ContractStandard, native_enum=False), default=ContractStandard.custom, nullable=False
    )
    is_proxy: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    implementation_address: Mapped[str | None] = mapped_column(String(128), nullable=True)
    verification_status: Mapped[VerificationStatus] = mapped_column(
        Enum(VerificationStatus, native_enum=False), default=VerificationStatus.unverified, nullable=False
    )
    source_code_ref: Mapped[str | None] = mapped_column(String(255), nullable=True)
    risk_score: Mapped[float | None] = mapped_column(Float, nullable=True)

    events: Mapped[list["ContractEvent"]] = relationship(back_populates="contract")
    upgrades: Mapped[list["ContractUpgrade"]] = relationship(back_populates="contract")


class ContractEvent(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "contract_events"

    contract_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("contracts.id"), nullable=False
    )
    tx_hash: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    log_index: Mapped[int] = mapped_column(Integer, nullable=False)
    block_number: Mapped[int] = mapped_column(BigInteger, nullable=False)
    event_name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    decoded_args: Mapped[dict] = mapped_column(JSONB, nullable=False)

    contract: Mapped["Contract"] = relationship(back_populates="events")


class ContractUpgrade(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "contract_upgrades"

    contract_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("contracts.id"), nullable=False
    )
    old_implementation: Mapped[str | None] = mapped_column(String(128), nullable=True)
    new_implementation: Mapped[str] = mapped_column(String(128), nullable=False)
    tx_hash: Mapped[str] = mapped_column(String(128), nullable=False)

    contract: Mapped["Contract"] = relationship(back_populates="upgrades")