from datetime import date

from homer.main.heating import AllSeasons, SeasonStats
from homer.models import Heating


s1_heating1 = {
    "weight": 10,
    "burn_date": date(2023, 9, 15),
    "temperature_in": 19,
    "temperature_out": 10,
    "season": "2023-2024",
}
s1_heating2 = {
    "weight": 10,
    "burn_date": date(2023, 9, 18),
    "temperature_in": 19,
    "temperature_out": 10,
    "season": "2023-2024",
}
s2_heating1 = {
    "weight": 8,
    "burn_date": date(2025, 1, 1),
    "temperature_in": 20,
    "temperature_out": 15,
    "season": "2024-2025",
}
s2_heating2 = {
    "weight": 8,
    "burn_date": date(2025, 1, 2),
    "temperature_in": 20,
    "temperature_out": 15,
    "season": "2024-2025",
}
s2_heating3 = {
    "weight": 8,
    "burn_date": date(2025, 1, 3),
    "temperature_in": 20,
    "temperature_out": 15,
    "season": "2024-2025",
}


def test_season_stats(app):
    season = SeasonStats([Heating(**s1_heating1), Heating(**s1_heating2)])
    expected = {
        "season": "2023-2024",
        "total_rounds": 2,
        "total_weight": 20,
        "avg_weight": 10.0,
        "avg_weight_per_day": 5.0,
        "season_start": date(2023, 9, 15),
        "season_end": date(2023, 9, 18),
        "season_days": 4,
        "average_round": 48.0,
        "avg_temp_in": 19.0,
        "avg_temp_out": 10.0,
    }
    assert season.statistics == expected


def test_all_seasons(app):
    season1 = SeasonStats([Heating(**s1_heating1), Heating(**s1_heating2)])
    season2 = SeasonStats(
        [Heating(**s2_heating1), Heating(**s2_heating2), Heating(**s2_heating3)]
    )
    all_seasons = AllSeasons([season1, season2])
    for season in all_seasons.statistics:
        if season["season"] == "2023-2024":
            assert all(
                [
                    season["max_season_days"] is True,
                    season["min_season_days"] is False,
                    season["max_total_rounds"] is False,
                    season["min_total_rounds"] is True,
                    season["max_total_weight"] is False,
                    season["min_total_weight"] is True,
                    season["max_avg_weight"] is True,
                    season["min_avg_weight"] is False,
                    season["max_avg_weight_per_day"] is False,
                    season["min_avg_weight_per_day"] is True,
                    season["max_average_round"] is True,
                    season["min_average_round"] is False,
                    season["max_avg_temp_in"] is False,
                    season["min_avg_temp_in"] is True,
                    season["max_avg_temp_out"] is False,
                    season["min_avg_temp_out"] is True,
                    season["max_season_start"] is False,
                    season["min_season_start"] is True,
                    season["max_season_end"] is False,
                    season["min_season_end"] is True,
                ]
            )
        if season["season"] == "2024-2025":
            assert all(
                [
                    season["max_season_days"] is False,
                    season["min_season_days"] is True,
                    season["max_total_rounds"] is True,
                    season["min_total_rounds"] is False,
                    season["max_total_weight"] is True,
                    season["min_total_weight"] is False,
                    season["max_avg_weight"] is False,
                    season["min_avg_weight"] is True,
                    season["max_avg_weight_per_day"] is True,
                    season["min_avg_weight_per_day"] is False,
                    season["max_average_round"] is False,
                    season["min_average_round"] is True,
                    season["max_avg_temp_in"] is True,
                    season["min_avg_temp_in"] is False,
                    season["max_avg_temp_out"] is True,
                    season["min_avg_temp_out"] is False,
                    season["max_season_start"] is True,
                    season["min_season_start"] is False,
                    season["max_season_end"] is True,
                    season["min_season_end"] is False,
                ]
            )
