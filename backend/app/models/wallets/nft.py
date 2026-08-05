import enum
import uuid
from datetime import datetime
from sqlalchemy import Boolean, Enum, ForeignKey, Index, Integer, Numeric, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin, UUIDMixin


class NFTStandard(str, enum.Enum):
    erc721 = "erc721"
    erc1155 = "erc1155"


class ListingStatus(str, enum.Enum):
    active = "active"
    sold = "sold"
    cancelled = "cancelled"
    expired = "expired"


class AuctionStatus(str, enum.Enum):
    open = "open"
    settled = "settled"
    cancelled = "cancelled"


class NFTCollection(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "nft_collections"

    contract_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("contracts.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    symbol: Mapped[str | None] = mapped_column(String(32), nullable=True)
    standard: Mapped[NFTStandard] = mapped_column(
        Enum(NFTStandard, native_enum=False), nullable=False
    )
    royalty_bps: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    creator_address: Mapped[str | None] = mapped_column(String(128), nullable=True)


class NFTItem(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "nft_items"
    __table_args__ = (
        Index("uq_collection_token_id", "collection_id", "token_id_onchain", unique=True),
    )

    collection_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("nft_collections.id"), nullable=False
    )
    token_id_onchain: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    owner_address: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True)
    metadata_uri: Mapped[str | None] = mapped_column(String(500), nullable=True)
    metadata_ref: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_lazy_minted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class NFTListing(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "nft_listings"

    nft_item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("nft_items.id"), nullable=False
    )
    seller_address: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    price: Mapped[int] = mapped_column(Numeric(78, 0), nullable=False)
    currency_token_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tokens.id"), nullable=False
    )
    status: Mapped[ListingStatus] = mapped_column(
        Enum(ListingStatus, native_enum=False), default=ListingStatus.active, nullable=False
    )
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class NFTAuction(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "nft_auctions"

    nft_item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("nft_items.id"), nullable=False
    )
    starting_price: Mapped[int] = mapped_column(Numeric(78, 0), nullable=False)
    reserve_price: Mapped[int | None] = mapped_column(Numeric(78, 0), nullable=True)
    current_bid: Mapped[int | None] = mapped_column(Numeric(78, 0), nullable=True)
    highest_bidder_address: Mapped[str | None] = mapped_column(String(128), nullable=True)
    status: Mapped[AuctionStatus] = mapped_column(
        Enum(AuctionStatus, native_enum=False), default=AuctionStatus.open, nullable=False
    )
    ends_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class NFTRoyaltyPayment(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "nft_royalty_payments"

    nft_item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("nft_items.id"), nullable=False
    )
    sale_tx_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    recipient_address: Mapped[str] = mapped_column(String(128), nullable=False)
    amount: Mapped[int] = mapped_column(Numeric(78, 0), nullable=False)