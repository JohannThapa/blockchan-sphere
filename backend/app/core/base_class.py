from dataclasses import Field
from typing import Optional
import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import DeclarativeBase
from sqlmodel import Field, Relationship, SQLModel
from sqlalchemy import Column, DateTime, String, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID

def get_datetime_utc() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


# class UUIDMixin(SQLModel):
#     id: uuid.UUID = Field(
#         default_factory=uuid.uuid4,
#         primary_key=True,
#         nullable=False,
#         sa_column_kwargs={"server_default": "gen_random_uuid()"}
#     )
class UUIDMixin(SQLModel):
    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        nullable=False,
    )
class TimestampMixin(SQLModel):
    created_at: datetime = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),
        nullable=False
    )
    updated_at: datetime = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),
        nullable=False
    )