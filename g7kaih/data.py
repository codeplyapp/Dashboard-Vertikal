"""Lapisan akses data: memuat, memvalidasi, dan memfilter dataset 7 KAIH."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

import pandas as pd

from g7kaih.constants import (
    BATTALION_BY_CODE,
    BATTALION_CODES,
    HABIT_KEYS,
    MAX_SCORE,
    META_PATH,
    MIN_SCORE,
    RESPONSES_PATH,
    TIMEZONE,
)

REQUIRED_META_KEYS: tuple[str, ...] = (
    "schema_version",
    "total_entries",
    "unique_students",
    "date_min",
    "date_max",
    "battalion_counts",
)
REQUIRED_COLUMNS: tuple[str, ...] = (
    "entry_id",
    "timestamp",
    "date",
    "battalion",
    "total_score",
    "index",
    *HABIT_KEYS,
)


class DataValidationError(ValueError):
    """Dataset tidak memenuhi skema yang diharapkan."""


@dataclass(frozen=True, slots=True)
class Filters:
    """Filter global dashboard. Nilai kosong berarti 'semua'."""

    battalions: tuple[str, ...] = ()
    start: date | None = None
    end: date | None = None
    habit: str | None = None


def load_meta(path: Path | None = None) -> dict[str, Any]:
    """Muat metadata dataset dan validasi kunci wajibnya."""
    meta_path = Path(path) if path is not None else META_PATH
    if not meta_path.exists():
        raise FileNotFoundError(
            f"Metadata tidak ditemukan: {meta_path}. Jalankan `python scripts/build_data.py`."
        )
    meta: dict[str, Any] = json.loads(meta_path.read_text(encoding="utf-8"))
    missing = [key for key in REQUIRED_META_KEYS if key not in meta]
    if missing:
        raise DataValidationError(f"Metadata kehilangan kunci: {', '.join(missing)}")
    return meta


def load_dataset(path: Path | None = None) -> pd.DataFrame:
    """Muat dataset anonim menjadi DataFrame tervalidasi.

    Kolom jawaban dinormalisasi menjadi skor ordinal 1-4.
    """
    data_path = Path(path) if path is not None else RESPONSES_PATH
    if not data_path.exists():
        raise FileNotFoundError(
            f"Dataset tidak ditemukan: {data_path}. Jalankan `python scripts/build_data.py`."
        )

    records: Any = json.loads(data_path.read_text(encoding="utf-8"))
    if not isinstance(records, list) or not records:
        raise DataValidationError("Dataset harus berupa array JSON yang tidak kosong.")

    rows: list[dict[str, Any]] = []
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            raise DataValidationError(f"Record ke-{index} bukan objek JSON.")
        answers = record.get("answers")
        if not isinstance(answers, dict):
            raise DataValidationError(f"Record ke-{index} tidak memiliki objek 'answers'.")
        missing = [key for key in HABIT_KEYS if key not in answers]
        if missing:
            raise DataValidationError(
                f"Record ke-{index} kehilangan jawaban: {', '.join(missing)}"
            )
        row: dict[str, Any] = {
            "entry_id": record.get("entry_id"),
            "timestamp": record.get("timestamp"),
            "battalion": record.get("battalion"),
        }
        row.update({key: answers[key] for key in HABIT_KEYS})
        rows.append(row)

    df = pd.DataFrame(rows)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, format="ISO8601").dt.tz_convert(
        TIMEZONE
    )
    df["date"] = df["timestamp"].dt.date
    df["battalion"] = pd.Categorical(df["battalion"], categories=list(BATTALION_CODES))
    for key in HABIT_KEYS:
        df[key] = pd.to_numeric(df[key], errors="coerce").astype("int8")
    df["entry_id"] = pd.to_numeric(df["entry_id"], errors="coerce").astype("int64")
    df["total_score"] = df[list(HABIT_KEYS)].sum(axis=1).astype("int16")
    df["index"] = (df["total_score"] - len(HABIT_KEYS) * MIN_SCORE) / (
        len(HABIT_KEYS) * (MAX_SCORE - MIN_SCORE)
    ) * 100
    df["index"] = df["index"].astype("float64")

    validate_dataset(df)
    return df.sort_values(["timestamp", "entry_id"]).reset_index(drop=True)


def validate_dataset(df: pd.DataFrame) -> None:
    """Validasi skema, kelengkapan, dan domain nilai. Melempar DataValidationError."""
    missing = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing:
        raise DataValidationError(f"Kolom wajib tidak ada: {', '.join(missing)}")
    if df.empty:
        raise DataValidationError("Dataset kosong.")
    if df["entry_id"].duplicated().any():
        raise DataValidationError("entry_id harus unik.")
    if df[list(REQUIRED_COLUMNS)].isna().any().any():
        raise DataValidationError("Dataset mengandung nilai kosong pada kolom wajib.")
    invalid_battalions = set(df["battalion"].astype(str)) - set(BATTALION_CODES)
    if invalid_battalions:
        raise DataValidationError(f"Batalyon tidak dikenal: {sorted(invalid_battalions)}")
    for key in HABIT_KEYS:
        values = df[key]
        if values.min() < MIN_SCORE or values.max() > MAX_SCORE:
            raise DataValidationError(f"Skor '{key}' harus berada pada rentang 1-4.")


def apply_filters(df: pd.DataFrame, filters: Filters) -> pd.DataFrame:
    """Terapkan filter global tanpa memutasi DataFrame masukan."""
    result = df
    if filters.battalions:
        unknown = set(filters.battalions) - set(BATTALION_CODES)
        if unknown:
            raise DataValidationError(f"Filter batalyon tidak dikenal: {sorted(unknown)}")
        result = result[result["battalion"].astype(str).isin(filters.battalions)]
    if filters.start is not None:
        result = result[result["date"] >= filters.start]
    if filters.end is not None:
        result = result[result["date"] <= filters.end]
    if filters.habit is not None and filters.habit not in HABIT_KEYS:
        raise DataValidationError(f"Kebiasaan tidak dikenal: {filters.habit}")
    return result.reset_index(drop=True)


def battalion_label(codes: tuple[str, ...] | list[str]) -> str:
    """Label ringkas untuk sekumpulan kode batalyon."""
    if not codes:
        return "Semua batalyon"
    ordered = [code for code in BATTALION_CODES if code in set(codes)]
    if len(ordered) == 1:
        battalion = BATTALION_BY_CODE[ordered[0]]
        return f"{battalion.name} ({battalion.class_label})"
    return "Batalyon " + ", ".join(ordered)


def active_filter_label(df: pd.DataFrame, filters: Filters) -> str:
    """Ringkasan filter aktif untuk ditampilkan di UI."""
    if df.empty:
        return "Tidak ada entri pada filter ini"
    start = min(df["date"])
    end = max(df["date"])
    period = (
        f"{start.day} {start.strftime('%b')} – {end.day} {end.strftime('%b')} {end.year}"
        if start != end
        else f"{start.day} {start.strftime('%b')} {start.year}"
    )
    return f"{len(df)} entri · {battalion_label(list(filters.battalions))} · {period}"
