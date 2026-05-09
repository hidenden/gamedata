import marimo

__generated_with = "0.23.5"
app = marimo.App(width="medium")

with app.setup:
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


@app.cell
def _():
    df_all = g.load_hard_sales()
    return (df_all,)


@app.cell
def _(df_all):
    share_df = g.maker_long(df_all, begin_year=2016)
    share_df
    return


@app.cell
def _(df_all):
    def chart_hbar_maker_share_by_year(
        begin:datetime | date | None = None,
        end: datetime | date | None = None
    ) -> alt.Chart:

        _df = g.maker_long(df_all, begin_year=2016)
        _df = (
            _df
            .with_columns(
            ((pl.col('yearly_pct').cum_sum().over('year') - pl.col('yearly_pct') / 2) / 100)
            .alias('mid_point'),
            (pl.col('yearly_pct').round(1).cast(pl.String) + '%')
            .alias('pct_label'),
            )
        )

        maker_list = g.get_maker(_df)
        maker_color = g.get_maker_colors(maker_list)
        _base = alt.Chart(_df).encode(
            y=alt.Y('year:O', sort='descending', title='年'),
            x=alt.X('yearly_pct:Q', stack='normalize', title='メーカーシェア'),
            color=alt.Color('maker_name:N', title='メーカー',
                            scale=alt.Scale(domain=maker_list, range=maker_color)),
            order=alt.Order('mid_point:Q'),
        )

        _bars = _base.mark_bar()
        _text = _base.mark_text(size=12, baseline='middle').encode(
            detail='maker_name:N',
            color=alt.value('white'),
            text=alt.Text('pct_label:N'),
            x=alt.X('mid_point:Q'),
        )
        return (_bars + _text).properties(width=800, height=400, title='年間シェア推移')


    return


@app.cell
def _():
    c1 = g.chart_hbar_maker_share_by_year(
        datetime(2016, 1, 1),
        datetime(2026, 12, 31)
    )
    mo.ui.altair_chart(c1)
    return


if __name__ == "__main__":
    app.run()
