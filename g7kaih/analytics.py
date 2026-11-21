"""Fungsi analitik murni untuk dashboard 7 KAIH.

Semua fungsi menerima DataFrame tervalidasi dan mengembalikan objek baru
tanpa melakukan I/O maupun menyimpan state.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

import pandas as pd

from g7kaih.constants import (
    ATTENTION_BENCHMARK,
    ATTENTION_LABELS,
    BATTALION_BY_CODE,
    BATTALION_CODES,
    HABIT_KEYS,
    HABIT_LABELS,
    HABITS,
    MAX_SCORE,
    MIN_SCORE,
    OTHER_WAVE_KEY,
    OTHER_WAVE_LABEL,
    POSITIVE_BENCHMARK,
    POSITIVE_LABELS,
    SCALE_BY_SCORE,
    WAVES,
    wave_for,
)

SUMMARY_COLUMNS: tuple[str, ...] = (
    "habit_key",
    "habit",
    "hs",
    "s",
    "j",
    "tp",
    "positive",
    "positive_pct",
    "attention",
    "attention_pct",
    "mean_score",
    "index",
)
DISTRIBUTION_COLUMNS: tuple[str, ...] = (
    "habit_key",
    "habit",
    "habit_short",
    "category",
    "score",
    "count",
    "pct",
)
BATTALION_COLUMNS: tuple[str, ...] = (
    "battalion",
    "battalion_name",
    "class_label",
    "n",
    "habit_key",
    "habit",
    "positive",
    "positive_pct",
    "attention",
    "attention_pct",
    "index",
)
TIMELINE_COLUMNS: tuple[str, ...] = (
    "date",
    "count",
    "cumulative",
    "wave_key",
    "wave_label",
)
MATRIX_COLUMNS: tuple[str, ...] = (
    "habit_key",
    "habit",
    "positive",
    "positive_pct",
    "attention",
    "attention_pct",
    "n",
    "quadrant",
)
WAVE_COLUMNS: tuple[str, ...] = ("wave_key", "wave_label", "entries", "pct", "date_range")


@dataclass(frozen=True, slots=True)
class KpiSnapshot:
    """Ringkasan angka utama untuk kartu KPI."""

    total_entries: int
    unique_students: int | None
    overall_index: float
    top_habit: str
    top_positive_pct: float
    priority_habit: str
    priority_attention_pct: float
    date_min: date | None
    date_max: date | None
    battalion_counts: dict[str, int] = field(default_factory=dict)
    focus_habit: str | None = None
    focus_index: float | None = None


def _present_battalions(df: pd.DataFrame) -> list[str]:
    present = set(df["battalion"].astype(str)) if not df.empty else set()
    return [code for code in BATTALION_CODES if code in present]


def _score_counts(series: pd.Series) -> dict[int, int]:
    counts = series.value_counts().reindex([4, 3, 2, 1], fill_value=0)
    return {int(score): int(counts.loc[score]) for score in (4, 3, 2, 1)}


def _normalized_index(mean_score: float) -> float:
    return (mean_score - MIN_SCORE) / (MAX_SCORE - MIN_SCORE) * 100


def _quadrant(positive_pct: float, attention_pct: float) -> str:
    if positive_pct < POSITIVE_BENCHMARK and attention_pct >= ATTENTION_BENCHMARK:
        return "Prioritas Tinggi"
    if positive_pct < POSITIVE_BENCHMARK:
        return "Pantau"
    if attention_pct >= ATTENTION_BENCHMARK:
        return "Waspada"
    return "Pertahankan"


def distribution(df: pd.DataFrame) -> pd.DataFrame:
    """Distribusi 4 skala jawaban untuk setiap kebiasaan (long format)."""
    if df.empty:
        return pd.DataFrame(columns=list(DISTRIBUTION_COLUMNS))
    total = len(df)
    rows: list[dict[str, object]] = []
    for habit in HABITS:
        counts = _score_counts(df[habit.key])
        for score in (4, 3, 2, 1):
            count = counts[score]
            rows.append(
                {
                    "habit_key": habit.key,
                    "habit": habit.label,
                    "habit_short": habit.short_label,
                    "category": SCALE_BY_SCORE[score],
                    "score": score,
                    "count": count,
                    "pct": count / total * 100,
                }
            )
    return pd.DataFrame(rows, columns=list(DISTRIBUTION_COLUMNS))


def summary_table(df: pd.DataFrame) -> pd.DataFrame:
    """Rekapitulasi absolut dan persentase per kebiasaan."""
    if df.empty:
        return pd.DataFrame(columns=list(SUMMARY_COLUMNS))
    total = len(df)
    rows: list[dict[str, object]] = []
    for habit in HABITS:
        counts = _score_counts(df[habit.key])
        positive = sum(counts[score] for score in (4, 3))
        attention = sum(counts[score] for score in (2, 1))
        mean_score = float(df[habit.key].mean())
        rows.append(
            {
                "habit_key": habit.key,
                "habit": habit.label,
                "hs": counts[4],
                "s": counts[3],
                "j": counts[2],
                "tp": counts[1],
                "positive": positive,
                "positive_pct": positive / total * 100,
                "attention": attention,
                "attention_pct": attention / total * 100,
                "mean_score": mean_score,
                "index": _normalized_index(mean_score),
            }
        )
    return pd.DataFrame(rows, columns=list(SUMMARY_COLUMNS))


def battalion_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Rekapitulasi per batalyon x kebiasaan (long format)."""
    if df.empty:
        return pd.DataFrame(columns=list(BATTALION_COLUMNS))
    rows: list[dict[str, object]] = []
    for code in _present_battalions(df):
        battalion = BATTALION_BY_CODE[code]
        subset = df[df["battalion"].astype(str) == code]
        total = len(subset)
        for habit in HABITS:
            counts = _score_counts(subset[habit.key])
            positive = sum(counts[score] for score in (4, 3))
            attention = sum(counts[score] for score in (2, 1))
            rows.append(
                {
                    "battalion": code,
                    "battalion_name": battalion.name,
                    "class_label": battalion.class_label,
                    "n": total,
                    "habit_key": habit.key,
                    "habit": habit.label,
                    "positive": positive,
                    "positive_pct": positive / total * 100 if total else 0.0,
                    "attention": attention,
                    "attention_pct": attention / total * 100 if total else 0.0,
                    "index": _normalized_index(float(subset[habit.key].mean())),
                }
            )
    return pd.DataFrame(rows, columns=list(BATTALION_COLUMNS))


def battalion_matrix(df: pd.DataFrame, value: str = "attention_pct") -> pd.DataFrame:
    """Matriks batalyon x kebiasaan untuk heatmap."""
    summary = battalion_summary(df)
    if summary.empty:
        return pd.DataFrame(columns=[habit.label for habit in HABITS])
    matrix = summary.pivot_table(index="battalion", columns="habit", values=value)
    matrix = matrix.reindex(index=_present_battalions(df))
    matrix = matrix.reindex(columns=[habit.label for habit in HABITS])
    return matrix


def battalion_counts(df: pd.DataFrame) -> pd.DataFrame:
    """Jumlah dan proporsi entri per batalyon."""
    columns = ["battalion", "battalion_name", "class_label", "n", "pct"]
    if df.empty:
        return pd.DataFrame(columns=columns)
    total = len(df)
    rows: list[dict[str, object]] = []
    for code in _present_battalions(df):
        battalion = BATTALION_BY_CODE[code]
        count = int((df["battalion"].astype(str) == code).sum())
        rows.append(
            {
                "battalion": code,
                "battalion_name": battalion.name,
                "class_label": battalion.class_label,
                "n": count,
                "pct": count / total * 100,
            }
        )
    return pd.DataFrame(rows, columns=columns)


def timeline(df: pd.DataFrame) -> pd.DataFrame:
    """Jumlah entri per tanggal beserta kumulatif dan label gelombang."""
    if df.empty:
        return pd.DataFrame(columns=list(TIMELINE_COLUMNS))
    grouped = (
        df.groupby("date", as_index=False)
        .size()
        .rename(columns={"size": "count"})
        .sort_values("date")
    )
    grouped["cumulative"] = grouped["count"].cumsum()
    grouped["date"] = pd.to_datetime(grouped["date"])
    wave_keys: list[str] = []
    wave_labels: list[str] = []
    for value in grouped["date"].dt.date:
        key, label = wave_for(value)
        wave_keys.append(key)
        wave_labels.append(label)
    grouped["wave_key"] = wave_keys
    grouped["wave_label"] = wave_labels
    return grouped[list(TIMELINE_COLUMNS)]


def wave_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Rekapitulasi entri per gelombang pengisian."""
    if df.empty:
        return pd.DataFrame(columns=list(WAVE_COLUMNS))
    total = len(df)
    labels = {wave.key: wave.label for wave in WAVES}
    labels[OTHER_WAVE_KEY] = OTHER_WAVE_LABEL
    order = [wave.key for wave in WAVES] + [OTHER_WAVE_KEY]
    frame = pd.DataFrame({"date": pd.to_datetime(df["date"])})
    frame["wave_key"] = frame["date"].dt.date.map(lambda value: wave_for(value)[0])
    grouped = frame.groupby("wave_key").agg(
        entries=("date", "size"),
        date_min=("date", "min"),
        date_max=("date", "max"),
    )
    rows: list[dict[str, object]] = []
    for key in order:
        if key not in grouped.index:
            continue
        row = grouped.loc[key]
        start = row["date_min"].date()
        end = row["date_max"].date()
        date_range = (
            f"{start.day} {start.strftime('%b')}"
            if start == end
            else f"{start.day}–{end.day} {end.strftime('%b')}"
        )
        rows.append(
            {
                "wave_key": key,
                "wave_label": labels[key],
                "entries": int(row["entries"]),
                "pct": int(row["entries"]) / total * 100,
                "date_range": date_range,
            }
        )
    return pd.DataFrame(rows, columns=list(WAVE_COLUMNS))


def index_by_habit(df: pd.DataFrame) -> pd.DataFrame:
    """Indeks 0-100 per kebiasaan."""
    columns = ["habit_key", "habit", "mean_score", "index"]
    if df.empty:
        return pd.DataFrame(columns=columns)
    rows = []
    for habit in HABITS:
        mean_score = float(df[habit.key].mean())
        rows.append(
            {
                "habit_key": habit.key,
                "habit": habit.label,
                "mean_score": mean_score,
                "index": _normalized_index(mean_score),
            }
        )
    return pd.DataFrame(rows, columns=columns)


def overall_index(df: pd.DataFrame) -> float:
    """Indeks 7KAIH keseluruhan (0-100)."""
    if df.empty:
        return float("nan")
    mean_score = float(df[list(HABIT_KEYS)].to_numpy().mean())
    return _normalized_index(mean_score)


def priority_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """Titik kebiasaan pada matriks prioritas."""
    if df.empty:
        return pd.DataFrame(columns=list(MATRIX_COLUMNS))
    summary = summary_table(df)
    total = len(df)
    rows = []
    for _, row in summary.iterrows():
        rows.append(
            {
                "habit_key": row["habit_key"],
                "habit": row["habit"],
                "positive": int(row["positive"]),
                "positive_pct": float(row["positive_pct"]),
                "attention": int(row["attention"]),
                "attention_pct": float(row["attention_pct"]),
                "n": total,
                "quadrant": _quadrant(float(row["positive_pct"]), float(row["attention_pct"])),
            }
        )
    return pd.DataFrame(rows, columns=list(MATRIX_COLUMNS))


def top_and_bottom(df: pd.DataFrame) -> tuple[pd.Series, pd.Series]:
    """Kebiasaan dengan persentase positif tertinggi dan terendah."""
    summary = summary_table(df)
    if summary.empty:
        raise ValueError("Tidak ada data untuk dihitung.")
    top = summary.loc[summary["positive_pct"].idxmax()]
    bottom = summary.loc[summary["positive_pct"].idxmin()]
    return top, bottom


def attention_by_battalion(df: pd.DataFrame, habit_key: str) -> pd.DataFrame:
    """Persentase 'perlu perhatian' satu kebiasaan per batalyon."""
    columns = ["battalion", "battalion_name", "n", "attention", "attention_pct"]
    summary = battalion_summary(df)
    if summary.empty:
        return pd.DataFrame(columns=columns)
    subset = summary[summary["habit_key"] == habit_key]
    return subset[columns].reset_index(drop=True)


def kpi_snapshot(df: pd.DataFrame, unique_students: int | None = None) -> KpiSnapshot:
    """Hitung seluruh angka kartu KPI dari data terfilter."""
    if df.empty:
        return KpiSnapshot(
            total_entries=0,
            unique_students=unique_students,
            overall_index=float("nan"),
            top_habit="–",
            top_positive_pct=float("nan"),
            priority_habit="–",
            priority_attention_pct=float("nan"),
            date_min=None,
            date_max=None,
        )
    top, _ = top_and_bottom(df)
    summary = summary_table(df)
    priority = summary.loc[summary["attention_pct"].idxmax()]
    counts = {
        row["battalion"]: int(row["n"])
        for _, row in battalion_counts(df).iterrows()
    }
    return KpiSnapshot(
        total_entries=len(df),
        unique_students=unique_students,
        overall_index=overall_index(df),
        top_habit=str(top["habit"]),
        top_positive_pct=float(top["positive_pct"]),
        priority_habit=str(priority["habit"]),
        priority_attention_pct=float(priority["attention_pct"]),
        date_min=min(df["date"]),
        date_max=max(df["date"]),
        battalion_counts=counts,
    )


def habit_label(key: str) -> str:
    """Label panjang sebuah kebiasaan."""
    return HABIT_LABELS.get(key, key)


def attention_labels_text() -> str:
    """Gabungan label 'perlu perhatian' untuk narasi."""
    return " + ".join(ATTENTION_LABELS)


def positive_labels_text() -> str:
    """Gabungan label 'positif' untuk narasi."""
    return " + ".join(POSITIVE_LABELS)
