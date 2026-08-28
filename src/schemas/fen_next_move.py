from pydantic import BaseModel


class GameEntry(BaseModel):
    opponent: str
    youtube_url: str
    chesscom_url: str
    speedrun_player_colour: str
    result: str


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