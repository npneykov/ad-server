"""Tracking models for impressions and clicks."""

from datetime import UTC, datetime

from sqlmodel import Field, SQLModel


class Impression(SQLModel, table=True):
    """Ad impression tracking."""

    id: int | None = Field(default=None, primary_key=True)
    ad_id: int = Field(foreign_key='ad.id')
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


class Click(SQLModel, table=True):
    """Ad click tracking."""

    id: int | None = Field(default=None, primary_key=True)
    ad_id: int = Field(foreign_key='ad.id')
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
