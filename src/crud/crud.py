from sqlalchemy import func, select, tuple_

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


def get_current_moves(db, fen_trimmed, filters):
    stmt = (
        select(Positions, Series, Games)
        .join(Games, Positions.game_id == Games.id)
        .join(Series, Games.series_id == Series.id)
        .where(fen_trimmed == Positions.fen_key)
    )
    stmt = filters.apply(stmt)

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


def get_current_games(db, fen_trimmed, filters, page: int, limit: int):
    stmt = (
        select(Positions, Series, Games, Creators)
        .join(Games, Positions.game_id == Games.id)
        .join(Series, Games.series_id == Series.id)
        .join(Creators, Series.creator_id == Creators.id)
        .where(fen_trimmed == Positions.fen_key)
        .order_by(Games.game_date.desc())
        .limit(limit)
        .offset((page - 1) * limit)
    )
    stmt = filters.apply(stmt)

    return db.execute(stmt).all()


def count_current_games(db, fen_trimmed, filters):
    stmt = (
        select(func.count(Games.id))
        .select_from(Positions)
        .join(Games, Positions.game_id == Games.id)
        .where(fen_trimmed == Positions.fen_key)
    )

    stmt = filters.apply(stmt)

    return db.scalar(stmt)


def filter_options_crud(db, col_type, search, limit, filters):
    if col_type == "speedrunner":
        val = Creators.name
    elif col_type == "series":
        val = Series.name
    elif col_type == "video_title":
        val = Games.youtube_video_title

    stmt = select(val).distinct().where(val.ilike(f"%{search}%")).limit(limit)

    # stmt = filters.apply(stmt)
    stmt = stmt.limit(limit)

    
    results = db.execute(stmt).scalars().all()
    return results