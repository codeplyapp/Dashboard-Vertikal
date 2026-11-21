"""Tema visual dan komponen HTML untuk Streamlit."""

from __future__ import annotations

import html
from pathlib import Path

import streamlit as st

from g7kaih.constants import UI_COLORS

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"
STYLES_PATH = ASSETS_DIR / "styles.css"

TONE_COLORS = {
    "positive": UI_COLORS["positive"],
    "attention": UI_COLORS["attention"],
    "neutral": UI_COLORS["muted"],
}


def inject_css() -> None:
    """Sisipkan stylesheet kustom ke halaman Streamlit."""
    css = STYLES_PATH.read_text(encoding="utf-8") if STYLES_PATH.exists() else ""
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def kpi_card(label: str, value: str, caption: str, accent: str | None = None) -> str:
    """HTML satu kartu KPI."""
    color = accent or UI_COLORS["gold"]
    return f"""
    <div class="kpi-card" style="--accent:{html.escape(color)}">
        <div class="kpi-label">{html.escape(label)}</div>
        <div class="kpi-value">{html.escape(value)}</div>
        <div class="kpi-caption">{html.escape(caption)}</div>
    </div>
    """


def section_title(title: str, subtitle: str = "") -> str:
    """HTML judul bagian dengan subjudul opsional."""
    subtitle_html = f'<p class="section-subtitle">{html.escape(subtitle)}</p>' if subtitle else ""
    return f"""
    <div class="section-head">
        <h2>{html.escape(title)}</h2>
        {subtitle_html}
    </div>
    """


def badge(text: str, tone: str = "neutral") -> str:
    """HTML badge kecil berwarna sesuai tone."""
    color = TONE_COLORS.get(tone, UI_COLORS["muted"])
    return (
        f'<span class="badge" style="--badge:{html.escape(color)}">'
        f"{html.escape(text)}</span>"
    )


def insight_card(title: str, detail: str, tone: str = "neutral") -> str:
    """HTML kartu temuan/insight."""
    color = TONE_COLORS.get(tone, UI_COLORS["muted"])
    return f"""
    <div class="insight-card" style="--tone:{html.escape(color)}">
        <div class="insight-title">{html.escape(title)}</div>
        <div class="insight-detail">{html.escape(detail)}</div>
    </div>
    """


def recommendation_card(
    priority: int, title: str, action: str, evidence: str, impact: str
) -> str:
    """HTML kartu rekomendasi tindak lanjut."""
    return f"""
    <div class="rec-card">
        <div class="rec-head">
            <span class="rec-number">{priority:02d}</span>
            <span class="rec-title">{html.escape(title)}</span>
        </div>
        <div class="rec-body">
            <p><span class="rec-label">Aksi</span>{html.escape(action)}</p>
            <p><span class="rec-label">Bukti data</span>{html.escape(evidence)}</p>
            <p><span class="rec-label">Dampak</span>{html.escape(impact)}</p>
        </div>
    </div>
    """
