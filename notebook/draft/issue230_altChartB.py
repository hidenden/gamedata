import marimo

__generated_with = "0.23.3"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import altair as alt
    # 標準ライブラリ
    from datetime import datetime, timedelta, date
    from typing import List, Optional

    # サードパーティライブラリ
    import polars as pl
    # import polars.selectors as cs

    # プロジェクト内モジュール
    import gamedata as g

    return datetime, g, mo


@app.cell
def _(g):
    df_all = g.load_hard_sales()

    return (df_all,)


@app.cell
def _(df_all, g):
    src_df = g.monthly_sales_long(df_all)
    src_df.tail(10)
    return


@app.cell
def _(datetime, g, mo):
    _begin = datetime(2022, 9, 1)
    _end = datetime(2026, 4, 30)

    mo.ui.altair_chart(
    g.chart_sales(begin=_begin, end=_end, mode="week", 
                            event_mask=g.EVENT_MASK_MIDDLE).interactive()
    )
    return


@app.cell
def _(datetime, g, mo):
    chart_offset = g.chart_sales_with_offset(
      hw_periods=[
          {'hw': 'PS5', 'begin': datetime(2023,3,1)},
          {'hw': 'PS5', 'begin': datetime(2024,3,1)},
          {'hw': 'PS5', 'begin': datetime(2025,3,1)},
          {'hw': 'PS5', 'begin': datetime(2026,3,1)},
          ],
      end = 20)

    mo_chart_offset = mo.ui.altair_chart(chart_offset)
    mo_chart_offset
    return


@app.cell
def _(datetime, g):
    g.chart_cumulative_sales(hw=["NSW", "PS5", "NS2", "XSX"], mode="week", 
                            begin=datetime(2017,3,3),
                            event_mask=g.EVENT_MASK_LONG)
    return


@app.cell
def _(g, mo):
    mo.ui.altair_chart(g.chart_cumulative_sales_by_delta(hw=["NS2", "NSW", "PS5", "3DS", "DS", "GBA", "PS2", "Wii"], mode="week", 
                            end=80,
                            event_mask=g.EVENT_MASK_SHORT))
    return


if __name__ == "__main__":
    app.run()
