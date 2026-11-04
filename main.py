from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Response, status
from pydantic import BaseModel

from logic import checkBingoSlot, convertBingoToOutput, convertSlotToOutput, createBingo, findBingoBySlug, findBingoSlot, getAllBingos, initialize, updateBingo, updateBingoSlot
from schemas import BingoInput, BingoOutput, BingoSlotOutput, BingosList

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

@app.post("/bingo/{slug}", response_model=BingoOutput)
async def update(slug: str, bingo: BingoInput, response: Response, pwd: str|None = None):
    b = findBingoBySlug(slug)
    if b:
        if b.pwd == pwd:
            return convertBingoToOutput(updateBingo(b, bingo))
        else:
            response.status_code = status.HTTP_403_FORBIDDEN
            return None
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
        return None

@app.post("/bingo/{slug}/{slot}", response_model=BingoSlotOutput)
async def update(slug: str, slot: int, value: str, response: Response, pwd: str|None = None):
    b = findBingoBySlug(slug)
    if b:
        if b.pwd == pwd:
            s = findBingoSlot(b, slot)
            if s is not None:
                return convertSlotToOutput(updateBingoSlot(s, value))
            else:
                response.status_code = status.HTTP_404_NOT_FOUND
                return None
        else:
            response.status_code = status.HTTP_403_FORBIDDEN
            return None
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
        return None

@app.post("/bingo/{slug}/{slot}/check", response_model=BingoSlotOutput)
async def check(slug: str, slot: int, checked: bool, response: Response, pwd: str|None = None):
    b = findBingoBySlug(slug)
    if b:
        if b.pwd == pwd:
            s = findBingoSlot(b, slot)
            if s is not None:
                return convertSlotToOutput(checkBingoSlot(s, checked))
            else:
                response.status_code = status.HTTP_404_NOT_FOUND
                return None
        else:
            response.status_code = status.HTTP_403_FORBIDDEN
            return None
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
        return None

@app.get("/search/{search}")
async def search(search):
    return {"message": f"searched {search}"}
