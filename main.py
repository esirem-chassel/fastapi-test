from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Response, status
from pydantic import BaseModel

from logic import convertBingoToOutput, createBingo, findBingoBySlug, getAllBingos, initialize
from schemas import BingoInput, BingoOutput, BingoSlotOutput, BingosList

class ClearText(BaseModel):
    value: str

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Initializing DB...")
    initialize()
    yield
    print("Closing...")

app = FastAPI(lifespan=lifespan)

@app.get("/", response_model=BingosList)
async def index():
    bingos = getAllBingos()
    res = []
    for b in bingos:
        res.append(convertBingoToOutput(b, False))
    return {"bingos": res}

@app.get("/bingo/{slug}", response_model=BingoOutput|None)
async def getBingo(slug: str, response: Response):
    b = findBingoBySlug(slug)
    if b:
        return convertBingoToOutput(b, True)
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
        return None

@app.put("/bingo", response_model=BingoOutput)
async def create(bingo: BingoInput):
    r = createBingo(bingo)
    if r is None:
        raise HTTPException(status_code=400, detail="Invalid Bingo input")
    else:
        return convertBingoToOutput(r, True)

@app.get("/search/{search}")
async def search(search):
    return {"message": f"searched {search}"}

@app.post("/register")
async def register(clear: ClearText):
    return clear