
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
        res.slots # access once to load
    return res

def convertBingoToOutput(bingo: Bingo, withSlots: bool = False)->BingoOutput:
    o = BingoOutput(**bingo.model_dump())
    if withSlots:
        for s in bingo.slots:
            o.slots.append(BingoSlotOutput(**s.model_dump()))
    return o

def initialize():
    SQLModel.metadata.create_all(engine)
