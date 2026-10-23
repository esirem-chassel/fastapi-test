
from sqlmodel import Field, Relationship, SQLModel


class Bingo(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    slug: str
    pwd: str | None
    size: int = Field(default=5)
    slots: list["BingoSlot"] = Relationship(back_populates="bingo")

class BingoSlot(SQLModel, table=True):
    bingo_id: int = Field(foreign_key="bingo.id", primary_key=True)
    slot_id: int = Field(primary_key=True)
    bingo: "Bingo" = Field(back_populates="slots")
    value: str
    checked: bool = False
