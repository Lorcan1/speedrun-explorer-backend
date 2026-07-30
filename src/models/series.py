from typing import TYPE_CHECKING

from src.models.database import Base
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from src.models.creator import Creator
    from src.models.games import Games

class Series(Base):
    __tablename__ = "series"
    id: Mapped[int] = mapped_column(primary_key=True)
    creator_id: Mapped[int] = mapped_column(ForeignKey("creators.id"), index= True)
    name: Mapped[str] = mapped_column(String(100))

    creator: Mapped["Creator"] = relationship(back_populates="series")
    games: Mapped[list["Games"]] = relationship(back_populates="series")