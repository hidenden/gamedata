import marimo

__generated_with = "0.23.3"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    from datetime import datetime, timedelta
    # サードパーティライブラリ
    import polars as pl
    # import polars.selectors as cs

    # プロジェクト内モジュール
    import gamedata as g
    g.set_dispfunc(func=None)
    return datetime, g, mo


@app.cell
def _(datetime, g, mo):
    def sales_by_year(year: int, hw=['NS2', 'NSW', 'PS5'], stacked=False):
        begin = datetime(year, 1, 1)
        end = datetime(year + 1, 1, 1)
        report_event_mask = g.EventMasks(hard=1.5, price=3, sale=2, soft=3, event=2)
        fig1, df1 = g.plot_sales(begin=begin, end=end, event_mask=report_event_mask)
        fig2, df2 = g.plot_monthly_bar_by_hard(hw=hw, begin=begin, end=end, stacked=stacked)
        return (
            mo.md(f"# {year}年のハード販売状況"),
            fig1,
            fig2,
            df1,
            df2
        )

    return (sales_by_year,)


@app.cell
def _(g, mo):
    from ipywidgets.embed import DEFAULT_EMBED_REQUIREJS_URL
    year = mo.ui.number(start=2001, stop=2026, step=1, value=2025, label="対象年")
    hwselect = g.HwSelect()
    hw_widget = hwselect.widget
    stacked = mo.ui.checkbox(label="積み上げ棒グラフ", value=False)
    return hw_widget, hwselect, stacked, year


@app.cell
def _(hw_widget, hwselect, mo, sales_by_year, stacked, year):
    hw_widget
    (_title, _fig1, _fig2, _df1, _df2) = sales_by_year(year=year.value, hw=hwselect.value, stacked=stacked.value)
    mo.vstack([year, _title, _fig1, hwselect, stacked, _fig2, _df2], justify="start")
    return


@app.cell
def _(g, mo):
    hw_dropdown = mo.ui.dropdown(options=g.get_hw_all(), value='NSW', label='ハード選択:')
    return (hw_dropdown,)


@app.cell
def _(g, hw_dropdown, mo):
    (_fig, _df) = g.plot_quarterly_bar_by_year(hw=hw_dropdown.value)
    mo.vstack([
        mo.md(f"## 四半期ごとの{hw_dropdown.value}販売台数"),
        hw_dropdown,
        _fig,
        _df
    ], justify="start")
    return


if __name__ == "__main__":
    app.run()
