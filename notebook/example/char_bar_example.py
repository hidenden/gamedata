# /// script
# [tool.marimo.display]
# theme = "system"
# ///

import marimo

__generated_with = "0.23.6"
app = marimo.App(width="medium")

with app.setup:
    # 標準ライブラリ
    from datetime import date

    import marimo as mo

    # プロジェクト内モジュール
    import gamedata as g


@app.cell(hide_code=True)
def md_cell_01():
    mo.md(r"""
    # chart_bar.py
    """)
    return


@app.cell
def calc_all_01():
    # 実データを読み込み、日付UIの初期値に最新集計日を利用する
    df_all = g.load_hard_sales()
    latest_date = g.current_report_date(df_all)
    return (latest_date,)


@app.cell
def latest_date(latest_date):
    ui_hws = g.HwSelect(default_list=["NSW", "PS5", "NS2"], force_any=True)
    ui_hw_single = mo.ui.dropdown(
        options=g.get_hw_all(), value="PS5", label="単一ハード"
    )
    ui_begin_date = mo.ui.date(label="開始日", value=date(2023, 1, 1))
    ui_end_date = mo.ui.date(label="終了日", value=latest_date)
    ui_mode = mo.ui.dropdown(
        options=["month", "quarter", "year"], value="month", label="集計単位"
    )
    ui_stacked = mo.ui.switch(label="積み上げ表示", value=False)
    ui_ymax = mo.ui.number(start=0, step=100000, value=0, label="Y軸上限(0で自動)")

    mo.vstack(
        [
            ui_hws,
            mo.hstack([ui_hw_single, ui_mode, ui_stacked], justify="start"),
            mo.hstack([ui_begin_date, ui_end_date, ui_ymax], justify="start"),
        ]
    )
    return (
        ui_begin_date,
        ui_end_date,
        ui_hw_single,
        ui_hws,
        ui_mode,
        ui_stacked,
        ui_ymax,
    )


@app.cell(hide_code=True)
def md_cell_02():
    mo.md(r"""
    ## chart_bar_sales
    """)
    return


@app.cell
def ui_begin_date(
    ui_begin_date,
    ui_end_date,
    ui_hws,
    ui_mode,
    ui_stacked,
    ui_ymax,
):
    # 選択したハードの期間別販売台数を棒グラフで確認する
    g.chart_bar_sales(
        hw=ui_hws.value,
        begin=ui_begin_date.value,
        end=ui_end_date.value,
        mode=ui_mode.value,
        stacked=ui_stacked.value,
        ymax=ui_ymax.value or None,
    )
    return


@app.cell(hide_code=True)
def md_cell_03():
    mo.md(r"""
    ## chart_bar_hwsales_by_year
    """)
    return


@app.cell
def ui_begin_date_2(ui_begin_date, ui_end_date, ui_hw_single, ui_ymax):
    # 単一ハードの月別推移を年ごとに並べて比較する
    g.chart_bar_hwsales_by_year(
        hw=ui_hw_single.value,
        begin=ui_begin_date.value,
        end=ui_end_date.value,
        mode="month",
        ymax=ui_ymax.value or None,
    )
    return


@app.cell(hide_code=True)
def md_cell_04():
    mo.md(r"""
    ## chart_hbar_yearly_share_by_maker
    """)
    return


@app.cell
def ui_begin_date_3(ui_begin_date, ui_end_date):
    # 年ごとのメーカーシェアを100%積み上げ横棒で表示する
    g.chart_hbar_yearly_share_by_maker(
        begin=ui_begin_date.value,
        end=ui_end_date.value,
    )
    return


@app.cell(hide_code=True)
def md_cell_05():
    mo.md(r"""
    ## chart_bar_sales_by_hard_year
    """)
    return


@app.cell
def ui_hwy_01():
    ui_hwy = mo.ui.array(
        [
            mo.ui.array(
                [
                    mo.ui.dropdown(options=g.get_hw_all(), value="NSW", label="HW"),
                    mo.ui.number(start=2001, stop=2026, value=2025, label="年"),
                ]
            ),
            mo.ui.array(
                [
                    mo.ui.dropdown(options=g.get_hw_all(), value="PS5", label="HW"),
                    mo.ui.number(start=2001, stop=2026, value=2025, label="年"),
                ]
            ),
        ]
    )
    mo.vstack([mo.hstack(row, justify="start") for row in ui_hwy])
    return (ui_hwy,)


@app.cell
def ui_hwy(ui_hwy, ui_mode, ui_stacked, ui_ymax):
    # ハードと年の組み合わせを月別/四半期別に比較する
    hwy = [(row[0], row[1]) for row in ui_hwy.value]
    mode = ui_mode.value if ui_mode.value in ["month", "quarter"] else "month"
    g.chart_bar_sales_by_hard_year(
        hwy=hwy,
        mode=mode,
        stacked=ui_stacked.value,
        ymax=ui_ymax.value or None,
    )
    return


@app.cell(hide_code=True)
def md_cell_06():
    mo.md(r"""
    ## chart_bar_yearly_delta
    """)
    return


@app.cell
def ui_hws(ui_hws, ui_stacked):
    # 発売年からの経過年ごとの販売台数を比較する
    g.chart_bar_yearly_delta(
        hw=ui_hws.value,
        stacked=ui_stacked.value,
        delta_begin=0,
        delta_end=6,
    )
    return


@app.cell(hide_code=True)
def md_cell_07():
    mo.md(r"""
    ## chart_bar_month_year
    """)
    return


@app.cell
def ui_month_02():
    ui_month = mo.ui.number(start=1, stop=12, value=12, label="対象月")
    ui_begin_year = mo.ui.number(start=2001, stop=2026, value=2017, label="開始年")
    ui_end_year = mo.ui.number(start=2001, stop=2026, value=2026, label="終了年")
    mo.hstack([ui_month, ui_begin_year, ui_end_year], justify="start")
    return ui_begin_year, ui_end_year, ui_month


@app.cell
def ui_begin_year(ui_begin_year, ui_end_year, ui_month, ui_stacked):
    # 指定月だけを取り出し、年ごとのメーカー販売台数を見る
    g.chart_bar_month_year(
        month=ui_month.value,
        begin_year=ui_begin_year.value,
        end_year=ui_end_year.value,
        stacked=ui_stacked.value,
    )
    return


@app.cell(hide_code=True)
def md_cell_08():
    mo.md(r"""
    ## chart_pie_yearly_share_by_maker
    """)
    return


@app.cell
def ui_begin_year_2(ui_begin_year, ui_end_year):
    # メーカー別年次シェアを円グラフで表示する
    g.chart_pie_yearly_share_by_maker(
        begin_year=ui_begin_year.value,
        end_year=ui_end_year.value,
    )
    return


if __name__ == "__main__":
    app.run()
