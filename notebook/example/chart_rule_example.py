# /// script
# [tool.marimo.display]
# theme = "system"
# ///

import marimo

__generated_with = "0.23.6"
app = marimo.App(width="medium")

with app.setup:
    import marimo as mo

    # プロジェクト内モジュール
    import gamedata as g


@app.cell(hide_code=True)
def md_cell_01():
    mo.md(r"""
    # chart_rule.py
    """)
    return


@app.cell
def ui_hws_01():
    ui_hws = g.HwSelect(default_list=["NSW", "PS5"], force_any=True)
    ui_rule_x = mo.ui.number(start=1, value=52, label="縦線: 週数")
    ui_rule_y = mo.ui.number(start=0, step=100000, value=5000000, label="横線: 台数")
    mo.vstack([ui_hws, mo.hstack([ui_rule_x, ui_rule_y], justify="start")])
    return ui_hws, ui_rule_x, ui_rule_y


@app.cell(hide_code=True)
def md_cell_02():
    mo.md(r"""
    ## chart_rule_xy
    """)
    return


@app.cell
def ui_hws(ui_hws, ui_rule_x, ui_rule_y):
    # ベースチャートに縦横の基準線を重ねる
    _base_chart = g.chart_line_cumulative_delta(
        hw=ui_hws.value,
        mode="week",
        begin=0,
        end=104,
        multi_line=True,
    )
    g.chart_rule_xy(
        base_chart=_base_chart,
        x=ui_rule_x.value,
        y=ui_rule_y.value,
        stroke=[6, 4],
        color="crimson",
    )
    return


@app.cell(hide_code=True)
def md_cell_03():
    mo.md(r"""
    ## chart_line_guide
    """)
    return


@app.cell
def ui_hws_2(ui_hws):
    # 2点を結ぶ補助線を重ね、販売ペースの目安として使う
    _base_chart = g.chart_line_cumulative_delta(
        hw=ui_hws.value,
        mode="week",
        begin=0,
        end=104,
        multi_line=True,
    )
    g.chart_line_guide(
        base_chart=_base_chart,
        x=1,
        y=0,
        x2=52,
        y2=5000000,
        stroke=[2, 3],
        color="darkgreen",
    )
    return


if __name__ == "__main__":
    app.run()
