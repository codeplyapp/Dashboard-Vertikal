"""Generator temuan dan rekomendasi berbasis data.

Narasi selalu diturunkan dari DataFrame terfilter; tidak ada angka yang
ditulis manual di dalam teks.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

import pandas as pd

from g7kaih import analytics
from g7kaih.constants import (
    ATTENTION_BENCHMARK,
    BATTALION_BY_CODE,
    MIN_ENTRIES_FOR_INSIGHT,
)
from g7kaih.formatting import date_id, pct, ratio

Tone = Literal["positive", "attention", "neutral"]


@dataclass(frozen=True, slots=True)
class Insight:
    """Satu temuan yang siap ditampilkan."""

    title: str
    detail: str
    tone: Tone


@dataclass(frozen=True, slots=True)
class Recommendation:
    """Rekomendasi tindak lanjut dengan bukti kuantitatif."""

    priority: int
    title: str
    action: str
    evidence: str
    impact: str


HABIT_ACTIONS: dict[str, tuple[str, str]] = {
    "bangun_pagi": (
        "Tinjau ulang jam mulai kegiatan pagi dan kepastian waktu istirahat malam agar taruna "
        "benar-benar siap mengikuti agenda pagi.",
        "Meningkatkan proporsi taruna yang merasa segar saat kegiatan pagi pada pemantauan "
        "berikutnya.",
    ),
    "ibadah": (
        "Pertahankan ketertiban jadwal dan pendampingan ibadah; jadikan praktik baik batalyon "
        "terbaik sebagai contoh antar-batalyon.",
        "Menjaga proporsi respons positif tetap di atas target sekolah.",
    ),
    "olahraga": (
        "Jaga variasi aktivitas fisik dan sesuaikan intensitas dengan kemampuan taruna agar semua "
        "bisa bergerak aktif.",
        "Mempertahankan keterlibatan taruna dalam aktivitas fisik harian.",
    ),
    "makan_sehat": (
        "Sampaikan temuan ini kepada pengelola konsumsi untuk mengevaluasi variasi menu, ukuran "
        "porsi, dan jadwal makan.",
        "Meningkatkan kepuasan taruna terhadap kecukupan dan variasi makanan.",
    ),
    "gemar_belajar": (
        "Optimalkan kondusivitas jam wajib belajar malam: pengaturan ruang, pengawasan, dan "
        "pengurangan gangguan.",
        "Meningkatkan kualitas konsentrasi taruna pada waktu belajar.",
    ),
    "bermasyarakat": (
        "Perkuat kegiatan kekompakan dan pendampingan sebaya, khususnya pada batalyon dengan "
        "respons kerja sama terendah.",
        "Meningkatkan rasa dihargai dan kualitas kerja sama antar-taruna.",
    ),
    "tidur_cepat": (
        "Evaluasi jadwal kegiatan malam dan waktu mulai istirahat agar durasi tidur taruna cukup "
        "sebelum kegiatan pagi.",
        "Menurunkan proporsi taruna yang merasa kurang beristirahat saat bangun.",
    ),
}


def _empty_insight() -> Insight:
    return Insight(
        title="Tidak ada data pada filter ini",
        detail=(
            "Kombinasi batalyon, tanggal, dan kebiasaan yang dipilih tidak menghasilkan entri. "
            "Ubah filter atau kembalikan ke pengaturan awal."
        ),
        tone="neutral",
    )


def build_insights(df: pd.DataFrame, meta: dict[str, Any] | None = None) -> list[Insight]:
    """Susun temuan utama dari data terfilter."""
    if df.empty:
        return [_empty_insight()]

    summary = analytics.summary_table(df)
    total = len(df)
    top = summary.loc[summary["positive_pct"].idxmax()]
    priority = summary.loc[summary["attention_pct"].idxmax()]
    insights: list[Insight] = []

    insights.append(
        Insight(
            title=f"Kekuatan utama: {top['habit']}",
            detail=(
                f"{ratio(int(top['positive']), total)} entri menjawab Hampir selalu atau Sering. "
                f"Kebiasaan ini menjadi modal budaya sekolah yang perlu dijaga."
            ),
            tone="positive",
        )
    )

    insights.append(
        Insight(
            title=f"Prioritas pembinaan: {priority['habit']}",
            detail=(
                f"{ratio(int(priority['attention']), total)} entri menjawab Jarang atau Tidak "
                f"Pernah. Ini adalah proporsi 'perlu perhatian' tertinggi dari tujuh kebiasaan."
            ),
            tone="attention",
        )
    )

    per_battalion = analytics.attention_by_battalion(df, str(priority["habit_key"]))
    if len(per_battalion) >= 2:
        highest = per_battalion.loc[per_battalion["attention_pct"].idxmax()]
        lowest = per_battalion.loc[per_battalion["attention_pct"].idxmin()]
        gap = float(highest["attention_pct"]) - float(lowest["attention_pct"])
        if gap >= 1:
            high_battalion = BATTALION_BY_CODE[str(highest["battalion"])]
            low_battalion = BATTALION_BY_CODE[str(lowest["battalion"])]
            insights.append(
                Insight(
                    title="Kesenjangan antar-batalyon",
                    detail=(
                        f"Pada {priority['habit']}, {high_battalion.class_label} mencatat "
                        f"{pct(float(highest['attention_pct']))} perlu perhatian, sedangkan "
                        f"{low_battalion.class_label} {pct(float(lowest['attention_pct']))} "
                        f"(selisih {pct(gap)} poin)."
                    ),
                    tone="attention",
                )
            )

    if meta:
        unique = meta.get("unique_students")
        coverage = (
            f"{total} entri dari {unique} siswa unik"
            if unique
            else f"{total} entri"
        )
        insights.append(
            Insight(
                title="Cakupan pengukuran",
                detail=(
                    f"Data terfilter mencakup {coverage}, rentang "
                    f"{date_id(min(df['date']))}–{date_id(max(df['date']))}. Satuan analisis "
                    "adalah entri karena formulir tidak memuat ID unik per siswa."
                ),
                tone="neutral",
            )
        )

    if total < MIN_ENTRIES_FOR_INSIGHT:
        insights.append(
            Insight(
                title="Sampel terbatas",
                detail=(
                    f"Filter menyisakan {total} entri. Persentase pada kelompok sekecil ini "
                    "perlu dibaca sebagai indikasi awal, bukan kesimpulan final."
                ),
                tone="attention",
            )
        )

    return insights


def build_recommendations(df: pd.DataFrame) -> list[Recommendation]:
    """Buat maksimal tiga rekomendasi prioritas dari kebiasaan berkinerja terendah."""
    if df.empty:
        return []
    summary = analytics.summary_table(df)
    total = len(df)
    ordered = summary.sort_values(
        ["attention_pct", "positive_pct"], ascending=[False, True]
    ).head(3)
    recommendations: list[Recommendation] = []
    for rank, (_, row) in enumerate(ordered.iterrows(), start=1):
        key = str(row["habit_key"])
        action, impact = HABIT_ACTIONS.get(
            key,
            (
                "Tindak lanjuti temuan ini bersama guru pendamping dan pengelola asrama.",
                "Perbaikan kondisi kebiasaan pada pemantauan berikutnya.",
            ),
        )
        attention_pct = float(row["attention_pct"])
        recommendations.append(
            Recommendation(
                priority=rank,
                title=f"Prioritas {rank}: {row['habit']}",
                action=action,
                evidence=(
                    f"{ratio(int(row['attention']), total)} entri menjawab Jarang atau Tidak "
                    f"Pernah; indeks kebiasaan {float(row['index']):.0f}/100."
                ),
                impact=impact
                if attention_pct >= ATTENTION_BENCHMARK
                else impact + " Pantau agar tidak melewati ambang 15%.",
            )
        )
    return recommendations
