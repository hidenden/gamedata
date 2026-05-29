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
    # chart_line.py
    """)
    return


@app.cell
def calc_all_01():
    # 実データの最新日をUI初期値に使う
    df_all = g.load_hard_sales()
    latest_date = g.current_report_date(df_all)
    return latest_date


@app.cell
def latest_date(latest_date):
    ui_hws = g.HwSelect(default_list=["NSW", "PS5", "NS2"], force_any=True)
    ui_begin_date = mo.ui.date(label="開始日", value=date(2025, 1, 1))
    ui_end_date = mo.ui.date(label="終了日", value=latest_date)
    ui_mode = mo.ui.dropdown(
        options=["week", "month", "quarter", "year"], value="week", label="集計単位"
    )
    ui_annotation = mo.ui.number(
        start=0, stop=50, step=1, value=20, label="アノテーションレベル"
    )
    ui_multiline = mo.ui.switch(label="Multi-line tooltip", value=True)

    mo.vstack(
        [
            ui_hws,
            mo.hstack([ui_begin_date, ui_end_date, ui_mode], justify="start"),
            mo.hstack([ui_annotation, ui_multiline], justify="start"),
        ]
    )
    return ui_annotation, ui_begin_date, ui_end_date, ui_hws, ui_mode, ui_multiline


@app.cell(hide_code=True)
def md_cell_02():
    mo.md(r"""
    ## chart_line_sales
    """)
    return


@app.cell
def ui_annotation(ui_annotation, ui_begin_date, ui_end_date, ui_hws, ui_mode, ui_multiline):
    # 週次/月次などの販売台数推移を折れ線で表示する
    g.chart_line_sales(
        hw=ui_hws.value,
        mode=ui_mode.value,
        begin=ui_begin_date.value,
        end=ui_end_date.value,
        annotation_level=ui_annotation.value or None,
        multi_line=ui_multiline.value,
    )
    return


@app.cell(hide_code=True)
def md_cell_03():
    mo.md(r"""
    ## chart_line_cumulative
    """)
    return


@app.cell
def ui_annotation_2(ui_annotation, ui_begin_date, ui_end_date, ui_hws, ui_mode, ui_multiline):
    # カレンダー日付ベースの累計販売台数を確認する
    _mode = ui_mode.value if ui_mode.value in ["week", "month", "year"] else "month"
    g.chart_line_cumulative(
        hw=ui_hws.value,
        mode=_mode,
        begin=ui_begin_date.value,
        end=ui_end_date.value,
        annotation_level=ui_annotation.value or None,
        multi_line=ui_multiline.value,
    )
    return


@app.cell(hide_code=True)
def md_cell_04():
    mo.md(r"""
    ## chart_line_cumulative_delta
    """)
    return


@app.cell
def ui_delta_begin_01():
    ui_delta_begin = mo.ui.number(start=0, value=0, label="経過期間 開始")
    ui_delta_end = mo.ui.number(start=1, value=52, label="経過期間 終了")
    mo.hstack([ui_delta_begin, ui_delta_end], justify="start")
    return ui_delta_begin, ui_delta_end


@app.cell
def ui_annotation_3(ui_annotation, ui_delta_begin, ui_delta_end, ui_hws, ui_mode, ui_multiline):
    # 発売からの経過期間を揃えて累計販売台数を比較する
    _mode = ui_mode.value if ui_mode.value in ["week", "month", "year"] else "week"
    g.chart_line_cumulative_delta(
        hw=ui_hws.value,
        mode=_mode,
        begin=ui_delta_begin.value,
        end=ui_delta_end.value,
        annotation_level=ui_annotation.value or None,
        multi_line=ui_multiline.value,
    )
    return


@app.cell(hide_code=True)
def md_cell_05():
    mo.md(r"""
    ## chart_line_weekly_by_hw_date
    """)
    return


@app.cell
def ui_periods_02():
    ui_periods = mo.ui.array(
        [
            mo.ui.array(
                [
                    mo.ui.dropdown(options=g.get_hw_all(), value="NSW", label="HW"),
                    mo.ui.date(label="開始日", value=date(2017, 3, 3)),
                ]
            ),
            mo.ui.array(
                [
                    mo.ui.dropdown(options=g.get_hw_all(), value="PS5", label="HW"),
                    mo.ui.date(label="開始日", value=date(2020, 11, 15)),
                ]
            ),
            mo.ui.array(
                [
                    mo.ui.dropdown(options=g.get_hw_all(), value="NS2", label="HW"),
                    mo.ui.date(label="開始日", value=date(2025, 6, 5)),
                ]
            ),
        ]
    )
    ui_period_end = mo.ui.number(start=1, value=52, label="表示週数")
    mo.vstack([*[mo.hstack(row, justify="start") for row in ui_periods], ui_period_end])
    return ui_period_end, ui_periods


@app.cell
def ui_multiline(ui_multiline, ui_period_end, ui_periods):
    # 任意の開始日からの週数を揃え、発売初期などの販売推移を比較する
    hw_periods = [
        {"hw": row[0], "begin": row[1], "label": f"{row[0]} {row[1]}"}
        for row in ui_periods.value
    ]
    g.chart_line_weekly_by_hw_date(
        hw_periods=hw_periods,
        end=ui_period_end.value,
        multi_line=ui_multiline.value,
    )
    return


@app.cell(hide_code=True)
def md_cell_06():
    mo.md(r"""
    ## chart_line_cumsum_diffs
    """)
    return


@app.cell
def ui_annotation_4(ui_annotation, ui_multiline):
    # 同じ集計日における累計販売台数差を確認する
    g.chart_line_cumsum_diffs(
        cmplist=[("NS2", "PS5"), ("NSW", "PS4")],
        annotation_level=ui_annotation.value or None,
        multi_line=ui_multiline.value,
    )
    return


@app.cell(hide_code=True)
def md_cell_07():
    mo.md(r"""
    ## chart_line_pase_diffs
    """)
    return


@app.cell
def ui_multiline_2(ui_multiline):
    # 発売後の同じ週数における累計販売ペース差を表示する
    g.chart_line_pase_diffs(
        cmplist=[("PS5", "PS4"), ("NS2", "PS5")],
        multi_line=ui_multiline.value,
    )
    return


@app.cell(hide_code=True)
def md_cell_08():
    mo.md(r"""
    ## chart_line_ycumulative
    """)
    return


@app.cell
def ui_year_03():
    ui_year = mo.ui.number(start=2001, stop=2026, value=2026, label="対象年")
    mo.hstack([ui_year], justify="start")
    return (ui_year,)


@app.cell
def ui_annotation_5(ui_annotation, ui_hws, ui_multiline, ui_year):
    # 同一年内の年次累計販売台数をハード別に比較する
    g.chart_line_ycumulative(
        hw=ui_hws.value,
        year=ui_year.value,
        begin=1,
        end=366,
        annotation_level=ui_annotation.value or None,
        multi_line=ui_multiline.value,
    )
    return


@app.cell(hide_code=True)
def md_cell_09():
    mo.md(r"""
    ## chart_line_ycumulative_by_hw_year
    """)
    return


@app.cell
def ui_multiline_3(ui_multiline):
    # ハードと年の組み合わせを指定し、年間通算日を揃えて比較する
    g.chart_line_ycumulative_by_hw_year(
        hw_years=[("NSW", 2025), ("PS5", 2025), ("NS2", 2026)],
        begin=1,
        end=366,
        multi_line=ui_multiline.value,
    )
    return


if __name__ == "__main__":
    app.run()
