import pandas as pd

import data_loader as dl


def _sample_records():
    return pd.DataFrame(
        [
            # Greece hosted Athens 1896 and won one event medal.
            {"Year": 1896, "Season": "Summer", "City": "Athina", "Region": "Greece",
             "NOC": "GRE", "Sport": "Athletics", "Event": "100m", "Medal": "Gold",
             "Name": "Athlete A", "Is_Preliminary_Entry": False},
            # France participated in 1896 but won no medals.
            {"Year": 1896, "Season": "Summer", "City": "Athina", "Region": "France",
             "NOC": "FRA", "Sport": "Athletics", "Event": "200m", "Medal": None,
             "Name": "Athlete B", "Is_Preliminary_Entry": False},
            # France hosted Paris 1900 and won one event medal.
            {"Year": 1900, "Season": "Summer", "City": "Paris", "Region": "France",
             "NOC": "FRA", "Sport": "Fencing", "Event": "Foil", "Medal": "Silver",
             "Name": "Athlete C", "Is_Preliminary_Entry": False},
            # Greece participated in 1900 but won no medals.
            {"Year": 1900, "Season": "Summer", "City": "Paris", "Region": "Greece",
             "NOC": "GRE", "Sport": "Athletics", "Event": "400m", "Medal": None,
             "Name": "Athlete D", "Is_Preliminary_Entry": False},
            # A 2026 roster row must not be counted as a completed medal result.
            {"Year": 2026, "Season": "Winter", "City": "Milano-Cortina", "Region": "Greece",
             "NOC": "GRE", "Sport": "Curling", "Event": "Mixed Doubles", "Medal": "Gold",
             "Name": "Athlete E", "Is_Preliminary_Entry": True},
        ]
    )


def test_host_analysis_retains_zero_medal_participations():
    summary, _, _ = dl.get_host_nation_analysis(_sample_records(), deduplicate=True)

    greece = summary.set_index("Region").loc["Greece"]
    france = summary.set_index("Region").loc["France"]

    assert greece["Host_Editions_Count"] == 1
    assert greece["Non_Host_Editions_Count"] == 1
    assert greece["Avg_Medals_When_Host"] == 1
    assert greece["Avg_Medals_Non_Host"] == 0

    assert france["Host_Editions_Count"] == 1
    assert france["Non_Host_Editions_Count"] == 1
    assert france["Avg_Medals_When_Host"] == 1
    assert france["Avg_Medals_Non_Host"] == 0


def test_preliminary_2026_rows_are_excluded_from_medal_tallies():
    df = _sample_records()

    deduplicated = dl.get_deduplicated_medals(df)
    assert not (deduplicated["Year"] == 2026).any()

    raw_tally = dl.get_medal_tally(df, year=2026, season="All", deduplicate=False)
    assert raw_tally.empty
