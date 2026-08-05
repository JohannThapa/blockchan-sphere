import enum
import uuid
from datetime import datetime, timezone
from sqlalchemy import UUID
from sqlalchemy import Enum, ForeignKey, Integer, Numeric, String, DateTime
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_class import Base

class UUIDMixin:
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    
class MetricType(str, enum.Enum):
    revenue = "revenue"
    wallet_growth = "wallet_growth"
    tvl = "tvl"
    token_distribution = "token_distribution"
    gas_analysis = "gas_analysis"
    user_activity = "user_activity"


class MetricPeriod(str, enum.Enum):
    hourly = "hourly"
    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"


class AnalyticsSnapshot(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "analytics_snapshots"

    organization_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=True
    )
    metric_type: Mapped[MetricType] = mapped_column(
        Enum(MetricType, native_enum=False), nullable=False
    )
    scope: Mapped[str | None] = mapped_column(String(255), nullable=True)
    value: Mapped[float] = mapped_column(Numeric(38, 10), nullable=False)
    period: Mapped[MetricPeriod] = mapped_column(
        Enum(MetricPeriod, native_enum=False), nullable=False
    )
    snapshot_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class DashboardWidget(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "dashboard_widgets"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    widget_type: Mapped[str] = mapped_column(String(100), nullable=False)
    config: Mapped[dict] = mapped_column(JSONB, default={}, nullable=False)
    position: Mapped[int] = mapped_column(Integer, default=0, nullable=False)