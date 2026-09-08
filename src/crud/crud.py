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


def get_current_games(db, fen_trimmed, filters, page: int, limit: int, sort: str):

    sort_param = sort_param_helper(sort)

    
    stmt = (
        select(Positions, Series, Games, Creators)
        .join(Games, Positions.game_id == Games.id)
        .join(Series, Games.series_id == Series.id)
        .join(Creators, Series.creator_id == Creators.id)
        .where(fen_trimmed == Positions.fen_key)
        .limit(limit)
        .offset((page - 1) * limit)
        .order_by(sort_param)
    
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

def sort_param_helper(sort):
    sort_param = Games.id.desc()
    
    asc = True

    if sort:
        if sort.startswith("-"):
            sort = sort[1:]
            asc = False
            
        if sort == "video_title":
            sort_param = Games.youtube_video_title
        elif sort == "series":
            sort_param = Series.name
        elif sort == "speedrunner":
            sort_param = Creators.name
        elif sort == "game_date":
            sort_param = Games.game_date
        elif sort == "speedrunner_elo":
            sort_param = Games.speedrunner_elo

        if asc:
            sort_param = sort_param.asc()
        else:
            sort_param = sort_param.desc()
    return sort_param 


def filter_options_crud(db, col_type, search, limit, filters):
    if col_type == "speedrunner":
        val = Creators.name
        if filters.speedrunner_names:
            filters.speedrunner_names = None
    elif col_type == "series":
        val = Series.name
        if filters.series_names:
            filters.series_names = None
    elif col_type == "video_title":
        val = Games.youtube_video_title
        if filters.video_titles:
            filters.video_titles = None

    stmt = select(val).distinct().where(val.ilike(f"%{search}%")).limit(limit)

    stmt = filters.apply(stmt)
    stmt = stmt.limit(limit)

    
    results = db.execute(stmt).scalars().all()
    return results