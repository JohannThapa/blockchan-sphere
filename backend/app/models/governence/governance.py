import enum
import uuid
from datetime import datetime
from sqlalchemy import Enum, ForeignKey, Index, Integer, Numeric, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base, TimestampMixin, UUIDMixin


class ProposalStatus(str, enum.Enum):
    pending = "pending"
    active = "active"
    succeeded = "succeeded"
    defeated = "defeated"
    queued = "queued"
    executed = "executed"
    cancelled = "cancelled"


class VoteSupport(str, enum.Enum):
    for_ = "for"
    against = "against"
    abstain = "abstain"


class TimelockStatus(str, enum.Enum):
    queued = "queued"
    executed = "executed"
    cancelled = "cancelled"


class DAO(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "daos"

    contract_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("contracts.id"), nullable=False
    )
    organization_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    governance_token_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tokens.id"), nullable=False
    )
    voting_delay: Mapped[int | None] = mapped_column(Integer, nullable=True)
    voting_period: Mapped[int | None] = mapped_column(Integer, nullable=True)
    quorum: Mapped[int | None] = mapped_column(Numeric(78, 0), nullable=True)


class GovernanceProposal(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "governance_proposals"

    dao_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("daos.id"), nullable=False
    )
    proposer_address: Mapped[str | None] = mapped_column(String(128), nullable=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description_ref: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[ProposalStatus] = mapped_column(
        Enum(ProposalStatus, native_enum=False), default=ProposalStatus.pending, nullable=False
    )
    votes_for: Mapped[int] = mapped_column(Numeric(78, 0), default=0, nullable=False)
    votes_against: Mapped[int] = mapped_column(Numeric(78, 0), default=0, nullable=False)
    votes_abstain: Mapped[int] = mapped_column(Numeric(78, 0), default=0, nullable=False)
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ends_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class GovernanceVote(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "governance_votes"
    __table_args__ = (Index("uq_proposal_voter", "proposal_id", "voter_address", unique=True),)

    proposal_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("governance_proposals.id"), nullable=False
    )
    voter_address: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    support: Mapped[VoteSupport] = mapped_column(
        Enum(VoteSupport, native_enum=False), nullable=False
    )
    voting_power: Mapped[int] = mapped_column(Numeric(78, 0), nullable=False)
    tx_hash: Mapped[str | None] = mapped_column(String(128), nullable=True)


class GovernanceDelegation(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "governance_delegations"

    dao_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("daos.id"), nullable=False
    )
    delegator_address: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    delegate_address: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    voting_power: Mapped[int | None] = mapped_column(Numeric(78, 0), nullable=True)
    tx_hash: Mapped[str | None] = mapped_column(String(128), nullable=True)


class TreasuryTimelock(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "treasury_timelocks"

    dao_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("daos.id"), nullable=False
    )
    tx_hash_queued: Mapped[str | None] = mapped_column(String(128), nullable=True)
    target_address: Mapped[str | None] = mapped_column(String(128), nullable=True)
    calldata_ref: Mapped[str | None] = mapped_column(String(255), nullable=True)
    eta: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[TimelockStatus] = mapped_column(
        Enum(TimelockStatus, native_enum=False), default=TimelockStatus.queued, nullable=False
    )
    executed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)