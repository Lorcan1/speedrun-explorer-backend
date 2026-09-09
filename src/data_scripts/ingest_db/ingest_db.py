import json
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models.creators import Creators
from src.models.database import Base, engine
from src.models.games import Games
from src.models.positions import Positions
from src.models.series import Series

SERIES_NAME_0 = "Speedrun"
SERIES_NAME_1 = "The Sensei Speedrun"
SERIES_NAME_2 = "DYI Develop Your Instincts Speedrun"
SPEEDRUN_USERNAME0 = "SenseiDanya"
SPEEDRUN_USERNAME1 = "HebeccaRaris"

series_name = SERIES_NAME_2
speedrun_username = SPEEDRUN_USERNAME1


location = {
    "Speedrun": {
        "updated_games": "data/series/Speedrun/updated_games.json",
        "positions": "data/series/Speedrun/positions.json",
    },
    "The Sensei Speedrun": {
        "updated_games": "data/series/The Sensei Speedrun/updated_games.json",
        "positions": "data/series/The Sensei Speedrun/positions.json",
    },
    "DYI Develop Your Instincts Speedrun": {
        "updated_games": "data/series/DYI/updated_games.json",
        "positions": "data/series/DYI/positions.json"

    }

}

chesscom_id_to_game_id = {}


Base.metadata.create_all(engine)

with Session(engine) as session:
    danya = session.scalar(select(Creators).where(Creators.name == "Daniel Naroditsky"))
    if not danya:
        danya = Creators(name="Daniel Naroditsky")
        session.add(danya)
        session.commit()
    series = session.scalar(select(Series).where(Series.name == series_name))
    if not series:
        series = Series(
        creator_id=danya.id, name=series_name, speedrun_username=speedrun_username
    )
        session.add(series)
        session.commit()

    # with open("updated_games.json") as f:
    #     games = json.load(f)

    with open(location[series_name]["updated_games"]) as f:
        games = json.load(f)

    sensei = session.scalar(select(Series).where(Series.name == series_name))

    for game in games:
        if game["result"] == "1/2-1/2":
            speedrunner_result = "draw"
        elif ((game["result"] == "1-0" and game["speedrunner_colour"] == "white") or 
              (game["result"] == "0-1" and game["speedrunner_colour"] == "black" )):
            speedrunner_result = "win"
        else:
            speedrunner_result = "loss"


        new_game = Games(
            series_id=sensei.id,
            white=game["white"],
            black=game["black"],
            result=game["result"],
            # speedrunner_result = speedrunner_result,
            white_elo=game["white_elo"],
            black_elo=game["black_elo"],
            speedrunner_colour=game["speedrunner_colour"],
            speedrunner_elo = game["white_elo"] if game["speedrunner_colour"] == "white" else game["black_elo"],
            game_date=datetime.strptime(game["date"], "%Y.%m.%d").date(),
            eco=game["eco"],
            opening=game["opening"],
            time_control=game["time_control"],
            termination=game["termination"],
            youtube_url=game["youtube_url"],
            youtube_video_title=game["youtube_video_title"],
            chesscom_url=game["chesscom_url"],
            youtube_found=game["youtube_found"],
            chesscom_found=game["chesscom_found"],
        )
        session.add(new_game)
        session.commit()
        chesscom_id_to_game_id[game["game_id"]] = new_game.id

    # with open("data/series/Speedrun/positions.json") as f:
    with open(location[series_name]["positions"]) as f:
        positions = json.load(f)

    for position in positions:
        position = Positions(
            game_id=chesscom_id_to_game_id[position["game_id"]],
            ply=position["ply"],
            move_number=position["move_number"],
            san=position["san"],
            side_to_move_next=position["side_to_move_next"],
            fen=position["fen"],
            fen_key=position["fen_key"],
        )
        session.add(position)
        session.commit()
