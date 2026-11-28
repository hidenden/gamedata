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
    mo.md("""
    # ゲーム機の販売動向
    """)


@app.cell(hide_code=True)
def _(g):
    import altair as alt
    import polars as pl

    sales = g.load_hard_sales()
    annotations = g.load_hard_annotation()
    return alt, annotations, pl, sales


@app.cell(hide_code=True)
def _(mo, sales):
    mo.stop(sales.is_empty(), mo.md("週次販売データがありません。"))
    _weeks = sales["report_date"].unique().sort(descending=True)
    _options = {d.isoformat(): d for d in _weeks}
    week = mo.ui.dropdown(
        _options, value=next(iter(_options)), searchable=True,
        allow_select_none=False, label="基準週（集計末日）",
    )
    view = mo.ui.radio(
        ["市場の振り返り", "機種サマリー", "年別比較"], value="市場の振り返り", inline=True,
    )
    mo.vstack([view, week])
    return view, week


@app.cell(hide_code=True)
def _(g, pl, sales, week):
    history = g.date_filter(sales, end=week.value)
    ranking = (
        history.group_by("hw", "full_name")
        .agg(
            total=pl.col("units").sum(),
            first=pl.col("report_date").min(),
            last=pl.col("report_date").max(),
            weeks=pl.col("report_date").n_unique(),
        )
        .with_columns(rank=pl.col("total").rank("min", descending=True))
        .sort(["total", "hw"], descending=[True, False])
    )
    return history, ranking


@app.cell(hide_code=True)
def machine_picker(mo, pl, sales):
    mo.stop(sales.is_empty())
    _totals = sales.group_by("full_name", "hw").agg(pl.col("units").sum()).sort(
        ["units", "hw"], descending=[True, False],
    )
    _options = dict(_totals.select("full_name", "hw").iter_rows())
    machine = mo.ui.dropdown(
        _options, value=next(iter(_options)), searchable=True,
        allow_select_none=False, label="機種",
    )
    return (machine,)


@app.cell(hide_code=True)
def machine_control(machine, mo, view):
    mo.stop(view.value == "市場の振り返り")
    machine


@app.cell(hide_code=True)
def current_data(history, machine, mo, pl, view):
    machine_history = history.filter(pl.col("hw") == machine.value)
    market_view = view.value == "市場の振り返り"
    scope = history if market_view else machine_history
    mo.stop(scope.is_empty(), mo.md("この基準週までに選択した機種の販売記録はありません。"))
    return machine_history, market_view, scope


@app.cell(hide_code=True)
def summary_panel(
    annotations,
    history,
    machine,
    machine_history,
    market_view,
    mo,
    pl,
    ranking,
    view,
    week,
):
    mo.stop(view.value == "年別比較")
    if market_view:
        _current = history.filter(pl.col("report_date") == week.value).sort("units", descending=True)
        _notes = annotations.filter(pl.col("report_date") == week.value)
        _metrics = [
            mo.stat(f"{_current['units'].sum():,} 台", label="週間販売台数"),
            mo.stat(f"{_current.height} 機種", label="集計機種"),
            mo.stat(f"{_notes.height} 件", label="関連する注釈"),
        ]
        _table = mo.ui.table(
            _current.select(機種="full_name", 販売台数="units"),
            selection=None, pagination=False, show_column_summaries=False,
        )
        _panel = mo.vstack([mo.hstack(_metrics, wrap=True, justify="start", gap=2), _table])
    else:
        _row = ranking.filter(pl.col("hw") == machine.value).row(0, named=True)
        _launch = machine_history.filter(pl.col("delta_week") == 0)
        _launch_units = f"{_launch['units'].sum():,} 台" if _launch.height else "記録なし"
        _metrics = [
            mo.stat(f"{_row['total']:,} 台", label="累計販売台数"),
            mo.stat(f"{_row['weeks']:,} 週", label="記録週数"),
            mo.stat(_launch_units, label="発売週の販売台数"),
            mo.stat(f"{_row['total'] / _row['weeks']:,.0f} 台", label="平均週販"),
            mo.stat(f"{_row['rank']} 位", label="歴代累計順位", caption=f"集計対象 {ranking.height} 機種"),
        ]
        _panel = mo.vstack([
            mo.md(f"**{_row['full_name']}**　記録期間　{_row['first']:%Y/%m/%d} 〜 {_row['last']:%Y/%m/%d}"),
            mo.hstack(_metrics, wrap=True, justify="start", gap=2),
        ])
    _panel


@app.cell(hide_code=True)
def weekly_bestsellers(annotations, machine, machine_history, mo, pl, view):
    mo.stop(view.value != "機種サマリー")
    _best = machine_history.select("report_date", "units").sort(
        ["units", "report_date"], descending=[True, False],
    ).head(5).with_row_index("順位", offset=1)

    # 同日にイベントが複数ある場合は、ひとつの欄にまとめる。
    _events = (
        annotations.filter((pl.col("hw") == machine.value) & pl.col("note").is_not_null())
        .sort(["annotation_date", "level", "id"])
        .group_by("annotation_date", maintain_order=True)
        .agg(pl.col("note").str.join("、"))
    )
    best_weeks = (
        _best.sort("report_date").join_asof(
            _events, left_on="report_date", right_on="annotation_date",
            strategy="backward", tolerance="13d",
        )
        .sort("順位")
        .select(
            "順位", 販売台数="units", 集計末日="report_date",
            直近のイベント=pl.concat_str(
                pl.col("annotation_date").dt.strftime("%Y/%m/%d"), "note", separator="　",
            ).fill_null("—"),
        )
    )
    mo.vstack([
        mo.md("### 週間販売台数ベスト5"),
        mo.md("イベント欄には、集計週とその前週に記録された同機種のイベントのうち、最も新しい日付のものを表示します。"),
        mo.ui.table(best_weeks, selection=None, pagination=False, show_column_summaries=False),
    ])


@app.cell(hide_code=True)
def monthly_overview(alt, g, mo, pl, scope, view):
    from datetime import date as _date

    mo.stop(view.value == "年別比較")
    _start = _date(2000, 1, 1)
    _last_month = scope["report_date"].max().replace(day=1)
    _periods = pl.date_range(_start, _last_month, interval="1mo", eager=True).dt.strftime("%Y-%m").to_list()
    _months = g.monthly_sales(scope, begin=_start).select(
        pl.date("year", "month", 1).dt.strftime("%Y-%m").alias("period"),
        "hw", "monthly_units",
    ).with_columns(total=pl.col("monthly_units").sum().over("period"))
    _hardware = g.get_hw(_months)
    brush = alt.selection_interval(name="months", encodings=["x"])
    _overview = (
        alt.Chart(_months).mark_bar()
        .encode(
            x=alt.X(
                "period:O", title=None, scale=alt.Scale(domain=_periods),
                axis=alt.Axis(labelAngle=-45, labelOverlap=True),
            ),
            y=alt.Y("monthly_units:Q", stack="zero", title="月販（台）"),
            color=alt.Color(
                "hw:N", title="機種",
                scale=alt.Scale(domain=_hardware, range=g.get_hard_colors(_hardware)),
                legend=alt.Legend(columns=2),
            ),
            opacity=alt.condition(brush, alt.value(1), alt.value(0.35)),
            tooltip=[
                alt.Tooltip("period:O", title="集計月"),
                alt.Tooltip("hw:N", title="機種"),
                alt.Tooltip("monthly_units:Q", title="機種別月販", format=","),
                alt.Tooltip("total:Q", title="表示機種の月計", format=","),
            ],
        )
        .add_params(brush)
        .properties(width=max(300, len(_periods) * 18), height=165)
    )
    month_chart = mo.ui.altair_chart(_overview, legend_selection=False)
    if _months.is_empty():
        _body = mo.md("2000年1月以降の対象期間に販売記録がありません。")
    else:
        _body = mo.vstack([
            mo.md("横にスクロールして過去へ移動し、調べたい月をドラッグすると下に週販が表示されます。"),
            mo.vstack([month_chart]).style({"width": "max-content", "direction": "ltr"})
                .style({"max-width": "100%", "overflow-x": "auto", "direction": "rtl"}),
        ])
    mo.vstack([mo.md("### 月間販売台数"), _body])
    return (month_chart,)


@app.cell(hide_code=True)
def weekly_annotation_slider(annotations, mo):
    annotation_level = mo.ui.slider(
        start=0, stop=max(30, annotations["level"].max() or 0), step=1, value=30,
        show_value=True, label="表示する注釈レベルの上限",
    )
    return (annotation_level,)


@app.cell(hide_code=True)
def weekly_detail_window(annotation_level, g, mo, month_chart, pl, scope):
    _selected = month_chart.value
    mo.stop(
        _selected.is_empty() and month_chart.selections.get("months", {}).get("period"),
        mo.md("選択した月に販売記録がありません。"),
    )
    if _selected.is_empty():
        _weeks = scope["report_date"].unique().sort().tail(13)
        _rows = scope.filter(pl.col("report_date").is_in(_weeks.to_list()))
        _label = f"直近{len(_weeks)}週"
    else:
        _months = _selected["period"].to_list()
        _rows = scope.filter(pl.col("report_date").dt.strftime("%Y-%m").is_in(_months))
        _label = " 〜 ".join(dict.fromkeys([min(_months), max(_months)]))

    detail_begin = _rows["report_date"].min()
    detail_end = _rows["report_date"].max()
    detail_hardware = g.get_hw(_rows)
    mo.vstack([mo.md(f"### 週間販売台数　{_label}"), annotation_level])
    return detail_begin, detail_end, detail_hardware


@app.cell(hide_code=True)
def weekly_detail(
    alt,
    annotation_level,
    detail_begin,
    detail_end,
    detail_hardware,
    g,
    mo,
):
    _chart = g.chart_line_sales(
        hw=detail_hardware,
        begin=detail_begin,
        end=detail_end,
        annotation_level=annotation_level.value,
        padding_begin=1,
        padding_end=1,
    )
    # 長期間を選んだときも、描画する列だけをブラウザーに渡す。
    _chart.data = _chart.data.select("hw", "report_date", "begin_date", "units", "note")
    _chart = _chart.encode(tooltip=[
        alt.Tooltip("hw:N", title="機種"),
        alt.Tooltip("begin_date:T", title="集計開始", format="%Y/%m/%d"),
        alt.Tooltip("report_date:T", title="集計末日", format="%Y/%m/%d"),
        alt.Tooltip("units:Q", title="週販", format=","),
        alt.Tooltip("note:N", title="イベント"),
    ]).properties(width="container", height=300, title="機種別の週販推移")
    weekly_chart = mo.ui.altair_chart(_chart, chart_selection=False, legend_selection=False)
    weekly_chart


@app.cell(hide_code=True)
def compare_controls(alt, g, machine_history, mo, view):
    mo.stop(view.value != "年別比較")
    _annual = g.yearly_sales(machine_history).select("year", "yearly_units").sort("year")
    initial_years = _annual["year"].tail(3).to_list()
    _pick = alt.selection_point(
        name="comparison_years", fields=["year"], on="click", toggle="true",
        clear=False, empty=False, value=[{"year": y} for y in initial_years],
    )
    _overview = (
        alt.Chart(_annual).mark_bar(cursor="pointer").encode(
            x=alt.X("year:O", title="年", axis=alt.Axis(labelAngle=0)),
            y=alt.Y("yearly_units:Q", title="年間販売台数（台）"),
            color=alt.condition(_pick, alt.value("#20685f"), alt.value("#b7cfc9")),
            tooltip=[alt.Tooltip("year:O", title="年"),
                     alt.Tooltip("yearly_units:Q", title="年間販売台数", format=",")],
        )
        .add_params(_pick)
        .properties(width="container", height=170)
    )
    year_chart = mo.ui.altair_chart(_overview, chart_selection=False, legend_selection=False)
    grain = mo.ui.radio(["週間", "月間", "四半期", "年間"], value="週間", inline=True, label="集計単位")
    mo.vstack([
        mo.md(f"### {machine_history['full_name'][0]} の年間販売台数"),
        mo.md("棒をクリックして比較する年を追加・解除できます。濃い色の棒が選択中です。"),
        year_chart, grain,
    ])
    return grain, initial_years, year_chart


@app.cell(hide_code=True)
def comparison(
    alt,
    g,
    grain,
    initial_years,
    machine_history,
    mo,
    pl,
    week,
    year_chart,
):
    # 初回描画時は Vega の初期選択を使い、操作後は空の選択もそのまま反映する。
    _years = year_chart.value["year"].to_list() if "comparison_years" in year_chart.selections else initial_years
    mo.stop(not _years, mo.md("上の棒グラフから比較する年を選んでください。"))
    _rows = machine_history.filter(pl.col("year").is_in(_years))
    _grain = grain.value
    _axis_title = {"週間": "年初からの週", "月間": "月", "四半期": "四半期", "年間": "年"}[_grain]
    if _grain == "週間":
        # 集計末日が1月1〜7日なら第1週。暦年の外にある日は持ち込まない。
        _data = _rows.select("year", "units", "report_date",
                             slot=((pl.col("yday") - 1) // 7 + 1))
    elif _grain == "月間":
        _data = g.monthly_sales(_rows).select("year", slot="month", units="monthly_units")
    elif _grain == "四半期":
        _data = g.quarterly_sales(_rows).select("year", slot="q_num", units="quarterly_units")
    else:
        _data = g.yearly_sales(_rows).select("year", slot="year", units="yearly_units")
    _tooltips = [alt.Tooltip("year:O", title="年"), alt.Tooltip("units:Q", title="販売台数", format=",")]
    _y = alt.Y("units:Q", title="販売台数（台）")
    _color = alt.Color("year:N", title="年", sort="ascending")
    if _grain in ("週間", "月間"):
        _data = _data.sort(["year", "slot"]).with_columns(
            segment=(pl.col("slot").diff().over("year").fill_null(1) != 1).cum_sum().over("year")
        )
        _max_slot = 53 if _grain == "週間" else 12
        _tooltips.append(alt.Tooltip("slot:Q", title=_axis_title))
        if _grain == "週間":
            _tooltips.append(alt.Tooltip("report_date:T", title="集計末日", format="%Y/%m/%d"))
        _chart = alt.Chart(_data).mark_line(point=True).encode(
            x=alt.X("slot:Q", title=_axis_title, scale=alt.Scale(domain=[1, _max_slot]),
                    axis=alt.Axis(tickMinStep=1)),
            y=_y, color=_color, detail="segment:N", order="slot:Q", tooltip=_tooltips,
        )
    elif _grain == "四半期":
        _chart = alt.Chart(_data).mark_bar().encode(
            x=alt.X("slot:O", title="四半期", scale=alt.Scale(domain=[1, 2, 3, 4])),
            xOffset="year:N", y=_y, color=_color,
            tooltip=[*_tooltips, alt.Tooltip("slot:O", title="四半期")],
        )
    else:
        _chart = alt.Chart(_data).mark_bar(color="#20685f").encode(
            x=alt.X("slot:O", title="年"), y=_y, tooltip=_tooltips,
        )
    comparison_chart = mo.ui.altair_chart(
        _chart.properties(width="container", height=320), chart_selection=False, legend_selection=False,
    )
    mo.vstack([mo.md(f"### {_rows['full_name'][0]} の{_grain}販売台数"),
               comparison_chart, mo.md(f"集計末日を基準に暦年で集計。{week.value:%Y/%m/%d} までの記録を表示しています。")])


if __name__ == "__main__":
    app.run()
