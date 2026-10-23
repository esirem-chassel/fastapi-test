from pydantic import BaseModel

class BingoInput(BaseModel):
    name: str
    pwd: str | None
    size: int = 5

class BingoSlotInput(BaseModel):
    bingo_id: int
    slot_id: int
    value: str

class BingoOutput(BaseModel):
    name: str
    size: int
    slug: str
    slots: list["BingoSlotOutput"]

class BingoSlotOutput(BaseModel):
    bingo_id: int
    slot_id: int
    value: str
    checked: bool