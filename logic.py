
import re

from sqlmodel import Session, col, select

from models import Bingo
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
            stmt = select(Bingo).where(col(Bingo.slug).regexp_match(f"^{slug}"))
            res = session.exec(stmt)
            if res:
                slug = f"{slug}-{1+len(res)}"
            bingo.slug = slug
            session.add(bingo)
            session.commit()
            r = bingo
    return r
