import json
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from src.models.creators import Creators
from src.models.database import Base
from src.models.games import Games
from src.models.positions import Positions
from src.models.series import Series

SERIES_NAME = "Sensei Speedrun"


engine = create_engine("sqlite:///./data/chess_positions.db")

Base.metadata.create_all(engine)

with Session(engine) as session:
    danya = Creators(name="Daniel Naroditsky")
    session.add(danya)
    session.commit()
    sensei = Series(creator_id = danya.id, name = SERIES_NAME)
    session.add(sensei)
    session.commit()

    with open("data/games.json") as f:
        games = json.load(f)

    for game in games:
        game = Games(
        series_id = sensei.id,
        white = game["white"], 
        black = game["black"],
        result = game["result"],
        white_elo = game["white_elo"],
        black_elo = game["black_elo"],
        game_date = datetime.strptime(game["date"], "%Y.%m.%d").date(),
        eco = game["eco"],
        opening = game["opening"],
        time_control = game["time_control"],
        termination = game["termination"],
        youtube_url = game["youtube_url"],
        chesscom_url = game["chesscom_url"],
        youtube_found = game["youtube_found"],
        chesscom_found = game["chesscom_found"],
        )
        session.add(game)
        session.commit()