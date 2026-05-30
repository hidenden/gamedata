from datetime import date
from unittest.mock import patch

import altair as alt
import polars as pl

import gamedata.chart_bar as cb
import gamedata.chart_line as cl
from gamedata.chart_config import ALT_EMBED_OPTIONS


def _assert_embed_options(chart: alt.Chart | alt.LayerChart | alt.FacetChart) -> None:
    spec = chart.to_dict(validate=False)
    assert spec["usermeta"]["embedOptions"] == ALT_EMBED_OPTIONS


def test_chart_bar_sales_embed_options_from_theme():
    src_df = pl.DataFrame({"x": [1], "y": [2], "category": ["A"]})
    chart = cb._chart_bar_sales(
        src_df=src_df,
        alt_x=alt.X("x:Q"),
        alt_y=alt.Y("y:Q"),
        color=alt.Color("category:N"),
    )
    _assert_embed_options(chart)


def test_chart_line_sales_embed_options_from_theme():
    src_df = pl.DataFrame({"x": [1], "y": [2], "category": ["A"]})
    chart = cl._chart_line_sales(
        src_df=src_df,
        alt_x=alt.X("x:Q"),
        alt_y=alt.Y("y:Q"),
        color=alt.Color("category:N"),
    )
    _assert_embed_options(chart)


def test_chart_hbar_yearly_share_by_maker_embed_options(sample_sales_df):
    with patch.object(cb.hs, "load_hard_sales", return_value=sample_sales_df):
        chart = cb.chart_hbar_yearly_share_by_maker(
            begin=date(2020, 1, 1), end=date(2021, 12, 31)
        )
    _assert_embed_options(chart)


def test_chart_pie_yearly_share_by_maker_embed_options(sample_sales_df):
    with patch.object(cb.hs, "load_hard_sales", return_value=sample_sales_df):
        chart = cb.chart_pie_yearly_share_by_maker(begin_year=2020, end_year=2021)
    _assert_embed_options(chart)
