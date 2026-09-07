from enum import Enum

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.crud.crud import (
    count_current_games,
    filter_options_crud,
    get_current_games,
    get_current_moves,
    get_current_moves_positions,
    get_next_moves,
)
from src.models.database import engine
from src.routers.game_filters import (
    GameFilters,
    SpeedrunPlayerColourFilter,
    get_game_filters,
)
from src.schemas.fen_next_move import FenNextMoveResponse
from src.utils.fen_trimmer import fen_trimmer

router = APIRouter()


STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"


async def get_db():
    try:
        db = Session(engine)
        yield db
    finally:
        db.close()


@router.get("/")
async def root():
    return {"message": "Hello World"}


@router.get("/fen_match")
async def fen_match(fen: str, db: Session = Depends(get_db)):
    fen_trimmed = fen_trimmer(fen)
    print(fen_trimmed)
    matches = get_current_moves_positions(db, fen_trimmed)
    return {"matches": matches}


@router.get("/fen_next_move", response_model=FenNextMoveResponse)
async def fen_next_move(
    fen: str = STARTING_FEN,
    filters: GameFilters = Depends(get_game_filters),
    db: Session = Depends(get_db),
):
    fen_trimmed = fen_trimmer(fen)

    rows = get_current_moves(db, fen_trimmed, filters)

    p_plus_one = [((row.Positions.game_id, row.Positions.ply + 1)) for row in rows]

    next_positions = get_next_moves(db, p_plus_one)

    output_json = {}

    next_moves = {}
    san_dict = {}
    endings_dict = {}
    next_by_key = {(pos.game_id, pos.ply): pos for pos in next_positions}

    total_games = 0

    for row in rows:
        pos, series, game = row

        if game.speedrunner_colour == "black":
            opp_name = game.white
        elif game.speedrunner_colour == "white":
            opp_name = game.black
        else:
            raise ValueError("Speedrun Player Name not found")

        total_games += 1

        if next_by_key.get((pos.game_id, pos.ply + 1)):
            game_output = {}

            game_output["opponent"] = opp_name
            game_output["youtube_url"] = game.youtube_url
            game_output["chesscom_url"] = game.chesscom_url
            game_output["speedrun_player_colour"] = game.speedrunner_colour
            game_output["result"] = game.result
            game_output["white_elo"] = game.white_elo
            game_output["black_elo"] = game.black_elo
            game_output["game_date"] = game.game_date

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
                if game.speedrunner_colour == "black":
                    speedrun_player_won = True
                elif game.speedrunner_colour == "white":
                    speedrun_player_won = False

            elif game.result == "1-0":
                if game.speedrunner_colour == "black":
                    speedrun_player_won = False
                elif game.speedrunner_colour == "white":
                    speedrun_player_won = True

            elif game.result == "1/2-1/2":
                draw = True

            else:
                raise ValueError("Result not found")

            finished_game_output["opponent"] = opp_name
            finished_game_output["youtube_url"] = game.youtube_url
            finished_game_output["chesscom_url"] = game.chesscom_url
            finished_game_output["speedrun_player_colour"] = game.speedrunner_colour
            finished_game_output["result"] = game.result
            finished_game_output["white_elo"] = game.white_elo
            finished_game_output["black_elo"] = game.black_elo
            finished_game_output["game_date"] = game.game_date

            key = (game.termination, game.result)

            endings_dict[key] = endings_dict.get(key, {})
            endings_dict[key]["termination"] = game.termination
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
    output_json["total_games"] = total_games

    next_moves = list(san_dict.values())
    output_json["next_moves"] = next_moves
    output_json["game_endings"] = list(endings_dict.values())

    return output_json


@router.get("/fen_games")
async def fen_games(
    fen: str = STARTING_FEN,
    filters: GameFilters = Depends(get_game_filters),
    page: int = 1,
    limit: int = 25,
    speedrun_player_colour_filter=SpeedrunPlayerColourFilter.BOTH,
    db: Session = Depends(get_db),
):

    output_json = {}
    games_list = []

    fen_trimmed = fen_trimmer(fen)

    rows = get_current_games(db, fen_trimmed, filters, page=page, limit=limit)

    for row in rows:
        pos, series, game, creators = row

        if series.speedrun_username == game.black:
            if speedrun_player_colour_filter == SpeedrunPlayerColourFilter.WHITE:
                continue
            opp_name = game.white
            speedrun_player_colour = "black"
            speedrunner_elo = game.white_elo
            opponent_elo = game.black_elo
        elif series.speedrun_username == game.white:
            if speedrun_player_colour_filter == SpeedrunPlayerColourFilter.BLACK:
                continue
            opp_name = game.black
            speedrun_player_colour = "white"
            speedrunner_elo = game.black_elo
            opponent_elo = game.white_elo
        else:
            raise ValueError("Speedrun Player Name not found")

        game_output = {}
        game_output["id"] = game.id
        game_output["video_title"] = game.youtube_video_title
        game_output["series"] = series.name
        game_output["speedrunner"] = creators.name
        game_output["speedrunner_elo"] = speedrunner_elo
        game_output["opponent_elo"] = opponent_elo
        game_output["speedrunner_colour"] = speedrun_player_colour
        game_output["result"] = game.result
        game_output["chesscom_url"] = game.chesscom_url
        game_output["youtube_url"] = game.youtube_url
        game_output["game_date"] = game.game_date

        games_list.append(game_output)

    total_count = count_current_games(db, fen_trimmed, filters)

    output_json["games"] = games_list
    output_json["total_games"] = total_count
    output_json["has_more"] = (page * limit) < total_count

    return output_json


class FilterOptionsType(str, Enum):
    speed_runner = "speedrunner"
    series = "series"
    video_title = "video_title"


@router.get("/filter_options")
async def filter_options(
    col_type: FilterOptionsType,
    search: str,
    limit: int = 10,
    filters: GameFilters = Depends(get_game_filters),
    db: Session = Depends(get_db),
):

    output_list = filter_options_crud(db, col_type, search, limit, filters)

    return output_list
