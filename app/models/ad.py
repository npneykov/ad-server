"""Ad model."""

from sqlmodel import Boolean, Column, Field, Relationship, SQLModel

from app.models.zone import Zone


class Ad(SQLModel, table=True):
    """Advertisement entity."""

    id: int | None = Field(default=None, primary_key=True)
    zone_id: int = Field(foreign_key='zone.id')
    html: str
    url: str
    weight: int = 1
    zone: Zone | None = Relationship(back_populates='ads')
    is_active: bool = Field(default=True, sa_column=Column(Boolean, default=True))
