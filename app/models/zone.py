"""Zone model."""

from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.ad import Ad


class Zone(SQLModel, table=True):
    """Advertising zone/placement area."""

    id: int | None = Field(default=None, primary_key=True)
    name: str
    width: int
    height: int
    ads: list['Ad'] = Relationship(back_populates='zone')
