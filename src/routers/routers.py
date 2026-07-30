from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models.creators import Creators
from src.models.database import engine
from src.models.games import Games
from src.models.positions import Positions
from src.models.series import Series
from src.utils.fen_trimmer import fen_trimmer

router = APIRouter()

@router.get("/")
async def root():
    return {"message": "Hello World"}

async def get_db():
    try:
        db = Session(engine)
        yield db 
    finally:
        db.close()

@router.get("/fen_match")
async def fen_match(fen: str, db: Session = Depends(get_db)):
    fen_trimmed = fen_trimmer(fen)
    print(fen_trimmed)
    matches = db.execute(select(Positions).where(Positions.fen_key == fen_trimmed)).scalars().all()
    return {"matches": matches}

