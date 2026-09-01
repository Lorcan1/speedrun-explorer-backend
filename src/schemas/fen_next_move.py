from pydantic import BaseModel
from datetime import date



class GameEntry(BaseModel):
    opponent: str
    youtube_url: str | None
    chesscom_url: str
    speedrun_player_colour: str
    result: str
    white_elo: int
    black_elo: int
    game_date: date


class NextMoveBucket(BaseModel):
    san: str
    count: int
    games: list[GameEntry]

class EndingBucket(BaseModel):
    termination: str
    speedrunner_result: str
    count: int
    games: list [GameEntry]


class FenNextMoveResponse(BaseModel):
    position_fen: str
    total_games: int
    next_moves: list[NextMoveBucket]
    game_endings: list[EndingBucket]