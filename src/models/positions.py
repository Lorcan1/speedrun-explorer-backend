from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.database import Base

if TYPE_CHECKING:
    from src.models.games import Games

class Positions(Base):
    __tablename__ = "positions"
    id: Mapped[int] = mapped_column(primary_key=True)
    game_id: Mapped[int] = mapped_column(ForeignKey("games.id"), index=True)
    ply: Mapped[int] = mapped_column(Integer)
    move_number: Mapped[int] = mapped_column(Integer)
    san: Mapped[str] = mapped_column(String(100))
    side_to_move_next: Mapped[str] = mapped_column(String(100))
    fen: Mapped[str] = mapped_column(String(100))
    fen_key: Mapped[str] = mapped_column(String(100), index=True)
    


    game: Mapped["Games"] = relationship(back_populates="positions")
