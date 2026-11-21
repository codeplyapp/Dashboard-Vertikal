"""Taksonomi dan konstanta domain dashboard 7 KAIH.

Modul ini tidak bergantung pada library eksternal agar dapat diimpor di mana pun.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from types import MappingProxyType
from typing import Final

PROJECT_ROOT: Final[Path] = Path(__file__).resolve().parent.parent
DATA_DIR: Final[Path] = PROJECT_ROOT / "data"
RESPONSES_PATH: Final[Path] = DATA_DIR / "responses_anon.json"
META_PATH: Final[Path] = DATA_DIR / "meta.json"

TIMEZONE: Final[str] = "Asia/Jakarta"


@dataclass(frozen=True, slots=True)
class Habit:
    """Satu kebiasaan 7 KAIH beserta pertanyaan instrumennya."""

    key: str
    label: str
    short_label: str
    question: str


HABITS: Final[tuple[Habit, ...]] = (
    Habit(
        key="bangun_pagi",
        label="Bangun Pagi",
        short_label="Bangun Pagi",
        question=(
            "Dalam dua hari terakhir, seberapa sering kamu merasa cukup segar dan siap "
            "mengikuti kegiatan pagi?"
        ),
    ),
    Habit(
        key="ibadah",
        label="Beribadah",
        short_label="Beribadah",
        question=(
            "Dalam dua hari terakhir, seberapa sering kegiatan ibadah berlangsung dengan tertib "
            "dan memberimu kesempatan untuk beribadah dengan khusyuk?"
        ),
    ),
    Habit(
        key="olahraga",
        label="Berolahraga",
        short_label="Berolahraga",
        question=(
            "Dalam dua hari terakhir, seberapa sering kegiatan olahraga memberimu kesempatan "
            "bergerak secara aktif sesuai kemampuanmu?"
        ),
    ),
    Habit(
        key="makan_sehat",
        label="Makan Sehat & Bergizi",
        short_label="Makan Sehat",
        question=(
            "Dalam dua hari terakhir, seberapa sering makanan yang disediakan terasa cukup dan "
            "memiliki variasi yang baik untuk kebutuhanmu?"
        ),
    ),
    Habit(
        key="gemar_belajar",
        label="Gemar Belajar",
        short_label="Gemar Belajar",
        question=(
            "Dalam dua hari terakhir, seberapa sering waktu dan lingkungan belajar membantumu "
            "berkonsentrasi?"
        ),
    ),
    Habit(
        key="bermasyarakat",
        label="Bermasyarakat",
        short_label="Bermasyarakat",
        question=(
            "Dalam dua hari terakhir, seberapa sering kamu merasa dihargai dan dapat bekerja sama "
            "dengan teman di sekolah atau asrama?"
        ),
    ),
    Habit(
        key="tidur_cepat",
        label="Tidur Cepat",
        short_label="Tidur Cepat",
        question=(
            "Dalam dua hari terakhir, seberapa sering waktu tidur yang tersedia membuatmu merasa "
            "cukup beristirahat saat bangun?"
        ),
    ),
)

HABIT_BY_KEY: Final[Mapping[str, Habit]] = MappingProxyType({h.key: h for h in HABITS})
HABIT_KEYS: Final[tuple[str, ...]] = tuple(h.key for h in HABITS)
HABIT_LABELS: Final[Mapping[str, str]] = MappingProxyType({h.key: h.label for h in HABITS})

# Label kolom asli pada sheet "Form Responses 1" (sudah di-strip saat dibaca).
SOURCE_COLUMNS: Final[Mapping[str, str]] = MappingProxyType(
    {
        "bangun_pagi": (
            "Dalam dua hari terakhir, seberapa sering kamu merasa cukup segar dan siap "
            "mengikuti kegiatan pagi?"
        ),
        "ibadah": (
            "Dalam dua hari terakhir, seberapa sering kegiatan ibadah berlangsung dengan tertib "
            "dan memberimu kesempatan untuk beribadah dengan khusyuk?"
        ),
        "olahraga": (
            "Dalam dua hari terakhir, seberapa sering kegiatan olahraga memberimu kesempatan "
            "bergerak secara aktif sesuai kemampuanmu?"
        ),
        "makan_sehat": (
            "Dalam dua hari terakhir, seberapa sering makanan yang disediakan terasa cukup dan "
            "memiliki variasi yang baik untuk kebutuhanmu?"
        ),
        "gemar_belajar": (
            "Dalam dua hari terakhir, seberapa sering waktu dan lingkungan belajar membantumu "
            "berkonsentrasi?"
        ),
        "bermasyarakat": (
            "Dalam dua hari terakhir, seberapa sering kamu merasa dihargai dan dapat bekerja sama "
            "dengan teman di sekolah atau asrama?"
        ),
        "tidur_cepat": (
            "Dalam dua hari terakhir, seberapa sering waktu tidur yang tersedia membuatmu merasa "
            "cukup beristirahat saat bangun?"
        ),
    }
)

SCALE_LABELS: Final[tuple[str, ...]] = (
    "Hampir selalu",
    "Sering",
    "Jarang",
    "Tidak Pernah",
)
SCALE_SCORES: Final[Mapping[str, int]] = MappingProxyType(
    {"Hampir selalu": 4, "Sering": 3, "Jarang": 2, "Tidak Pernah": 1}
)
SCALE_BY_SCORE: Final[Mapping[int, str]] = MappingProxyType(
    {score: label for label, score in SCALE_SCORES.items()}
)
POSITIVE_LABELS: Final[tuple[str, ...]] = ("Hampir selalu", "Sering")
ATTENTION_LABELS: Final[tuple[str, ...]] = ("Jarang", "Tidak Pernah")
POSITIVE_SCORES: Final[frozenset[int]] = frozenset({4, 3})
ATTENTION_SCORES: Final[frozenset[int]] = frozenset({2, 1})
MIN_SCORE: Final[int] = 1
MAX_SCORE: Final[int] = 4


@dataclass(frozen=True, slots=True)
class Battalion:
    """Identitas batalyon (kelompok taruna per tingkat)."""

    code: str
    name: str
    class_label: str
    short_name: str


BATTALIONS: Final[tuple[Battalion, ...]] = (
    Battalion(
        code="X",
        name="Batalyon Bhara Abyakta Radhika",
        class_label="Kelas X",
        short_name="X",
    ),
    Battalion(
        code="XI",
        name="Batalyon Bhara Mada Wiradharma",
        class_label="Kelas XI",
        short_name="XI",
    ),
    Battalion(
        code="XII",
        name="Batalyon Bhara Arsa Nawasena",
        class_label="Kelas XII",
        short_name="XII",
    ),
)

BATTALION_BY_CODE: Final[Mapping[str, Battalion]] = MappingProxyType(
    {b.code: b for b in BATTALIONS}
)
BATTALION_CODE_BY_NAME: Final[Mapping[str, str]] = MappingProxyType(
    {
        alias: b.code
        for b in BATTALIONS
        for alias in (b.name, f"{b.name} ({b.class_label})")
    }
)
BATTALION_CODES: Final[tuple[str, ...]] = tuple(b.code for b in BATTALIONS)


@dataclass(frozen=True, slots=True)
class Wave:
    """Gelombang pengisian formulir."""

    key: str
    label: str
    start: date
    end: date


WAVES: Final[tuple[Wave, ...]] = (
    Wave("G1", "Gelombang 1 · 5 Nov", date(2026, 11, 5), date(2026, 11, 5)),
    Wave("G2", "Gelombang 2 · 8–9 Nov", date(2026, 11, 8), date(2026, 11, 9)),
    Wave("G3", "Gelombang 3 · 11 Nov", date(2026, 11, 11), date(2026, 11, 11)),
    Wave("G4", "Gelombang 4 · 13–14 Nov", date(2026, 11, 13), date(2026, 11, 14)),
)
OTHER_WAVE_KEY: Final[str] = "LAIN"
OTHER_WAVE_LABEL: Final[str] = "Di luar gelombang"


def wave_for(day: date) -> tuple[str, str]:
    """Kembalikan (key, label) gelombang untuk sebuah tanggal."""
    for wave in WAVES:
        if wave.start <= day <= wave.end:
            return wave.key, wave.label
    return OTHER_WAVE_KEY, OTHER_WAVE_LABEL


# Palet visual (dipakai theme.py dan charts.py)
UI_COLORS: Final[Mapping[str, str]] = MappingProxyType(
    {
        "navy": "#0B2545",
        "navy_soft": "#16355C",
        "gold": "#C9A227",
        "gold_soft": "#F2E3B3",
        "surface": "#F4F6F9",
        "ink": "#10233F",
        "muted": "#5B6B82",
        "grid": "#DCE3EC",
        "positive": "#14532D",
        "attention": "#C0392B",
    }
)

SCALE_COLORS: Final[Mapping[str, str]] = MappingProxyType(
    {
        "Hampir selalu": "#14532D",
        "Sering": "#22A06B",
        "Jarang": "#E0A100",
        "Tidak Pernah": "#C0392B",
    }
)

BATTALION_COLORS: Final[Mapping[str, str]] = MappingProxyType(
    {"X": "#0B2545", "XI": "#C9A227", "XII": "#2A7F9E"}
)

QUADRANT_COLORS: Final[Mapping[str, str]] = MappingProxyType(
    {
        "Prioritas Tinggi": "#C0392B",
        "Waspada": "#E0A100",
        "Pantau": "#2A7F9E",
        "Pertahankan": "#14532D",
    }
)

POSITIVE_BENCHMARK: Final[float] = 85.0
ATTENTION_BENCHMARK: Final[float] = 15.0
TARGET_POSITIVE: Final[float] = 90.0
MIN_ENTRIES_FOR_INSIGHT: Final[int] = 10
