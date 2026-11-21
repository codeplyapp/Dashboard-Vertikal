"""Bangun dataset anonim dari ekspor Google Forms.

Contoh:
    python scripts/build_data.py
    python scripts/build_data.py --skip-unique
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from g7kaih.constants import (  # noqa: E402
    BATTALION_CODE_BY_NAME,
    BATTALION_CODES,
    DATA_DIR,
    HABITS,
    SCALE_SCORES,
    SOURCE_COLUMNS,
    TIMEZONE,
)

DEFAULT_SOURCE = (
    PROJECT_ROOT.parent
    / "DATA EVALUASI G7KAIH SMAN 2 TARUNA BHAYANGKARA JAWA TIMUR.xlsx"
)
DEFAULT_NIS_SOURCE = (
    PROJECT_ROOT.parent
    / "Evaluasi Pelaksanaan Kualitas G7KAIH - SMAN 2 Taruna Bhayangkara Jawa Timur "
    "(Responses).xlsx"
)
SHEET_NAME = "Form Responses 1"
EXPECTED_TOTAL = 232
EXPECTED_UNIQUE_STUDENTS = 203
EXPECTED_BATTALIONS = {"X": 138, "XI": 47, "XII": 47}
EXPECTED_DISTRIBUTION: dict[str, dict[str, int]] = {
    "bangun_pagi": {"Hampir selalu": 85, "Sering": 117, "Jarang": 29, "Tidak Pernah": 1},
    "ibadah": {"Hampir selalu": 129, "Sering": 86, "Jarang": 16, "Tidak Pernah": 1},
    "olahraga": {"Hampir selalu": 98, "Sering": 114, "Jarang": 19, "Tidak Pernah": 1},
    "makan_sehat": {"Hampir selalu": 83, "Sering": 105, "Jarang": 42, "Tidak Pernah": 2},
    "gemar_belajar": {"Hampir selalu": 62, "Sering": 137, "Jarang": 31, "Tidak Pernah": 2},
    "bermasyarakat": {"Hampir selalu": 96, "Sering": 108, "Jarang": 28, "Tidak Pernah": 0},
    "tidur_cepat": {"Hampir selalu": 82, "Sering": 90, "Jarang": 50, "Tidak Pernah": 10},
}


class BuildError(RuntimeError):
    """Kegagalan validasi saat membangun dataset."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_responses(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise BuildError(f"File sumber tidak ditemukan: {path}")
    frame = pd.read_excel(path, sheet_name=SHEET_NAME)
    frame.columns = [str(column).strip() for column in frame.columns]
    frame = frame.dropna(subset=["Timestamp", "Batalyon"]).reset_index(drop=True)
    if len(frame) != EXPECTED_TOTAL:
        raise BuildError(f"Jumlah baris {len(frame)} != {EXPECTED_TOTAL}")
    if frame.duplicated().any():
        raise BuildError("Terdapat baris duplikat pada sumber.")
    return frame


def normalize_timestamp(series: pd.Series) -> pd.Series:
    if pd.api.types.is_datetime64_any_dtype(series):
        stamps = pd.to_datetime(series)
    else:
        stamps = pd.to_datetime(series, unit="D", origin="1899-12-30")
    stamps = stamps.dt.tz_localize(ZoneInfo(TIMEZONE), ambiguous="raise", nonexistent="raise")
    return stamps


def map_battalion(value: Any) -> str:
    name = str(value).strip()
    code = BATTALION_CODE_BY_NAME.get(name)
    if code is None:
        raise BuildError(f"Nama batalyon tidak dikenal: {name!r}")
    return code


def build_records(frame: pd.DataFrame) -> list[dict[str, Any]]:
    stamps = normalize_timestamp(frame["Timestamp"])
    order = stamps.sort_values().index
    frame = frame.loc[order].reset_index(drop=True)
    stamps = stamps.loc[order].reset_index(drop=True)

    records: list[dict[str, Any]] = []
    for position, row in frame.iterrows():
        answers: dict[str, int] = {}
        for habit in HABITS:
            column = SOURCE_COLUMNS[habit.key]
            if column not in frame.columns:
                raise BuildError(f"Kolom pertanyaan tidak ditemukan: {column!r}")
            label = str(row[column]).strip()
            if label not in SCALE_SCORES:
                raise BuildError(f"Jawaban tidak dikenal pada {habit.key}: {label!r}")
            answers[habit.key] = SCALE_SCORES[label]
        records.append(
            {
                "entry_id": position + 1,
                "timestamp": stamps.iloc[position].isoformat(timespec="seconds"),
                "battalion": map_battalion(row["Batalyon"]),
                "answers": answers,
            }
        )
    return records


def validate_records(records: list[dict[str, Any]]) -> None:
    if len(records) != EXPECTED_TOTAL:
        raise BuildError(f"Jumlah record {len(records)} != {EXPECTED_TOTAL}")
    battalion_counts = {code: 0 for code in BATTALION_CODES}
    for record in records:
        battalion_counts[record["battalion"]] += 1
    if battalion_counts != EXPECTED_BATTALIONS:
        raise BuildError(f"Sebaran batalyon {battalion_counts} != {EXPECTED_BATTALIONS}")

    from collections import Counter

    for key, expected in EXPECTED_DISTRIBUTION.items():
        labels = [SCALE_SCORES_REVERSE[record["answers"][key]] for record in records]
        counts = Counter(labels)
        actual = {label: counts.get(label, 0) for label in expected}
        if actual != expected:
            raise BuildError(f"Distribusi {key} {actual} != {expected}")


SCALE_SCORES_REVERSE = {score: label for label, score in SCALE_SCORES.items()}


def count_unique_students(path: Path) -> int:
    if not path.exists():
        raise BuildError(
            f"File berkode tidak ditemukan: {path}. Gunakan --skip-unique untuk melewati."
        )
    frame = pd.read_excel(path, sheet_name=SHEET_NAME)
    frame.columns = [str(column).strip() for column in frame.columns]
    code_column = next(
        (column for column in frame.columns if column.lower().startswith("kode responden")),
        None,
    )
    if code_column is None:
        raise BuildError("Kolom 'Kode Responden (NIS)' tidak ditemukan.")

    def normalize(value: Any) -> str:
        text = str(value).strip()
        if text.endswith(".0") and text[:-2].isdigit():
            text = text[:-2]
        return text

    codes = {normalize(value) for value in frame[code_column].dropna() if normalize(value)}
    if len(codes) != EXPECTED_UNIQUE_STUDENTS:
        raise BuildError(
            f"Jumlah siswa unik {len(codes)} != {EXPECTED_UNIQUE_STUDENTS}"
        )
    return len(codes)


def main() -> int:
    parser = argparse.ArgumentParser(description="Bangun dataset anonim 7 KAIH.")
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--nis-source", type=Path, default=DEFAULT_NIS_SOURCE)
    parser.add_argument(
        "--skip-unique",
        action="store_true",
        help="Lewati penghitungan siswa unik (meta.unique_students = null).",
    )
    parser.add_argument("--output-dir", type=Path, default=DATA_DIR)
    args = parser.parse_args()

    frame = read_responses(args.source)
    records = build_records(frame)
    validate_records(records)

    unique_students = None if args.skip_unique else count_unique_students(args.nis_source)

    stamps = pd.to_datetime([record["timestamp"] for record in records], utc=True)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    responses_path = args.output_dir / "responses_anon.json"
    meta_path = args.output_dir / "meta.json"

    responses_path.write_text(
        json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    meta = {
        "schema_version": 1,
        "total_entries": len(records),
        "unique_students": unique_students,
        "date_min": stamps.min().date().isoformat(),
        "date_max": stamps.max().date().isoformat(),
        "battalion_counts": EXPECTED_BATTALIONS,
        "source_file": args.source.name,
        "source_sha256": sha256_file(args.source),
        "generated_at": datetime.now(ZoneInfo(TIMEZONE)).isoformat(timespec="seconds"),
    }
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print("Dataset berhasil dibangun.")
    print(f"  Entri          : {meta['total_entries']}")
    print(f"  Siswa unik     : {meta['unique_students']}")
    print(f"  Rentang tanggal: {meta['date_min']} s.d. {meta['date_max']}")
    print(f"  Batalyon       : {meta['battalion_counts']}")
    print(f"  Output         : {responses_path} & {meta_path}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BuildError as error:
        print(f"GAGAL: {error}", file=sys.stderr)
        raise SystemExit(1) from error
