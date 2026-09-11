from sqlalchemy import select, delete
from src.models.positions import Positions
from src.models.games import Games
from src.models.series import Series
from src.data_scripts.ingest_db.ingest_db import engine, Session

SERIES_NAME_2 = "DYI Develop Your Instincts Speedrun"

with Session(engine) as session:
    s3 = session.scalar(select(Series).where(Series.name == SERIES_NAME_2))
    game_ids = session.scalars(select(Games.id).where(Games.series_id == s3.id)).all()
    session.execute(delete(Positions).where(Positions.game_id.in_(game_ids)))
    session.execute(delete(Games).where(Games.series_id == s3.id))
    # optional: also delete the Series row if you want it fully recreated
    session.execute(delete(Series).where(Series.id == s3.id))
    session.commit()