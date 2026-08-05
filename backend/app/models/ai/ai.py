import enum
import uuid
from sqlalchemy import Boolean, Enum, Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base_class import Base, TimestampMixin, UUIDMixin


class AIModelType(str, enum.Enum):
    fraud = "fraud"
    risk = "risk"
    nlp = "nlp"
    forecasting = "forecasting"
    anomaly = "anomaly"


class SubjectType(str, enum.Enum):
    wallet = "wallet"
    contract = "contract"
    transaction = "transaction"
    portfolio = "portfolio"
    treasury = "treasury"


class FraudType(str, enum.Enum):
    phishing = "phishing"
    wash_trading = "wash_trading"
    honeypot = "honeypot"
    insider_trading = "insider_trading"
    mev = "mev"
    flash_loan_exploit = "flash_loan_exploit"


class MessageRole(str, enum.Enum):
    user = "user"
    assistant = "assistant"
    system = "system"
    tool = "tool"


class AIModel(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "ai_models"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    model_type: Mapped[AIModelType] = mapped_column(
        Enum(AIModelType, native_enum=False), nullable=False
    )
    version: Mapped[str] = mapped_column(String(50), nullable=False)
    provider: Mapped[str | None] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class AIInsight(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "ai_insights"

    ai_model_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ai_models.id"), nullable=False
    )
    subject_type: Mapped[SubjectType] = mapped_column(
        Enum(SubjectType, native_enum=False), nullable=False
    )
    subject_id: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    insight_text_ref: Mapped[str | None] = mapped_column(String(255), nullable=True)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)


class FraudDetectionResult(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "fraud_detection_results"

    ai_model_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ai_models.id"), nullable=False
    )
    subject_address: Mapped[str | None] = mapped_column(String(128), nullable=True)
    tx_hash: Mapped[str | None] = mapped_column(String(128), nullable=True)
    fraud_type: Mapped[FraudType] = mapped_column(
        Enum(FraudType, native_enum=False), nullable=False
    )
    score: Mapped[float] = mapped_column(Float, nullable=False)
    evidence: Mapped[dict] = mapped_column(JSONB, default={}, nullable=False)


class WalletScore(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "wallet_scores"

    address: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    chain_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("chains.id"), nullable=False
    )
    health_score: Mapped[float] = mapped_column(Float, nullable=False)
    activity_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    computed_by_model_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ai_models.id"), nullable=False
    )


class RugPullPrediction(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "rug_pull_predictions"

    contract_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("contracts.id"), nullable=False
    )
    ai_model_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ai_models.id"), nullable=False
    )
    risk_score: Mapped[float] = mapped_column(Float, nullable=False)
    indicators: Mapped[dict] = mapped_column(JSONB, default={}, nullable=False)


class AIAssistantConversation(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "ai_assistant_conversations"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class AIAssistantMessage(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "ai_assistant_messages"

    conversation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ai_assistant_conversations.id"), nullable=False
    )
    role: Mapped[MessageRole] = mapped_column(
        Enum(MessageRole, native_enum=False), nullable=False
    )
    content_ref: Mapped[str] = mapped_column(String(255), nullable=False)