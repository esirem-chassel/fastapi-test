
import re

from sqlmodel import SQLModel, Session, col, func, select

from models import Bingo, BingoSlot
from schemas import BingoInput
from database import engine


def createBingo(bingoIn: BingoInput)->Bingo|None:
    r = None
    if bingoIn.size > 0:
        bingo = Bingo(name=bingoIn.name, pwd=bingoIn.pwd, size=bingoIn.size)
        # generate slug from name
        slug:str = re.sub(r'[^a-zA-Z0-9-]', bingo.name, '-')
        slug = re.sub(r'-{2,}', slug, '-')
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
    with Session(engine) as session:
        stmt = select(Bingo)
        results = session.exec(stmt)
        return results
    return []

def initialize():
    SQLModel.metadata.create_all(engine)
