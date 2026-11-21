"""Dashboard Pemantauan 7 Kebiasaan Anak Indonesia Hebat.

Entry point Streamlit. Seluruh angka dihitung ulang dari `data/responses_anon.json`
melalui fungsi murni di package `g7kaih`.
"""

from __future__ import annotations

import logging
from datetime import date
from typing import Any

import pandas as pd
import streamlit as st

from g7kaih import analytics, charts, theme
from g7kaih.constants import (
    ATTENTION_BENCHMARK,
    BATTALION_BY_CODE,
    BATTALION_CODES,
    HABIT_BY_KEY,
    HABIT_KEYS,
    HABIT_LABELS,
    HABITS,
    META_PATH,
    POSITIVE_BENCHMARK,
    RESPONSES_PATH,
    TARGET_POSITIVE,
    UI_COLORS,
)
from g7kaih.data import (
    DataValidationError,
    Filters,
    active_filter_label,
    apply_filters,
    load_dataset,
    load_meta,
)
from g7kaih.formatting import date_id, num, pct
from g7kaih.insights import build_insights, build_recommendations

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
LOGGER = logging.getLogger("g7kaih.app")

st.set_page_config(
    page_title="Dashboard 7 KAIH · SMAN 2 Taruna Bhayangkara Jatim",
    layout="wide",
    initial_sidebar_state="auto",
)


@st.cache_data(show_spinner=False, ttl=3600)
def _load_dataset(path: str, modified: float) -> pd.DataFrame:
    return load_dataset(path)


@st.cache_data(show_spinner=False, ttl=3600)
def _load_meta(path: str, modified: float) -> dict[str, Any]:
    return load_meta(path)


def _load() -> tuple[pd.DataFrame, dict[str, Any]]:
    try:
        dataset_modified = META_PATH.stat().st_mtime if META_PATH.exists() else 0.0
        responses_modified = (
            RESPONSES_PATH.stat().st_mtime if RESPONSES_PATH.exists() else 0.0
        )
        data = _load_dataset(str(RESPONSES_PATH), responses_modified)
        metadata = _load_meta(str(META_PATH), dataset_modified)
    except (FileNotFoundError, DataValidationError) as error:
        st.error(f"Dataset belum siap: {error}")
        st.code("python scripts/build_data.py", language="bash")
        st.stop()
    except Exception:  # noqa: BLE001 - boundary UI
        LOGGER.exception("Gagal memuat dataset")
        st.error("Terjadi kesalahan tak terduga saat memuat data. Periksa log server.")
        st.stop()
    return data, metadata


def _reset_filters(min_date: date, max_date: date) -> None:
    st.session_state["battalion_filter"] = list(BATTALION_CODES)
    st.session_state["date_filter"] = (min_date, max_date)
    st.session_state["habit_filter"] = "all"


def _focus_summary(summary: pd.DataFrame, focus: str | None) -> pd.DataFrame:
    if not focus or focus == "all":
        return summary
    mask = summary["habit_key"] == focus
    return pd.concat([summary[mask], summary[~mask]]).reset_index(drop=True)


def _plot(figure: Any, key: str) -> None:
    st.plotly_chart(
        figure,
        width="stretch",
        theme=None,
        config={"displayModeBar": False},
        key=key,
    )


def _format_index(value: float) -> str:
    return f"{value:.1f}".replace(".", ",")


def _kpi_row(
    snapshot: analytics.KpiSnapshot,
    metadata: dict[str, Any],
    dates: int,
) -> None:
    unique = metadata.get("unique_students")
    dataset_total = int(metadata.get("total_entries", snapshot.total_entries))
    if snapshot.total_entries == dataset_total:
        coverage = (
            f"{unique} siswa unik · {dates} tanggal pengisian"
            if unique
            else f"{dates} tanggal pengisian"
        )
    else:
        coverage = f"Bagian dari {num(dataset_total)} entri · {dates} tanggal"
    columns = st.columns(4, gap="small")
    cards = [
        (
            "Total entri terfilter",
            num(snapshot.total_entries),
            coverage,
            UI_COLORS["navy"],
        ),
        (
            "Indeks 7KAIH",
            _format_index(snapshot.overall_index),
            "Skala 0–100 · target 90",
            UI_COLORS["gold"],
        ),
        (
            "Kekuatan utama",
            snapshot.top_habit,
            f"{pct(snapshot.top_positive_pct)} respons positif",
            UI_COLORS["positive"],
        ),
        (
            "Prioritas pembinaan",
            snapshot.priority_habit,
            f"{pct(snapshot.priority_attention_pct)} perlu perhatian",
            UI_COLORS["attention"],
        ),
    ]
    for column, (label, value, caption, accent) in zip(columns, cards, strict=True):
        with column:
            st.markdown(
                theme.kpi_card(label, value, caption, accent), unsafe_allow_html=True
            )


def _sidebar(data: pd.DataFrame, metadata: dict[str, Any]) -> tuple[Filters, str]:
    min_date = min(data["date"])
    max_date = max(data["date"])
    if "battalion_filter" not in st.session_state:
        st.session_state["battalion_filter"] = list(BATTALION_CODES)
    if "date_filter" not in st.session_state:
        st.session_state["date_filter"] = (min_date, max_date)
    if "habit_filter" not in st.session_state:
        st.session_state["habit_filter"] = "all"

    with st.sidebar:
        st.markdown('<div class="sidebar-title">Filter Dashboard</div>', unsafe_allow_html=True)
        selected = st.multiselect(
            "Batalyon",
            options=list(BATTALION_CODES),
            format_func=lambda code: f"Kelas {code} · {BATTALION_BY_CODE[code].name}",
            key="battalion_filter",
        )
        if not selected:
            st.warning("Tidak ada batalyon dipilih. Menampilkan semua batalyon.")
        date_value = st.date_input(
            "Rentang tanggal pengisian",
            min_value=min_date,
            max_value=max_date,
            key="date_filter",
            format="DD/MM/YYYY",
        )
        focus = st.selectbox(
            "Fokus kebiasaan",
            options=["all", *HABIT_KEYS],
            format_func=lambda key: "Semua kebiasaan"
            if key == "all"
            else HABIT_BY_KEY[key].label,
            key="habit_filter",
        )
        st.button(
            "Reset filter",
            on_click=_reset_filters,
            args=(min_date, max_date),
            width="stretch",
        )
        st.markdown(
            f"""
            <div class="sidebar-note">
                <strong>Sumber data</strong><br/>
                {metadata.get('total_entries', len(data))} entri anonim ·
                {metadata.get('unique_students') or '–'} siswa unik<br/>
                {date_id(min_date)} – {date_id(max_date)}<br/>
                SHA-256: <code>{str(metadata.get('source_sha256', ''))[:12]}…</code>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if isinstance(date_value, (tuple, list)):
        start = date_value[0] if len(date_value) > 0 else min_date
        end = date_value[1] if len(date_value) > 1 else max_date
    else:
        start = end = date_value
    battalions: tuple[str, ...] = ()
    if selected and len(selected) < len(BATTALION_CODES):
        battalions = tuple(selected)
    filters = Filters(
        battalions=battalions,
        start=start,
        end=end,
        habit=None if focus == "all" else focus,
    )
    return filters, focus


def _header(data: pd.DataFrame, metadata: dict[str, Any]) -> None:
    unique = metadata.get("unique_students") or "–"
    total = int(metadata.get("total_entries", len(data)))
    dates = int(data["date"].nunique())
    st.markdown(
        f"""
        <div class="hero">
            <div class="hero-kicker">Dashboard Evaluasi · VERTIKAL SMA 2026</div>
            <h1>Pemantauan 7 Kebiasaan Anak Indonesia Hebat</h1>
            <p>SMAN 2 Taruna Bhayangkara Jawa Timur — membaca kondisi, prioritas, dan tindak
            lanjut pembiasaan taruna dari data evaluasi berkala.</p>
            <div class="hero-chips">
                <span class="chip"><strong>{num(total)}</strong> entri</span>
                <span class="chip"><strong>{unique}</strong> siswa unik</span>
                <span class="chip"><strong>{dates}</strong> tanggal pengisian</span>
                <span class="chip"><strong>7</strong> kebiasaan</span>
                <span class="chip"><strong>3</strong> batalyon</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _overview(
    filtered: pd.DataFrame,
    summary: pd.DataFrame,
    snapshot: analytics.KpiSnapshot,
    metadata: dict[str, Any],
    focus: str,
) -> None:
    ordered = _focus_summary(summary, focus)
    st.markdown(
        theme.section_title(
            "Ringkasan kondisi 7 KAIH",
            "Distribusi empat skala jawaban, indeks kebiasaan, dan posisi prioritas.",
        ),
        unsafe_allow_html=True,
    )
    left, right = st.columns([1.65, 1], gap="large")
    with left:
        _plot(charts.stacked_distribution(ordered), "overview_stacked")
        st.caption(
            "Batang = 100% respons per kebiasaan. Arahkan kursor untuk melihat jumlah entri. "
            "Garis putus-putus menandai target respons positif 90%."
        )
    with right:
        _plot(charts.index_gauge(snapshot.overall_index), "overview_gauge")
        top, bottom = analytics.top_and_bottom(filtered)
        st.markdown(
            f"""
            <div class="method-box">
                <strong>Kekuatan:</strong> {top['habit']} —
                {pct(float(top['positive_pct']))} positif<br/>
                <strong>Terendah:</strong> {bottom['habit']} —
                {pct(float(bottom['positive_pct']))} positif<br/>
                <strong>Ambang prioritas:</strong> perlu perhatian ≥
                {pct(ATTENTION_BENCHMARK, 0)}
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.write("")
    left, right = st.columns(2, gap="large")
    with left:
        st.markdown(
            theme.section_title(
                "Profil batalyon",
                "Indeks 7KAIH 0–100; semakin mendekati pusat, semakin baik.",
            ),
            unsafe_allow_html=True,
        )
        _plot(charts.radar_chart(filtered), "overview_radar")
    with right:
        st.markdown(
            theme.section_title(
                "Matriks prioritas",
                f"Kuadran dari ambang positif {pct(POSITIVE_BENCHMARK, 0)} dan perlu perhatian "
                f"{pct(ATTENTION_BENCHMARK, 0)}.",
            ),
            unsafe_allow_html=True,
        )
        _plot(charts.priority_matrix_chart(analytics.priority_matrix(filtered)), "overview_matrix")


def _distribution_tab(filtered: pd.DataFrame, summary: pd.DataFrame, focus: str) -> None:
    st.markdown(
        theme.section_title(
            "Distribusi jawaban per kebiasaan",
            "Proporsi Hampir selalu, Sering, Jarang, dan Tidak Pernah pada data terfilter.",
        ),
        unsafe_allow_html=True,
    )
    ordered = _focus_summary(summary, focus)
    _plot(charts.stacked_distribution(ordered), "distribution_stacked")
    st.write("")
    default_index = HABIT_KEYS.index(focus) if focus in HABIT_KEYS else 0
    selected = st.selectbox(
        "Lihat detail kebiasaan",
        options=list(HABIT_KEYS),
        index=default_index,
        format_func=lambda key: HABIT_BY_KEY[key].label,
        key="habit_detail",
    )
    habit = HABIT_BY_KEY[selected]
    row = summary.set_index("habit_key").loc[selected]
    total = int(row["hs"] + row["s"] + row["j"] + row["tp"])
    st.info(f"**Pertanyaan instrumen:** {habit.question}")
    columns = st.columns(4, gap="small")
    detail = [
        ("Hampir selalu", row["hs"], UI_COLORS["positive"]),
        ("Sering", row["s"], "#22A06B"),
        ("Jarang", row["j"], "#E0A100"),
        ("Tidak Pernah", row["tp"], UI_COLORS["attention"]),
    ]
    for column, (label, count, accent) in zip(columns, detail, strict=True):
        with column:
            st.markdown(
                theme.kpi_card(
                    label,
                    num(int(count)),
                    pct(int(count) / total * 100 if total else 0.0),
                    accent,
                ),
                unsafe_allow_html=True,
            )
    st.caption(
        f"Indeks kebiasaan: {_format_index(float(row['index']))}/100 · "
        f"{pct(float(row['positive_pct']))} respons positif."
    )


def _battalion_tab(filtered: pd.DataFrame, summary: pd.DataFrame) -> None:
    st.markdown(
        theme.section_title(
            "Perbandingan antar-batalyon",
            "Fokus pada persentase respons yang perlu perhatian (Jarang + Tidak Pernah).",
        ),
        unsafe_allow_html=True,
    )
    per_battalion = analytics.battalion_summary(filtered)
    matrix = analytics.battalion_matrix(filtered)
    left, right = st.columns([1, 1], gap="large")
    with left:
        _plot(charts.battalion_heatmap(matrix), "battalion_heatmap")
        st.caption("Warna lebih gelap menunjukkan proporsi perlu perhatian yang lebih tinggi.")
    with right:
        _plot(charts.battalion_grouped(per_battalion), "battalion_grouped")
        st.caption("Setiap kelompok warna mewakili satu batalyon.")
    st.write("")
    st.markdown(theme.section_title("Tabel per batalyon"), unsafe_allow_html=True)
    if per_battalion.empty:
        st.info("Tidak ada data batalyon pada filter ini.")
        return
    pivot = per_battalion.pivot_table(
        index=["battalion", "class_label", "n"],
        columns="habit",
        values="attention_pct",
    )
    pivot = pivot.reindex(columns=[habit.label for habit in HABITS])
    display = pivot.reset_index()
    display["battalion"] = display["battalion"].astype(str)
    display.columns = [
        "Batalyon",
        "Kelas",
        "n",
        *[habit.label for habit in HABITS],
    ]
    for column in [habit.label for habit in HABITS]:
        display[column] = display[column].map(lambda value: pct(float(value), 1))
    st.dataframe(display, hide_index=True, width="stretch")
    st.caption(
        "Nilai = persentase Jarang + Tidak Pernah. Angka absolut tersedia pada tooltip grafik."
    )
    worst = per_battalion.sort_values("attention_pct", ascending=False).iloc[0]
    st.warning(
        f"Perlu perhatian tertinggi: **Kelas {worst['battalion']}** pada "
        f"**{worst['habit']}** sebesar **{pct(float(worst['attention_pct']))}** "
        f"({int(worst['attention'])} dari {int(worst['n'])} entri)."
    )


def _timeline_tab(filtered: pd.DataFrame, snapshot: analytics.KpiSnapshot) -> None:
    st.markdown(
        theme.section_title(
            "Dinamika pengisian",
            "Jumlah entri per tanggal dan empat gelombang utama pengisian pada November 2026.",
        ),
        unsafe_allow_html=True,
    )
    frame = analytics.timeline(filtered)
    _plot(charts.timeline_chart(frame), "timeline")
    st.caption("Batang = entri per tanggal; garis emas = jumlah kumulatif.")
    st.write("")
    waves = analytics.wave_summary(filtered)
    left, right = st.columns([1, 1], gap="large")
    with left:
        st.markdown(theme.section_title("Rekap gelombang"), unsafe_allow_html=True)
        display = waves.copy()
        display["entries"] = display["entries"].map(num)
        display["pct"] = display["pct"].map(lambda value: pct(float(value), 1))
        display.columns = ["Kode", "Gelombang", "Entri", "Proporsi", "Rentang"]
        st.dataframe(display, hide_index=True, width="stretch")
    with right:
        peak = frame.loc[frame["count"].idxmax()]
        st.markdown(
            f"""
            <div class="method-box">
                <strong>Puncak pengisian:</strong> {date_id(peak['date'])} —
                {num(int(peak['count']))} entri ({pct(float(peak['count']) / len(filtered) * 100)}).<br/>
                <strong>Hari aktif:</strong> {len(frame)} tanggal.<br/>
                <strong>Rata-rata per hari aktif:</strong>
                {_format_index(len(filtered) / len(frame))} entri.<br/>
                <strong>Catatan:</strong> tanggal pengisian menunjukkan kapan formulir diisi,
                bukan periode perilaku yang dinilai (instrumen memakai rentang dua hari terakhir).
            </div>
            """,
            unsafe_allow_html=True,
        )


def _table_tab(filtered: pd.DataFrame, summary: pd.DataFrame) -> None:
    st.markdown(
        theme.section_title(
            "Rekapitulasi data asli",
            "Absolut dan persentase dari dataset terfilter; dapat diunduh untuk verifikasi.",
        ),
        unsafe_allow_html=True,
    )
    total = len(filtered)
    display = pd.DataFrame(
        {
            "Kebiasaan": summary["habit"],
            "Hampir selalu": [
                f"{num(int(row.hs))} ({pct(int(row.hs) / total * 100)})"
                for row in summary.itertuples()
            ],
            "Sering": [
                f"{num(int(row.s))} ({pct(int(row.s) / total * 100)})"
                for row in summary.itertuples()
            ],
            "Jarang": [
                f"{num(int(row.j))} ({pct(int(row.j) / total * 100)})"
                for row in summary.itertuples()
            ],
            "Tidak Pernah": [
                f"{num(int(row.tp))} ({pct(int(row.tp) / total * 100)})"
                for row in summary.itertuples()
            ],
            "Positif": [
                f"{num(int(row.positive))} ({pct(float(row.positive_pct), 2)})"
                for row in summary.itertuples()
            ],
            "Perlu perhatian": [
                f"{num(int(row.attention))} ({pct(float(row.attention_pct), 2)})"
                for row in summary.itertuples()
            ],
            "Indeks": [_format_index(float(value)) for value in summary["index"]],
        }
    )
    st.dataframe(display, hide_index=True, width="stretch")
    st.caption(
        f"Total {num(total)} entri. Positif = Hampir selalu + Sering; "
        "perlu perhatian = Jarang + Tidak Pernah."
    )
    export = summary[
        [
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
        ]
    ].rename(
        columns={
            "habit": "kebiasaan",
            "hs": "hampir_selalu",
            "s": "sering",
            "j": "jarang",
            "tp": "tidak_pernah",
            "positive": "positif",
            "positive_pct": "positif_persen",
            "attention": "perlu_perhatian",
            "attention_pct": "perlu_perhatian_persen",
            "mean_score": "rata_rata_skor",
            "index": "indeks",
        }
    )
    st.download_button(
        "Unduh CSV rekapitulasi",
        data=export.to_csv(index=False).encode("utf-8-sig"),
        file_name="rekap_7kaih_terfilter.csv",
        mime="text/csv",
        use_container_width=False,
    )
    with st.expander("Verifikasi integritas angka"):
        st.write(
            {
                "total_entri": int(total),
                "jumlah_kebiasaan": len(summary),
                "total_sel_jawaban": int(
                    summary[["hs", "s", "j", "tp"]].to_numpy().sum()
                ),
                "selisih": int(summary[["hs", "s", "j", "tp"]].to_numpy().sum())
                - int(total) * len(summary),
            }
        )


def _insight_tab(filtered: pd.DataFrame, metadata: dict[str, Any]) -> None:
    st.markdown(
        theme.section_title(
            "Temuan & rencana tindak lanjut",
            "Narasi dihitung dari filter aktif; angka pada setiap temuan dapat dilacak.",
        ),
        unsafe_allow_html=True,
    )
    insights = build_insights(filtered, metadata)
    columns = st.columns(2, gap="large")
    for index, insight in enumerate(insights):
        with columns[index % 2]:
            st.markdown(
                theme.insight_card(insight.title, insight.detail, insight.tone),
                unsafe_allow_html=True,
            )
    st.write("")
    st.markdown(
        theme.section_title(
            "Rekomendasi operasional",
            "Tiga prioritas berdasarkan proporsi perlu perhatian tertinggi.",
        ),
        unsafe_allow_html=True,
    )
    recommendations = build_recommendations(filtered)
    for item in recommendations:
        st.markdown(
            theme.recommendation_card(
                item.priority,
                item.title,
                item.action,
                item.evidence,
                item.impact,
            ),
            unsafe_allow_html=True,
        )
    st.info(
        "Rekomendasi bersifat operasional dan tidak menyimpulkan hubungan sebab-akibat. "
        "Evaluasi lanjutan disarankan memakai periode pengisian berikutnya sebagai pembanding."
    )


def _method_tab(filtered: pd.DataFrame, metadata: dict[str, Any]) -> None:
    st.markdown(
        theme.section_title(
            "Metodologi, kualitas data, dan jejak Gemini",
            "Transparansi pengolahan agar angka dapat diverifikasi ulang.",
        ),
        unsafe_allow_html=True,
    )
    left, right = st.columns([1.15, 1], gap="large")
    with left:
        st.markdown(
            f"""
            <div class="method-box">
                <strong>Sumber data.</strong> Ekspor Google Forms
                <code>{metadata.get('source_file', 'xlsx')}</code>, sheet
                <code>Form Responses 1</code>. Dataset anonim dibangun oleh
                <code>scripts/build_data.py</code> dan divalidasi otomatis.<br/><br/>
                <strong>Satuan analisis.</strong> <code>entri</code>, karena formulir tidak memuat
                ID unik per siswa. Sebanyak {num(metadata.get('total_entries', len(filtered)))}
                entri berasal dari {metadata.get('unique_students') or '–'} siswa unik
                (dihitung terpisah dari kode responden; kode tidak pernah ditampilkan).<br/><br/>
                <strong>Skala.</strong> Hampir selalu = 4, Sering = 3, Jarang = 2,
                Tidak Pernah = 1. Positif = Hampir selalu + Sering; perlu perhatian =
                Jarang + Tidak Pernah.<br/><br/>
                <strong>Indeks 7KAIH.</strong>
                <code>(rata-rata skor − 1) / 3 × 100</code>, sehingga rentang 0–100.<br/><br/>
                <strong>Ambang.</strong> Positif {pct(POSITIVE_BENCHMARK, 0)},
                perlu perhatian {pct(ATTENTION_BENCHMARK, 0)}; target positif
                {pct(TARGET_POSITIVE, 0)} adalah target sekolah, bukan angka data.
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.write("")
        missing = int(filtered.isna().sum().sum())
        duplicates = int(filtered["entry_id"].duplicated().sum())
        st.markdown(
            theme.section_title("Kualitas data terfilter"),
            unsafe_allow_html=True,
        )
        st.write(
            {
                "entri": len(filtered),
                "nilai_kosong": missing,
                "duplikat_id": duplicates,
                "tanggal_awal": str(min(filtered["date"])),
                "tanggal_akhir": str(max(filtered["date"])),
                "sha256_sumber": str(metadata.get("source_sha256", ""))[:16] + "…",
            }
        )
        st.warning(
            "Batasan: data bersifat ordinal dan merupakan persepsi taruna dalam dua hari "
            "terakhir. Perbedaan antarbatalyon tidak otomatis menunjukkan sebab tertentu."
        )
    with right:
        st.markdown(
            theme.section_title(
                "Jejak pemanfaatan Gemini",
                "Empat tahap kerja; tim memverifikasi setiap keluaran.",
            ),
            unsafe_allow_html=True,
        )
        log = pd.DataFrame(
            [
                (
                    1,
                    "Merancang instrumen",
                    "Menyusun tujuh pertanyaan 7 KAIH dengan skala empat titik.",
                    "Tim menyesuaikan konteks sekolah dan memastikan bahasa mudah dipahami.",
                ),
                (
                    2,
                    "Mengumpulkan data",
                    "Membaca ekspor xlsx, memeriksa 232 baris, nilai kosong, dan duplikat.",
                    "Tim menjalankan formulir dan memverifikasi jumlah respons per batalyon.",
                ),
                (
                    3,
                    "Menganalisis data",
                    "Menghitung distribusi, indeks, perbandingan batalyon, dan prioritas.",
                    "Seluruh angka diuji ulang dengan pytest dan tabel referensi.",
                ),
                (
                    4,
                    "Membangun dashboard",
                    "Menyusun struktur Streamlit, grafik Plotly, dan narasi dinamis.",
                    "Tim menguji filter, aksesibilitas, dan konsistensi angka di browser.",
                ),
            ],
            columns=["Tahap", "Aktivitas", "Bantuan Gemini", "Verifikasi tim"],
        )
        st.dataframe(log, hide_index=True, width="stretch")
        with st.expander("Prompt utama yang digunakan"):
            st.code(
                "Buat dashboard interaktif 7 KAIH dari file Excel 232 respons. "
                "Jangan mengubah atau mengarang angka. Sajikan filter batalyon dan tanggal, "
                "KPI cakupan, distribusi empat skala, perbandingan batalyon, tren pengisian, "
                "tabel rekapitulasi, serta temuan dan tindak lanjut.",
                language="text",
            )
        st.caption(
            "Gemini berperan sebagai alat bantu analisis dan pengembangan; keputusan akhir, "
            "verifikasi angka, dan konteks sekolah tetap dilakukan tim."
        )


def main() -> None:
    theme.inject_css()
    data, metadata = _load()
    filters, focus = _sidebar(data, metadata)
    filtered = apply_filters(data, filters)

    if filtered.empty:
        st.warning(
            "Tidak ada entri pada kombinasi filter ini. Silakan ubah batalyon, rentang tanggal, "
            "atau kembalikan ke pengaturan awal."
        )
        st.button(
            "Kembalikan filter awal",
            on_click=_reset_filters,
            args=(min(data["date"]), max(data["date"])),
        )
        st.stop()

    summary = analytics.summary_table(filtered)
    snapshot = analytics.kpi_snapshot(filtered, metadata.get("unique_students"))
    dates = int(filtered["date"].nunique())

    _header(data, metadata)
    st.markdown(
        f"""
        <div class="filter-summary">
            <strong>{active_filter_label(filtered, filters)}</strong>
            {theme.badge("Fokus: " + (HABIT_LABELS[focus] if focus != "all" else "Semua kebiasaan"), "neutral")}
            {theme.badge("Positif " + pct(float(summary["positive"].sum()) / (len(filtered) * len(summary)) * 100), "positive")}
            {theme.badge("Perlu perhatian " + pct(float(summary["attention"].sum()) / (len(filtered) * len(summary)) * 100), "attention")}
        </div>
        """,
        unsafe_allow_html=True,
    )
    _kpi_row(snapshot, metadata, dates)
    st.write("")

    tabs = st.tabs(
        [
            "Ringkasan",
            "Distribusi 7 KAIH",
            "Per Batalyon",
            "Tren Waktu",
            "Tabel Data",
            "Insight & Aksi",
            "Metodologi & Gemini",
        ]
    )
    with tabs[0]:
        _overview(filtered, summary, snapshot, metadata, focus)
    with tabs[1]:
        _distribution_tab(filtered, summary, focus)
    with tabs[2]:
        _battalion_tab(filtered, summary)
    with tabs[3]:
        _timeline_tab(filtered, snapshot)
    with tabs[4]:
        _table_tab(filtered, summary)
    with tabs[5]:
        _insight_tab(filtered, metadata)
    with tabs[6]:
        _method_tab(filtered, metadata)

    st.markdown(
        f"""
        <div class="note" style="margin-top:24px;border-top:1px solid {UI_COLORS['grid']};padding-top:12px">
            Dashboard 7 KAIH · SMAN 2 Taruna Bhayangkara Jawa Timur
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
