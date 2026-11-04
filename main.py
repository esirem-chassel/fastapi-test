from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from logic import createBingo, getAllBingos, initialize
from schemas import BingoInput, BingoOutput, BingoSlotOutput

class ClearText(BaseModel):
    value: str

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Initializing DB...")
    initialize()
    yield
    print("Closing...")

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def index():
    return {"bingos": getAllBingos()}

@app.get("/bingo/{slug}")
async def getBingo(slug):
    pass

@app.put("/bingo", response_model=BingoOutput)
async def create(bingo: BingoInput):
    r = createBingo(bingo)
    if r is None:
        raise HTTPException(status_code=400, detail="Invalid Bingo input")
    else:
        bingoOutput = BingoOutput(**r.model_dump())
        for s in r.slots:
            bingoOutput.slots.append(BingoSlotOutput(**s.model_dump()))
        return bingoOutput

@app.get("/search/{search}")
async def search(search):
    return {"message": f"searched {search}"}

@app.post("/register")
async def register(clear: ClearText):
    return clear