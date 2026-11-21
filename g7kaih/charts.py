"""Factory grafik Plotly dengan tema konsisten."""

from __future__ import annotations

import math

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from g7kaih import analytics
from g7kaih.constants import (
    ATTENTION_BENCHMARK,
    BATTALION_BY_CODE,
    BATTALION_COLORS,
    HABITS,
    OTHER_WAVE_KEY,
    POSITIVE_BENCHMARK,
    QUADRANT_COLORS,
    SCALE_COLORS,
    SCALE_LABELS,
    UI_COLORS,
)
from g7kaih.formatting import date_id, num, pct

FONT_FAMILY = '"Segoe UI", "Inter", system-ui, sans-serif'
WAVE_COLORS = {
    "G1": "#0B2545",
    "G2": "#2A7F9E",
    "G3": "#C9A227",
    "G4": "#14532D",
    OTHER_WAVE_KEY: "#9AA8B8",
}


def apply_theme(fig: go.Figure, *, height: int = 380, show_legend: bool = False) -> go.Figure:
    """Terapkan tema visual dan format angka Indonesia."""
    fig.update_layout(
        height=height,
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(family=FONT_FAMILY, size=12, color=UI_COLORS["ink"]),
        margin=dict(l=10, r=10, t=30, b=10),
        separators=",.",
        hoverlabel=dict(
            bgcolor="white",
            bordercolor=UI_COLORS["grid"],
            font=dict(family=FONT_FAMILY, size=12, color=UI_COLORS["ink"]),
        ),
        showlegend=show_legend,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            x=0,
            bgcolor="rgba(0,0,0,0)",
            font=dict(size=11),
        ),
    )
    fig.update_xaxes(
        showgrid=True,
        gridcolor=UI_COLORS["grid"],
        zeroline=False,
        linecolor=UI_COLORS["grid"],
        tickfont=dict(size=11, color=UI_COLORS["muted"]),
        automargin=True,
    )
    fig.update_yaxes(
        showgrid=False,
        zeroline=False,
        linecolor=UI_COLORS["grid"],
        tickfont=dict(size=11, color=UI_COLORS["muted"]),
        automargin=True,
    )
    return fig


def stacked_distribution(summary: pd.DataFrame) -> go.Figure:
    """Bar horizontal 100% untuk distribusi empat skala jawaban."""
    fig = go.Figure()
    if summary.empty:
        return apply_theme(fig)
    data = summary.iloc[::-1]
    columns = {
        "Hampir selalu": ("hs", "positive"),
        "Sering": ("s", "positive"),
        "Jarang": ("j", "attention"),
        "Tidak Pernah": ("tp", "attention"),
    }
    total = int(data[["hs", "s", "j", "tp"]].to_numpy().sum())
    for label in SCALE_LABELS:
        count_col, _ = columns[label]
        counts = data[count_col].astype(int)
        pcts = counts / total * 100 if total else counts * 0
        text = [pct(value, 1) if value >= 6 else "" for value in pcts]
        text_color = UI_COLORS["ink"] if label == "Jarang" else "#ffffff"
        fig.add_trace(
            go.Bar(
                y=data["habit"],
                x=pcts,
                name=label,
                orientation="h",
                marker=dict(color=SCALE_COLORS[label], line=dict(width=0)),
                customdata=counts,
                text=text,
                textposition="inside",
                insidetextanchor="middle",
                textfont=dict(size=10, color=text_color),
                hovertemplate=(
                    "%{y}<br>" + label + ": %{customdata} entri (%{x:.1f}%)<extra></extra>"
                ),
            )
        )
    fig.update_layout(barmode="stack", bargap=0.28)
    fig.update_xaxes(range=[0, 100], ticksuffix="%", title=None)
    fig.update_yaxes(autorange="reversed", tickfont=dict(size=11, color=UI_COLORS["ink"]))
    fig.add_vline(x=90, line=dict(color=UI_COLORS["gold"], width=1, dash="dot"))
    fig.add_annotation(
        x=90,
        y=1.02,
        yref="paper",
        text="target positif 90%",
        showarrow=False,
        font=dict(size=10, color=UI_COLORS["muted"]),
        xanchor="right",
    )
    return apply_theme(fig, height=430, show_legend=True)


def battalion_heatmap(matrix: pd.DataFrame) -> go.Figure:
    """Heatmap persentase perlu perhatian per batalyon x kebiasaan."""
    fig = go.Figure()
    if matrix.empty:
        return apply_theme(fig)
    z = matrix.to_numpy(dtype=float)
    text = [[pct(value, 1) for value in row] for row in z]
    y_labels = [
        f"{code} · {BATTALION_BY_CODE[code].class_label}" for code in matrix.index
    ]
    zmax = max(20.0, math.ceil(float(z[~pd.isna(z)].max()) / 5) * 5) if z.size else 20.0
    fig.add_trace(
        go.Heatmap(
            z=z,
            x=list(matrix.columns),
            y=y_labels,
            text=text,
            texttemplate="%{text}",
            textfont=dict(size=11),
            colorscale=[
                [0.0, "#F4F6F9"],
                [0.35, "#F6D58B"],
                [0.7, "#E08E45"],
                [1.0, "#A93226"],
            ],
            zmin=0,
            zmax=zmax,
            xgap=3,
            ygap=3,
            colorbar=dict(thickness=10, len=0.85, title=dict(text="%", side="right")),
            hovertemplate="%{y}<br>%{x}: %{z:.1f}%<extra></extra>",
        )
    )
    fig.update_xaxes(tickangle=-18, showgrid=False)
    fig.update_yaxes(showgrid=False)
    return apply_theme(fig, height=300)


def battalion_grouped(summary: pd.DataFrame) -> go.Figure:
    """Bar berkelompok persentase perlu perhatian per batalyon."""
    fig = go.Figure()
    if summary.empty:
        return apply_theme(fig)
    habits = [habit.label for habit in HABITS]
    for code in [b for b in BATTALION_COLORS if b in set(summary["battalion"])]:
        subset = summary[summary["battalion"] == code]
        subset = subset.set_index("habit").reindex(habits)
        fig.add_trace(
            go.Bar(
                x=habits,
                y=subset["attention_pct"],
                name=f"Kelas {code}",
                marker=dict(color=BATTALION_COLORS[code]),
                customdata=subset["attention"].fillna(0).astype(int),
                text=[pct(value, 1) for value in subset["attention_pct"]],
                textposition="outside",
                textfont=dict(size=9, color=UI_COLORS["muted"]),
                hovertemplate=(
                    "%{x}<br>Kelas " + code + ": %{y:.1f}% (%{customdata} entri)"
                    "<extra></extra>"
                ),
            )
        )
    fig.update_layout(barmode="group", bargap=0.22, bargroupgap=0.08)
    fig.update_xaxes(tickangle=-18, showgrid=False)
    fig.update_yaxes(ticksuffix="%", range=[0, 55], showgrid=True)
    return apply_theme(fig, height=380, show_legend=True)


def timeline_chart(frame: pd.DataFrame) -> go.Figure:
    """Combo bar jumlah entri per tanggal + garis kumulatif."""
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    if frame.empty:
        return apply_theme(fig)
    labels = [date_id(value) for value in frame["date"]]
    colors = [WAVE_COLORS.get(key, WAVE_COLORS[OTHER_WAVE_KEY]) for key in frame["wave_key"]]
    fig.add_trace(
        go.Bar(
            x=labels,
            y=frame["count"],
            name="Entri per tanggal",
            marker=dict(color=colors),
            customdata=frame["wave_label"],
            text=frame["count"],
            textposition="outside",
            textfont=dict(size=10, color=UI_COLORS["muted"]),
            hovertemplate=(
                "%{x}<br>%{y} entri<br>%{customdata}<extra></extra>"
            ),
        ),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(
            x=labels,
            y=frame["cumulative"],
            name="Kumulatif",
            mode="lines+markers",
            line=dict(color=UI_COLORS["gold"], width=3),
            marker=dict(size=7, color=UI_COLORS["gold"]),
            hovertemplate="Kumulatif s.d. %{x}: %{y} entri<extra></extra>",
        ),
        secondary_y=True,
    )
    peak = frame.loc[frame["count"].idxmax()]
    fig.add_annotation(
        x=date_id(peak["date"]),
        y=int(peak["count"]),
        text=f"Puncak: {num(int(peak['count']))} entri",
        showarrow=True,
        arrowhead=2,
        arrowcolor=UI_COLORS["muted"],
        ax=0,
        ay=-32,
        font=dict(size=10, color=UI_COLORS["ink"]),
        bgcolor="rgba(255,255,255,0.85)",
        bordercolor=UI_COLORS["grid"],
    )
    fig.update_yaxes(title_text="Entri", secondary_y=False, rangemode="tozero")
    fig.update_yaxes(
        title_text="Kumulatif",
        secondary_y=True,
        rangemode="tozero",
        showgrid=False,
    )
    fig.update_xaxes(showgrid=False)
    return apply_theme(fig, height=390, show_legend=True)


def radar_chart(df: pd.DataFrame) -> go.Figure:
    """Radar indeks 7KAIH per batalyon."""
    fig = go.Figure()
    if df.empty:
        return apply_theme(fig)
    labels = [habit.short_label for habit in HABITS]
    theta = labels + [labels[0]]
    present = [code for code in BATTALION_COLORS if code in set(df["battalion"].astype(str))]
    for code in present:
        subset = df[df["battalion"].astype(str) == code]
        values = analytics.index_by_habit(subset)["index"].tolist()
        r = values + [values[0]]
        fig.add_trace(
            go.Scatterpolar(
                r=r,
                theta=theta,
                name=f"Kelas {code}",
                fill="toself",
                opacity=0.55,
                line=dict(color=BATTALION_COLORS[code], width=2.4),
                hovertemplate="%{theta}: %{r:.1f}/100<extra>Kelas " + code + "</extra>",
            )
        )
    fig.update_layout(
        polar=dict(
            bgcolor="white",
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                gridcolor=UI_COLORS["grid"],
                tickfont=dict(size=9, color=UI_COLORS["muted"]),
            ),
            angularaxis=dict(
                gridcolor=UI_COLORS["grid"],
                tickfont=dict(size=10, color=UI_COLORS["ink"]),
            ),
        )
    )
    return apply_theme(fig, height=400, show_legend=True)


def priority_matrix_chart(matrix: pd.DataFrame) -> go.Figure:
    """Scatter prioritas: positif vs perlu perhatian."""
    fig = go.Figure()
    if matrix.empty:
        return apply_theme(fig)
    sizes = matrix["attention"].astype(float)
    max_size = max(1.0, float(sizes.max()))
    marker_sizes = 14 + sizes / max_size * 30
    colors = [QUADRANT_COLORS.get(q, UI_COLORS["muted"]) for q in matrix["quadrant"]]
    fig.add_trace(
        go.Scatter(
            x=matrix["positive_pct"],
            y=matrix["attention_pct"],
            mode="markers+text",
            text=matrix["habit"],
            textposition="top center",
            textfont=dict(size=10, color=UI_COLORS["ink"]),
            marker=dict(
                size=marker_sizes,
                color=colors,
                opacity=0.85,
                line=dict(color="white", width=1.5),
            ),
            customdata=matrix[["positive", "attention", "quadrant"]],
            hovertemplate=(
                "<b>%{text}</b><br>Positif: %{x:.1f}% (%{customdata[0]} entri)"
                "<br>Perlu perhatian: %{y:.1f}% (%{customdata[1]} entri)"
                "<br>Kuadran: %{customdata[2]}<extra></extra>"
            ),
            showlegend=False,
        )
    )
    fig.add_vline(
        x=POSITIVE_BENCHMARK,
        line=dict(color=UI_COLORS["muted"], width=1, dash="dot"),
    )
    fig.add_hline(
        y=ATTENTION_BENCHMARK,
        line=dict(color=UI_COLORS["muted"], width=1, dash="dot"),
    )
    x_min = max(0.0, float(matrix["positive_pct"].min()) - 8)
    y_max = max(30.0, float(matrix["attention_pct"].max()) + 8)
    fig.update_xaxes(title="Respons positif (%)", range=[x_min, 100], ticksuffix="%")
    fig.update_yaxes(title="Perlu perhatian (%)", range=[0, y_max], ticksuffix="%")
    corners = [
        (x_min + 1.5, y_max - 1.5, "Prioritas Tinggi", "left", "top"),
        (99.0, y_max - 1.5, "Waspada", "right", "top"),
        (x_min + 1.5, 1.5, "Pantau", "left", "bottom"),
        (99.0, 1.5, "Pertahankan", "right", "bottom"),
    ]
    for x, y, text, xanchor, yanchor in corners:
        fig.add_annotation(
            x=x,
            y=y,
            text=text,
            showarrow=False,
            xanchor=xanchor,
            yanchor=yanchor,
            font=dict(size=9, color=UI_COLORS["muted"]),
        )
    return apply_theme(fig, height=400)


def index_gauge(value: float) -> go.Figure:
    """Gauge indeks 7KAIH keseluruhan."""
    safe_value = 0.0 if value != value else float(value)
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=safe_value,
            number=dict(suffix="/100", font=dict(size=30, color=UI_COLORS["ink"])),
            gauge=dict(
                axis=dict(range=[0, 100], tickwidth=1, tickcolor=UI_COLORS["muted"]),
                bar=dict(color=UI_COLORS["navy"], thickness=0.28),
                bgcolor="white",
                borderwidth=0,
                steps=[
                    dict(range=[0, 60], color="#F6D5D0"),
                    dict(range=[60, 80], color="#F7E3B5"),
                    dict(range=[80, 100], color="#D6EBDD"),
                ],
                threshold=dict(
                    line=dict(color=UI_COLORS["gold"], width=3),
                    thickness=0.8,
                    value=90,
                ),
            ),
        )
    )
    fig = apply_theme(fig, height=240)
    fig.update_layout(margin=dict(l=34, r=34, t=24, b=6))
    return fig


def empty_figure(message: str) -> go.Figure:
    """Placeholder saat tidak ada data."""
    fig = go.Figure()
    fig.add_annotation(
        text=message,
        x=0.5,
        y=0.5,
        xref="paper",
        yref="paper",
        showarrow=False,
        font=dict(size=13, color=UI_COLORS["muted"]),
    )
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    return apply_theme(fig, height=240)
