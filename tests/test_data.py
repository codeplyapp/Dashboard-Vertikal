from __future__ import annotations

from datetime import date

import pandas as pd
import pytest

from g7kaih.constants import HABIT_KEYS
from g7kaih.data import (
    DataValidationError,
    Filters,
    active_filter_label,
    apply_filters,
    load_dataset,
    validate_dataset,
)


def test_dataset_shape_and_schema(dataset: pd.DataFrame) -> None:
    assert len(dataset) == 232
    for column in ("entry_id", "timestamp", "date", "battalion", "total_score", "index"):
        assert column in dataset.columns
    for key in HABIT_KEYS:
        assert key in dataset.columns


def test_dataset_has_no_missing_values(dataset: pd.DataFrame) -> None:
    assert not dataset.isna().any().any()


def test_scores_within_domain(dataset: pd.DataFrame) -> None:
    scores = dataset[list(HABIT_KEYS)]
    assert int(scores.min().min()) >= 1
    assert int(scores.max().max()) <= 4


def test_battalion_distribution(dataset: pd.DataFrame) -> None:
    counts = dataset["battalion"].astype(str).value_counts().to_dict()
    assert counts == {"X": 138, "XI": 47, "XII": 47}


def test_date_range(dataset: pd.DataFrame) -> None:
    assert min(dataset["date"]) == date(2026, 10, 28)
    assert max(dataset["date"]) == date(2026, 11, 14)


def test_meta_matches_dataset(dataset: pd.DataFrame, meta: dict) -> None:
    assert meta["total_entries"] == len(dataset) == 232
    assert meta["unique_students"] == 203
    assert meta["battalion_counts"] == {"X": 138, "XI": 47, "XII": 47}


def test_filter_by_battalion(dataset: pd.DataFrame) -> None:
    filtered = apply_filters(dataset, Filters(battalions=("XI",)))
    assert len(filtered) == 47
    assert set(filtered["battalion"].astype(str)) == {"XI"}


def test_filter_by_date_range(dataset: pd.DataFrame) -> None:
    filtered = apply_filters(
        dataset, Filters(start=date(2026, 11, 11), end=date(2026, 11, 11))
    )
    assert len(filtered) == 51


def test_filter_returns_empty_frame(dataset: pd.DataFrame) -> None:
    filtered = apply_filters(
        dataset, Filters(battalions=("XI",), start=date(2026, 10, 28), end=date(2026, 10, 28))
    )
    assert filtered.empty
    assert set(filtered.columns) == set(dataset.columns)


def test_filter_habit_does_not_drop_rows(dataset: pd.DataFrame) -> None:
    filtered = apply_filters(dataset, Filters(habit="tidur_cepat"))
    assert len(filtered) == len(dataset)


def test_filter_does_not_mutate_input(dataset: pd.DataFrame) -> None:
    before = dataset.copy()
    apply_filters(dataset, Filters(battalions=("X",)))
    pd.testing.assert_frame_equal(dataset, before)


def test_unknown_battalion_raises(dataset: pd.DataFrame) -> None:
    with pytest.raises(DataValidationError):
        apply_filters(dataset, Filters(battalions=("XIII",)))


def test_unknown_habit_raises(dataset: pd.DataFrame) -> None:
    with pytest.raises(DataValidationError):
        apply_filters(dataset, Filters(habit="merokok"))


def test_validate_rejects_invalid_score(dataset: pd.DataFrame) -> None:
    broken = dataset.copy()
    broken.loc[0, "ibadah"] = 9
    with pytest.raises(DataValidationError):
        validate_dataset(broken)


def test_active_filter_label(dataset: pd.DataFrame) -> None:
    label = active_filter_label(dataset, Filters())
    assert "232 entri" in label
    assert "Semua batalyon" in label


def test_load_dataset_missing_file(tmp_path) -> None:
    with pytest.raises(FileNotFoundError):
        load_dataset(tmp_path / "tidak-ada.json")
