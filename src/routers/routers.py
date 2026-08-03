from fastapi import APIRouter, Depends
from sqlalchemy import select, tuple_
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


@router.get("/fen_next_move")
async def fen_match(fen: str, db: Session = Depends(get_db)):
    fen_trimmed = fen_trimmer(fen)
    print(fen_trimmed)
    positions = db.execute(select(Positions).where(Positions.fen_key == fen_trimmed)).scalars().all()
    p_plus_one = []
    for pos in positions:
        p_plus_one.append((pos.game_id, pos.ply + 1))

    output_json = {}
    # next_moves = []
    game_endings = []
    
    next_positions = db.execute(select(Positions).where(tuple_(Positions.game_id, Positions.ply).in_(p_plus_one))).scalars().all()

    next_pos_id = [(next_pos.game_id) for next_pos in next_positions]

    games = db.execute(select(Games).where((Games.id).in_(next_pos_id))).scalars().all()

    next_moves = {}
    san_dict = {}
    next_by_key = {(pos.game_id, pos.ply): pos for pos in next_positions}

    for pos in positions: 
        game = [g for g in games if g.id == pos.game_id]
        if not game: 
            pass
        if next_by_key.get((pos.game_id, pos.ply + 1)):
            game_output = {}
            game_output["opponent"] = "Hikaru"
            game_output["youtube_url"] = game[0].youtube_url
            game_output["chesscom_url"] = game[0].chesscom_url
            game_output["speedrun_player_colour"] = "white" #to be fixed

            next_move = next_by_key.get((pos.game_id, pos.ply + 1))

            san_dict[next_move.san] = san_dict.get(next_move.san, {})
            san_dict[next_move.san]["san"] = next_move.san
            san_dict[next_move.san]["count"] = san_dict[next_move.san].get("count", 0 ) + 1
            games_list = san_dict[next_move.san].get("games", [])
            games_list.append(game_output)
            san_dict[next_move.san]["games"] = games_list
            
        else:

            game_endings.append(game.termination)

    output_json["position_fen"] = fen
    output_json["total_games"] = len(next_positions)
    
    next_moves = list(san_dict.values())
    output_json["next_moves"] = next_moves
    output_json["game_endings"] = game_endings

    return output_json

