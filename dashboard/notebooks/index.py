import marimo

__generated_with = "0.26.0"
app = marimo.App(width="medium", app_title="ゲーム機の週間販売台数")


@app.cell
async def _():
    import sys

    import marimo as mo

    if sys.platform == "emscripten":
        import micropip
        from js import location
        from pyodide.http import pyfetch

        _packages = f"{location.origin}/dashboard/packages"
        _response = await pyfetch(f"{_packages}/wheel.json")
        _response.raise_for_status()
        _wheel = (await _response.json())["filename"]
        await micropip.install(["polars", "pyarrow", "pandas", "jinja2", "altair"])
        # ローカルの開発・分析ツールは Pyodide にインストールしない。
        await micropip.install(f"{_packages}/{_wheel}", deps=False)

    import gamedata as g

    return g, mo


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # ゲーム機の週間販売台数
    """)
    return


@app.cell
def _(g):
    sales = g.load_hard_sales()
    hardware = g.load_hard_info()
    annotations = g.load_hard_annotation()
    return annotations, hardware, sales


@app.cell(hide_code=True)
def _(mo, sales):
    mo.stop(sales.is_empty(), mo.md("週次販売データがありません。"))
    _weeks = sales["report_date"].unique().sort(descending=True).head(12)
    _options = {d.isoformat(): d for d in _weeks}
    week = mo.ui.dropdown(_options, value=next(iter(_options)), label="集計週の末日")
    week
    return (week,)


@app.cell(hide_code=True)
def _(annotations, hardware, mo, sales, week):
    _sales = sales.filter(sales["report_date"] == week.value).join(
        hardware.select("id", "full_name"), left_on="hw", right_on="id"
    ).sort("units", descending=True)
    _notes = annotations.filter(annotations["report_date"] == week.value)
    mo.vstack([
        mo.md(f"**合計 {_sales['units'].sum():,} 台**　｜　{_sales.height} 機種　｜　関連する注釈 {_notes.height} 件"),
        mo.ui.table(
            [{"機種": name, "販売台数": f"{units:,} 台"}
             for name, units in _sales.select("full_name", "units").iter_rows()],
            selection=None, pagination=False, show_column_summaries=False,
        ),
    ])
    return


if __name__ == "__main__":
    app.run()
