from __future__ import annotations

from datetime import date

from g7kaih.formatting import date_id, date_long_id, delta_pp, num, pct, ratio


def test_pct_uses_indonesian_decimal() -> None:
    assert pct(12.345) == "12,3%"
    assert pct(92.666, 2) == "92,67%"


def test_num_uses_thousands_separator() -> None:
    assert num(1000) == "1.000"
    assert num(232) == "232"


def test_ratio() -> None:
    assert ratio(60, 232, 2) == "60 (25,86%)"
    assert ratio(0, 0) == "0 (0%)"


def test_date_formats() -> None:
    assert date_id(date(2026, 11, 5)) == "5 Nov 2026"
    assert date_long_id(date(2026, 11, 5)) == "5 November 2026"


def test_delta() -> None:
    assert delta_pp(3.2) == "+3,2%"
    assert delta_pp(-1.5) == "-1,5%"
