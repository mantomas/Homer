"""Heating utilities and classes"""

import dataclasses
from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(init=False)
class SeasonStats:
    """Single heating season statistics"""

    season: str
    total_rounds: int
    total_weight: float
    avg_weight: float
    avg_weight_per_day: float
    season_start: datetime
    season_end: datetime
    season_days: int
    average_round: float
    avg_temp_in: float
    avg_temp_out: float

    def __init__(self, records):
        season_days = (records[-1].burn_date - records[0].burn_date).days + 1
        total_weight = sum([record.weight for record in records])
        temperatures_in = [record.temperature_in for record in records]
        temperatures_out = [record.temperature_out for record in records]
        self.season = records[0].season
        self.total_rounds = len(records)
        self.total_weight = total_weight
        self.avg_weight = total_weight / len(records)
        self.avg_weight_per_day = total_weight / season_days
        self.season_start = records[0].burn_date
        self.season_end = records[-1].burn_date
        self.season_days = season_days
        self.average_round = (season_days * 24) / len(records)
        self.avg_temp_in = sum(temperatures_in) / len(records)
        self.avg_temp_out = sum(temperatures_out) / len(records)

    @property
    def statistics(self):
        return dataclasses.asdict(self)


@dataclass
class AllSeasons:
    seasons: list[SeasonStats]

    @property
    def statistics(self):
        base_stats = [season.statistics for season in self.seasons]
        updated_stats = self.enrich_stats(base_stats)
        return updated_stats

    def shift_date(self, dt: datetime) -> tuple[int, int]:
        """
        Helper function to enable comparing month-day relative to
        a season (season lasts from July 1st to June 30th)
        E.g. December 1st is lower than January 1st
        """
        shift_month = dt.month if dt.month >= 7 else dt.month + 12
        return (shift_month, dt.day)

    def enrich_stats(
        self,
        data: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        fields_to_compare = (
            "season_days",
            "total_rounds",
            "total_weight",
            "avg_weight",
            "avg_weight_per_day",
            "average_round",
            "avg_temp_in",
            "avg_temp_out",
        )
        date_fields_to_compare = (
            "season_start",
            "season_end",
        )
        for season in data:
            for field in fields_to_compare:
                season[f"max_{field}"] = season[field] == max(s[field] for s in data)
                season[f"min_{field}"] = season[field] == min(s[field] for s in data)
            for field in date_fields_to_compare:
                season[f"max_{field}"] = self.shift_date(season[field]) == max(
                    self.shift_date(s[field]) for s in data
                )
                season[f"min_{field}"] = self.shift_date(season[field]) == min(
                    self.shift_date(s[field]) for s in data
                )

        return data
