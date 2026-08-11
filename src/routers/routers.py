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

STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"


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
    matches = (
        db.execute(select(Positions).where(Positions.fen_key == fen_trimmed))
        .scalars()
        .all()
    )
    return {"matches": matches}


@router.get("/fen_next_move")
async def fen_next_move(fen: str = STARTING_FEN, db: Session = Depends(get_db)):
    fen_trimmed = fen_trimmer(fen)
    positions = (
        db.execute(select(Positions).where(Positions.fen_key == fen_trimmed))
        .scalars()
        .all()
    )
    p_plus_one = []
    for pos in positions:
        p_plus_one.append((pos.game_id, pos.ply + 1))

    output_json = {}

    next_positions = (
        db.execute(
            select(Positions).where(
                tuple_(Positions.game_id, Positions.ply).in_(p_plus_one)
            )
        )
        .scalars()
        .all()
    )

    next_moves = {}
    san_dict = {}
    endings_dict = {}
    next_by_key = {(pos.game_id, pos.ply): pos for pos in next_positions}

    stmt = (
        select(Positions, Series, Games)
        .join(Games, Positions.game_id == Games.id)
        .join(Series, Games.series_id == Series.id)
        .where(fen_trimmed == Positions.fen_key)
    )

    rows = db.execute(stmt).all()

    for row in rows:
        pos, series, game = row

        if series.speedrun_username == game.black:
            opp_name = game.white
            speedrun_player_colour = "black"
        elif series.speedrun_username == game.white:
            opp_name = game.black
            speedrun_player_colour = "white"
        else:
            raise ValueError("Speedrun Player Name not found")

        if next_by_key.get((pos.game_id, pos.ply + 1)):
            game_output = {}

            game_output["opponent"] = opp_name
            game_output["youtube_url"] = game.youtube_url
            game_output["chesscom_url"] = game.chesscom_url
            game_output["speedrun_player_colour"] = speedrun_player_colour
            game_output["result"] = game.result

            next_move = next_by_key.get((pos.game_id, pos.ply + 1))

            san_dict[next_move.san] = san_dict.get(next_move.san, {})
            san_dict[next_move.san]["san"] = next_move.san
            san_dict[next_move.san]["count"] = (
                san_dict[next_move.san].get("count", 0) + 1
            )
            games_list = san_dict[next_move.san].get("games", [])
            games_list.append(game_output)
            san_dict[next_move.san]["games"] = games_list

        else:
            finished_game_output = {}
            speedrun_player_won = None
            draw = False

            if game.result == "0-1":
                if speedrun_player_colour == "black":
                    speedrun_player_won = True
                elif speedrun_player_colour == "white":
                    speedrun_player_won = False

            elif game.result == "1-0":
                if speedrun_player_colour == "black":
                    speedrun_player_won = False
                elif speedrun_player_colour == "white":
                    speedrun_player_won = True

            elif game.result == "1/2-1/2":
                draw = True

            else:
                raise ValueError("Result not found")

            finished_game_output["opponent"] = opp_name
            finished_game_output["youtube_url"] = game.youtube_url
            finished_game_output["chesscom_url"] = game.chesscom_url
            finished_game_output["speedrun_player_colour"] = speedrun_player_colour
            finished_game_output["result"] = game.result

            key = (game.termination, game.result)

            endings_dict[key] = endings_dict.get(key, {})
            endings_dict[key]["result"] = game.termination
            if draw:
                endings_dict[key]["speedrunner_result"] = "D"
            else:
                endings_dict[key]["speedrunner_result"] = (
                    "W" if speedrun_player_won else "L"
                )
            endings_dict[key]["count"] = endings_dict[key].get("count", 0) + 1
            finished_games_list = endings_dict[key].get("games", [])
            finished_games_list.append(finished_game_output)
            endings_dict[key]["games"] = finished_games_list

    output_json["position_fen"] = fen
    output_json["total_games"] = len(positions)

    next_moves = list(san_dict.values())
    output_json["next_moves"] = next_moves
    output_json["game_endings"] = list(endings_dict.values())

    return output_json
