from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import Annotated

from fastapi import Query
from sqlalchemy import case, or_

from src.models.creators import Creators
from src.models.games import Games
from src.models.series import Series


class SpeedrunPlayerColourFilter(str, Enum):
    BOTH = "both"
    WHITE = "white"
    BLACK = "black"


@dataclass
class GameFilters:
    speedrun_player_colour_filter: SpeedrunPlayerColourFilter | None = None
    speedrunner_names: list[str] | None = None
    series_names: list[str] | None = None
    video_titles: list[str] | None = None
    min_game_date: date | None = None
    max_game_date: date | None = None
    min_elo_opponent: int | None = None
    max_elo_opponent: int | None = None
    min_elo_speedrunner: int | None = None
    max_elo_speedrunner: int | None = None
    result: str | None = None

    def apply(self, query):
        if self.speedrun_player_colour_filter and self.speedrun_player_colour_filter != SpeedrunPlayerColourFilter.BOTH:
            query = query.where(Games.speedrunner_colour == self.speedrun_player_colour_filter)
        if self.speedrunner_names is not None:
            sp_name_conditions = [Creators.name == speedrunner_name for speedrunner_name in self.speedrunner_names]
            query = query.where(or_(*sp_name_conditions))
        if self.series_names is not None:
            s_n_conditions = [Series.name == series_name for series_name in self.series_names]
            query = query.where(or_(*s_n_conditions))
        if self.video_titles is not None:
            v_t_conditions = [Games.youtube_video_title.ilike(f"%{video_title}%") for video_title in self.video_titles]
            query = query.where(or_(*v_t_conditions))
        if self.min_game_date is not None:
            query = query.where(Games.game_date >= self.min_game_date)
        if self.max_game_date is not None:
            query = query.where(Games.game_date <= self.max_game_date)
        if self.min_elo_opponent is not None:
            query = query.where(self._opponent_elo_expr() >= self.min_elo_opponent)
        if self.max_elo_opponent is not None:
            query = query.where(self._opponent_elo_expr() <= self.max_elo_opponent)
        if self.min_elo_speedrunner is not None:
            query = query.where(self._speedrunner_elo_expr() >= self.min_elo_speedrunner)
        if self.max_elo_speedrunner is not None:
            query = query.where(self._speedrunner_elo_expr() <= self.max_elo_speedrunner)
        if self.result is not None:
            query = query.where(Games.result == self.result)
        return query

    def _speedrunner_elo_expr(self):
        return case(
            (Games.speedrunner_colour == SpeedrunPlayerColourFilter.WHITE, Games.white_elo),
            (Games.speedrunner_colour == SpeedrunPlayerColourFilter.BLACK, Games.black_elo),
        )

    def _opponent_elo_expr(self):
        return case(
            (Games.speedrunner_colour == SpeedrunPlayerColourFilter.WHITE, Games.black_elo),
            (Games.speedrunner_colour == SpeedrunPlayerColourFilter.BLACK, Games.white_elo),
        )


def get_game_filters(
    speedrun_player_colour_filter: SpeedrunPlayerColourFilter | None = None,
    speedrunner_names: Annotated[list[str] | None, Query()] = None,
    series_names: Annotated[list[str] | None, Query()] = None,
    video_titles: Annotated[list[str] | None, Query()] = None,
    min_game_date: date | None = None,
    max_game_date: date | None = None,
    min_elo_opponent: int | None = None,
    max_elo_opponent: int | None = None,
    min_elo_speedrunner: int | None = None,
    max_elo_speedrunner: int | None = None,
    result: str | None = None,
) -> GameFilters:
    return GameFilters(
        speedrun_player_colour_filter=speedrun_player_colour_filter,
        speedrunner_names=speedrunner_names,
        series_names=series_names,
        video_titles=video_titles,
        min_game_date=min_game_date,
        max_game_date=max_game_date,
        min_elo_opponent=min_elo_opponent,
        max_elo_opponent=max_elo_opponent,
        min_elo_speedrunner=min_elo_speedrunner,
        max_elo_speedrunner=max_elo_speedrunner,
        result=result,
    )