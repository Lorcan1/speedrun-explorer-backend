from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Date, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.database import Base

if TYPE_CHECKING:
    from src.models.positions import Positions
    from src.models.series import Series


class Games(Base):
    __tablename__ = "games"
    id: Mapped[int] = mapped_column(primary_key=True)
    series_id: Mapped[int] = mapped_column(ForeignKey("series.id"), index=True)
    white: Mapped[str] = mapped_column(String(100))
    black: Mapped[str] = mapped_column(String(100))
    result: Mapped[str] = mapped_column(String(100))
    speedrunner_result: Mapped[str] = mapped_column(String(100))
    white_elo: Mapped[int] = mapped_column(Integer)
    black_elo: Mapped[int] = mapped_column(Integer)
    speedrunner_colour: Mapped[str | None] = mapped_column(String(100))
    speedrunner_elo: Mapped[int | None] = mapped_column(Integer) 
    game_date: Mapped[date | None] = mapped_column(Date)
    eco: Mapped[str | None] = mapped_column(String(100))
    opening: Mapped[str | None] = mapped_column(String(100))
    time_control: Mapped[str | None] = mapped_column(String(100))
    termination: Mapped[str | None] = mapped_column(String(100))
    youtube_url: Mapped[str | None] = mapped_column(String(100))
    youtube_video_title: Mapped[str | None] = mapped_column(String(100))
    chesscom_url: Mapped[str | None] = mapped_column(String(100))
    youtube_found: Mapped[bool] = mapped_column(Boolean, default=False)
    chesscom_found: Mapped[bool] = mapped_column(Boolean, default=False)

    series: Mapped["Series"] = relationship(back_populates="games")
    positions: Mapped[list["Positions"]] = relationship(back_populates="game")

