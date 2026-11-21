"""Format angka dan tanggal dengan konvensi Indonesia."""

from __future__ import annotations

from datetime import date, datetime

MONTHS_ID: tuple[str, ...] = (
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "Mei",
    "Jun",
    "Jul",
    "Agu",
    "Sep",
    "Okt",
    "Nov",
    "Des",
)


def pct(value: float, decimals: int = 1) -> str:
    """Format persentase dengan koma desimal, mis. 12.345 -> '12,3%'."""
    if value is None or value != value:  # NaN-safe tanpa numpy
        return "–"
    return f"{value:.{decimals}f}".replace(".", ",") + "%"


def num(value: int | float) -> str:
    """Format bilangan bulat dengan pemisah ribuan titik."""
    if value is None or value != value:
        return "–"
    return f"{int(round(value)):,}".replace(",", ".")


def ratio(count: int, total: int, decimals: int = 1) -> str:
    """Format 'n (x%)' dengan aman untuk total nol."""
    if total <= 0:
        return f"{num(count)} (0%)"
    return f"{num(count)} ({pct(count / total * 100, decimals)})"


def date_id(value: date | datetime) -> str:
    """Format tanggal Indonesia ringkas, mis. '5 Nov 2026'."""
    return f"{value.day} {MONTHS_ID[value.month - 1]} {value.year}"


def date_long_id(value: date | datetime) -> str:
    """Format tanggal Indonesia lengkap, mis. '5 November 2026'."""
    names = (
        "Januari",
        "Februari",
        "Maret",
        "April",
        "Mei",
        "Juni",
        "Juli",
        "Agustus",
        "September",
        "Oktober",
        "November",
        "Desember",
    )
    return f"{value.day} {names[value.month - 1]} {value.year}"


def delta_pp(value: float, decimals: int = 1) -> str:
    """Format selisih poin persentase dengan tanda."""
    sign = "+" if value > 0 else ""
    return f"{sign}{pct(value, decimals)}"
