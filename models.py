from datetime import datetime

from sqlmodel import Boolean, Column, Field, Relationship, SQLModel


class Zone(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    width: int
    height: int
    ads: list['Ad'] = Relationship(back_populates='zone')


class Ad(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    zone_id: int = Field(foreign_key='zone.id')
    html: str
    url: str
    weight: int = 1
    zone: Zone | None = Relationship(back_populates='ads')
    is_active: bool = Field(default=True, sa_column=Column(Boolean, default=True))


class Impression(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    ad_id: int = Field(foreign_key='ad.id')
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class Click(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    ad_id: int = Field(foreign_key='ad.id')
    timestamp: datetime = Field(default_factory=datetime.utcnow)
