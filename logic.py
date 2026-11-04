
import re

from sqlmodel import SQLModel, Session, col, func, select

from models import Bingo, BingoSlot
from schemas import BingoInput, BingoOutput, BingoSlotOutput
from database import engine


def createBingo(bingoIn: BingoInput)->Bingo|None:
    r = None
    if bingoIn.size > 0:
        bingo = Bingo(name=bingoIn.name, pwd=bingoIn.pwd, size=bingoIn.size)
        # generate slug from name
        slug:str = re.sub(r'[^a-z0-9-]', '-', bingoIn.name.lower())
        slug = re.sub(r'-{2,}', '-', slug)
        # now, search for slug in db, if exists, count and +1
        with Session(engine) as session:
            nb = session.exec(select(func.count(col(Bingo.id))).where(col(Bingo.slug).regexp_match(f"^{slug}"))).one()
            if nb > 0:
                slug = f"{slug}-{1+nb}"
            bingo.slug = slug
            session.add(bingo)
            for z in range(bingo.size**2):
                bs = BingoSlot(bingo=bingo, slot_id=1+z, value="")
                session.add(bs)
            session.commit()
            session.refresh(bingo)
            for s in bingo.slots:
                session.refresh(s)
            r = bingo
    return r

def getAllBingos()->list[Bingo]:
    res = []
    with Session(engine) as session:
        stmt = select(Bingo)
        results = session.exec(stmt).all()
        res = results
    return res

def findBingoBySlug(slug: str)->Bingo|None:
    res = None
    with Session(engine) as session:
        stmt = select(Bingo).where(Bingo.slug == slug)
        res = session.exec(stmt).one_or_none()
        if res is not None:
            res.slots # access once to load
    return res

def updateBingo(bingo: Bingo, input: BingoInput)->Bingo|None:
    res = None
    with Session(engine) as session:
        bingo.name = input.name
        if input.pwd is not None and input.pwd != bingo.pwd:
            bingo.pwd = input.pwd
        session.add(bingo)
        session.commit()
        session.refresh(bingo)
        bingo.slots # force refresh slots
        res = bingo
    return res

def findBingoSlot(bingo: Bingo, slotId: int)->BingoSlot|None:
    res = None
    with Session(engine) as session:
        stmt = select(BingoSlot).where(BingoSlot.bingo_id == bingo.id).where(BingoSlot.slot_id == slotId)
        res = session.exec(stmt).one_or_none()
    return res

def updateBingoSlot(slot: BingoSlot, newValue: str)->BingoSlot|None:
    res = None
    with Session(engine) as session:
        slot.value = newValue
        session.add(slot)
        session.commit()
        session.refresh(slot)
        res = slot
    return res

def checkBingoSlot(slot: BingoSlot, checked: bool)->BingoSlot|None:
    res = None
    with Session(engine) as session:
        slot.checked = checked
        session.add(slot)
        session.commit()
        session.refresh(slot)
        res = slot
    return res

def convertBingoToOutput(bingo: Bingo, withSlots: bool = False)->BingoOutput:
    o = BingoOutput(**bingo.model_dump())
    o.private = (bingo.pwd is not None)
    if withSlots:
        for s in bingo.slots:
            o.slots.append(convertSlotToOutput(s))
    return o

def convertSlotToOutput(slot: BingoSlot)->BingoSlotOutput:
    return BingoSlotOutput(**slot.model_dump())

def initialize():
    SQLModel.metadata.create_all(engine)
