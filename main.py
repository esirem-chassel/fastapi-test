from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from logic import createBingo
from schemas import BingoInput, BingoOutput, BingoSlotOutput

class ClearText(BaseModel):
    value: str

app = FastAPI()

@app.get("/")
async def index():
    return {"message": "Hello World"}

@app.get("/bingo/{slug}")
async def getBingo(slug):
    pass

@app.put("/bingo")
async def create(bingo: BingoInput):
    r = createBingo(bingo)
    if r is None:
        raise HTTPException(status_code=400, detail="Invalid Bingo input")
    else:
        bingoOutput = BingoOutput(name=r.name, size=r.size, slug=r.slug)
        for s in r.slots:
            bingoOutput.slots.append(BingoSlotOutput(bingo_id=None)) # @TODO
        return {"bingo": bingoOutput)}

@app.get("/search/{search}")
async def search(search):
    return {"message": f"searched {search}"}

@app.post("/register")
async def register(clear: ClearText):
    return clear