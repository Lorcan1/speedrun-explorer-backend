import json
from datetime import datetime
from src.models.database import engine
from sqlalchemy.orm import Session

from src.models.creators import Creators
from src.models.database import Base
from src.models.games import Games
from src.models.positions import Positions
from src.models.series import Series

SERIES_NAME = "Sensei Speedrun"

chesscom_id_to_game_id = {}



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
        new_game = Games(
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
        session.add(new_game)
        session.commit()
        chesscom_id_to_game_id[game['game_id']] = new_game.id

    with open("data/positions.json") as f:
            positions = json.load(f)
    
    for position in positions:
        position = Positions(
        game_id = chesscom_id_to_game_id[position["game_id"]],
        ply = position['ply'],
        move_number = position["move_number"],
        san = position["san"],
        side_to_move_next = position["side_to_move_next"],
        fen = position["fen"],
        fen_key = position["fen_key"]
        )
        session.add(position)
        session.commit()