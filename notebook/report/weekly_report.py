# /// script
# [tool.marimo.display]
# theme = "system"
# ///

import marimo

__generated_with = "0.23.3"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import altair as alt
    # 標準ライブラリ
    from datetime import datetime, timedelta, date

    # サードパーティライブラリ
    import polars as pl
    # import polars.selectors as cs

    # プロジェクト内モジュール
    import gamedata as g
    g.set_dispfunc(func=None)
    return alt, datetime, g, mo


@app.cell
def _(mo):
    meta = mo.app_meta()
    is_publish = True
    if meta.mode in ["edit", "run"]:
        is_publish = False

    return (is_publish,)


@app.cell
def _(datetime, g, is_publish, mo):
    # レポート日付
    from report_config import get_config

    config = get_config()
    report_date = config["date"]
    report_event_mask = g.EventMasks(hard=1.5, price=3, sale=2, soft=1.5, event=1)

    def show_title(d:datetime) -> None:
        last_updated_str = d.strftime("%Y-%m-%d")
        mode = "LAB MODE" if not is_publish else ""
        return mo.md(f"# 国内ゲームハード週販レポート ({last_updated_str}) {mode}")

    df_all = g.load_hard_sales()
    return df_all, report_date, show_title


@app.cell
def _(report_date, show_title):
    show_title(report_date)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    * ハードウェアの販売データはファミ通の調査結果を基にしています。
    * 一部のデータは処理上の都合により、週次値に調整しています｡
    * [過去の週販レポート](../index.html)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 直近4週間のハード売り上げ／累計推移
    """)
    return


@app.cell
def _(df_all, g, report_date):
    g.chart_units_by_date_hw(df_all, begin=g.weeks_before(report_date, 3), end=report_date)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Switch2が7週間ぶりに下げ止まって増加しました｡先週から1500台増加の4万5千台です｡
    5万台前後で安定するのであれば特に問題ないでしょう｡
    ぽこあポケモンはパッケージ累計92万本､100万本が射程距離内です｡

    Switchは4千台下げましたが､それでも高水準の2万7千台｡
    Switch Liteの好調が続きます｡
    トモダチコレクションは累計74万本､こちらも100万本を目指せるでしょう｡

    PS5はさらに2千台増加し1万2千台です｡
    値上げ以降 PS5 Proが以下のように増え続けています｡
    よくわからない動きです｡

    1219台 → 3066台 → 4330台
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 週販推移
    """)
    return


@app.cell
def _(alt, df_all, g, mo, report_date):
    _begin = g.report_begin(report_date)
    _end = report_date
    _weekly_df = g.date_filter(df_all, begin=_begin, end=_end)
    _base = alt.Chart(_weekly_df).encode(
            x='report_date:T',
            y='units:Q',
            color='hw:N',
        )

    weekly_chart = mo.ui.altair_chart(
        ((_base.mark_point() + _base.mark_line())).properties(
            width=800,
            height=400,
            title='販売台数(週単位)'
        )
    )
    weekly_chart
    return (weekly_chart,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 週販推移(拡大)
    """)
    return


@app.cell
def _(alt, mo, weekly_chart):
    _zoom_df = weekly_chart.value
    _zoom_base = alt.Chart(_zoom_df).encode(
            x='report_date:T',
            y='units:Q',
            color='hw:N',
        )
    _zoom_chart = mo.ui.altair_chart(
        ((_zoom_base.mark_point() + _zoom_base.mark_line())).properties(
            width=800,
            height=400,
            title='販売台数(週単位)[拡大]',
        )
    )
    _zoom_chart
    return


if __name__ == "__main__":
    app.run()
