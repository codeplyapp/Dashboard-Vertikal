from __future__ import annotations

import math
from datetime import date

import pandas as pd
import pytest

from g7kaih import analytics
from g7kaih.constants import BATTALION_CODES, HABIT_KEYS

REFERENCE = {
    "bangun_pagi": {"hs": 85, "s": 117, "j": 29, "tp": 1},
    "ibadah": {"hs": 129, "s": 86, "j": 16, "tp": 1},
    "olahraga": {"hs": 98, "s": 114, "j": 19, "tp": 1},
    "makan_sehat": {"hs": 83, "s": 105, "j": 42, "tp": 2},
    "gemar_belajar": {"hs": 62, "s": 137, "j": 31, "tp": 2},
    "bermasyarakat": {"hs": 96, "s": 108, "j": 28, "tp": 0},
    "tidur_cepat": {"hs": 82, "s": 90, "j": 50, "tp": 10},
}


def test_summary_matches_reference(dataset: pd.DataFrame) -> None:
    summary = analytics.summary_table(dataset).set_index("habit_key")
    for key, expected in REFERENCE.items():
        row = summary.loc[key]
        for column, value in expected.items():
            assert int(row[column]) == value, f"{key}.{column}"


def test_positive_and_attention_totals(dataset: pd.DataFrame) -> None:
    summary = analytics.summary_table(dataset)
    assert (summary["positive"] + summary["attention"] == 232).all()
    assert summary.loc[summary["habit_key"] == "ibadah", "positive"].item() == 215
    assert summary.loc[summary["habit_key"] == "tidur_cepat", "attention"].item() == 60


def test_distribution_is_complete(dataset: pd.DataFrame) -> None:
    frame = analytics.distribution(dataset)
    assert len(frame) == 7 * 4
    assert frame.groupby("habit_key")["count"].sum().eq(232).all()
    assert frame["pct"].sum() == pytest.approx(700.0, abs=0.01)


def test_overall_index_formula(dataset: pd.DataFrame) -> None:
    mean_score = dataset[list(HABIT_KEYS)].to_numpy().mean()
    expected = (mean_score - 1) / 3 * 100
    assert analytics.overall_index(dataset) == pytest.approx(expected)
    assert 0 <= analytics.overall_index(dataset) <= 100


def test_index_by_habit(dataset: pd.DataFrame) -> None:
    frame = analytics.index_by_habit(dataset)
    assert len(frame) == 7
    assert frame["index"].between(0, 100).all()
    assert frame.loc[frame["habit_key"] == "ibadah", "index"].item() > frame.loc[
        frame["habit_key"] == "tidur_cepat", "index"
    ].item()


def test_battalion_attention_values(dataset: pd.DataFrame) -> None:
    frame = analytics.battalion_summary(dataset)
    pivot = frame.pivot(index="battalion", columns="habit_key", values="attention_pct")
    assert pivot.loc["XI", "tidur_cepat"] == pytest.approx(46.8085, abs=0.001)
    assert pivot.loc["XII", "makan_sehat"] == pytest.approx(29.7872, abs=0.001)
    assert pivot.loc["X", "gemar_belajar"] == pytest.approx(15.9420, abs=0.001)


def test_battalion_matrix_shape(dataset: pd.DataFrame) -> None:
    matrix = analytics.battalion_matrix(dataset)
    assert list(matrix.index) == list(BATTALION_CODES)
    assert matrix.shape == (3, 7)
    assert not matrix.isna().any().any()


def test_battalion_counts(dataset: pd.DataFrame) -> None:
    counts = analytics.battalion_counts(dataset).set_index("battalion")
    assert counts.loc["X", "n"] == 138
    assert counts["pct"].sum() == pytest.approx(100.0)


def test_timeline(dataset: pd.DataFrame) -> None:
    frame = analytics.timeline(dataset)
    assert len(frame) == 9
    assert frame["count"].sum() == 232
    assert frame["cumulative"].iloc[-1] == 232
    assert dict(zip(frame["date"].dt.date, frame["count"], strict=True)) == {
        date(2026, 10, 28): 1,
        date(2026, 11, 5): 114,
        date(2026, 11, 6): 8,
        date(2026, 11, 8): 24,
        date(2026, 11, 9): 19,
        date(2026, 11, 11): 51,
        date(2026, 11, 12): 2,
        date(2026, 11, 13): 12,
        date(2026, 11, 14): 1,
    }


def test_wave_summary(dataset: pd.DataFrame) -> None:
    frame = analytics.wave_summary(dataset).set_index("wave_key")
    assert frame.loc["G1", "entries"] == 114
    assert frame.loc["G2", "entries"] == 43
    assert frame.loc["G3", "entries"] == 51
    assert frame.loc["G4", "entries"] == 13
    assert frame.loc["LAIN", "entries"] == 11


def test_priority_matrix(dataset: pd.DataFrame) -> None:
    matrix = analytics.priority_matrix(dataset)
    assert len(matrix) == 7
    row = matrix.set_index("habit_key").loc["tidur_cepat"]
    assert row["quadrant"] == "Prioritas Tinggi"
    assert row["positive"] == 172
    assert row["attention"] == 60


def test_kpi_snapshot(dataset: pd.DataFrame) -> None:
    snapshot = analytics.kpi_snapshot(dataset, unique_students=203)
    assert snapshot.total_entries == 232
    assert snapshot.top_habit == "Beribadah"
    assert snapshot.priority_habit == "Tidur Cepat"
    assert snapshot.unique_students == 203
    assert snapshot.battalion_counts == {"X": 138, "XI": 47, "XII": 47}


def test_filtered_analytics(dataset: pd.DataFrame) -> None:
    subset = dataset[dataset["battalion"].astype(str) == "XI"]
    summary = analytics.summary_table(subset)
    assert summary["hs"].sum() + summary["s"].sum() + summary["j"].sum() + summary[
        "tp"
    ].sum() == 47 * 7


def test_empty_inputs_return_empty_frames(dataset: pd.DataFrame) -> None:
    empty = dataset.iloc[0:0].copy()
    assert analytics.summary_table(empty).empty
    assert analytics.distribution(empty).empty
    assert analytics.battalion_summary(empty).empty
    assert analytics.timeline(empty).empty
    assert analytics.wave_summary(empty).empty
    assert analytics.priority_matrix(empty).empty
    assert math.isnan(analytics.overall_index(empty))
    assert analytics.kpi_snapshot(empty).total_entries == 0
