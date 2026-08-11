from sqlalchemy import select, tuple_

from src.models.creators import Creators  # noqa: F401
from src.models.games import Games
from src.models.positions import Positions
from src.models.series import Series


def get_current_moves_positions(db, fen_trimmed):
    return (
        db.execute(select(Positions).where(Positions.fen_key == fen_trimmed))
        .scalars()
        .all()
    )


def get_current_moves(db, fen_trimmed):
    stmt = (
        select(Positions, Series, Games)
        .join(Games, Positions.game_id == Games.id)
        .join(Series, Games.series_id == Series.id)
        .where(fen_trimmed == Positions.fen_key)
    )

    return db.execute(stmt).all()


def get_next_moves(db, p_plus_one):
    return (
        db.execute(
            select(Positions).where(
                tuple_(Positions.game_id, Positions.ply).in_(p_plus_one)
            )
        )
        .scalars()
        .all()
    )
