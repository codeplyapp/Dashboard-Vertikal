from __future__ import annotations

import pandas as pd

from g7kaih.insights import build_insights, build_recommendations


def test_insights_default(dataset: pd.DataFrame, meta: dict) -> None:
    insights = build_insights(dataset, meta)
    titles = " ".join(item.title for item in insights)
    assert "Beribadah" in titles
    assert "Tidur Cepat" in titles
    assert len(insights) >= 3


def test_insight_details_contain_numbers(dataset: pd.DataFrame, meta: dict) -> None:
    for insight in build_insights(dataset, meta):
        assert any(character.isdigit() for character in insight.detail)


def test_recommendations(dataset: pd.DataFrame) -> None:
    recommendations = build_recommendations(dataset)
    assert len(recommendations) == 3
    assert recommendations[0].title.endswith("Tidur Cepat")
    assert all("entri" in item.evidence for item in recommendations)
    assert all(item.action for item in recommendations)


def test_insights_empty(dataset: pd.DataFrame) -> None:
    empty = dataset.iloc[0:0].copy()
    insights = build_insights(empty, {"unique_students": 203})
    assert len(insights) == 1
    assert insights[0].tone == "neutral"
    assert build_recommendations(empty) == []
