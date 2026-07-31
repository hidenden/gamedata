# /// script
# [tool.marimo.display]
# theme = "system"
# ///

import marimo

__generated_with = "0.23.14"
app = marimo.App(width="medium")

with app.setup:
    # 標準ライブラリ
    from datetime import date, datetime

    import marimo as mo
    import altair as alt

    # サードパーティライブラリ
    import polars as pl

    # import polars.selectors as cs
    # プロジェクト内モジュール
    import gamedata as g

    # レポート日付
    # from report_config import get_config


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    # PS5とSwitch2の累計逆転予測
    """)
    return


@app.cell
def load_hard_sales():
    df_all = g.load_hard_sales()
    return (df_all,)


@app.cell
def forecast_ps5_switch2(df_all):
    from datetime import timedelta
    import math

    # PS5とSwitch 2の最新累計をgamedataの抽出APIで取得する。
    _latest_pair = g.extract_total(
        df_all.filter(pl.col("hw").is_in(["PS5", "NS2"])),
        compact=True,
    )
    _latest_map = {_row["hw"]: _row for _row in _latest_pair.iter_rows(named=True)}
    _forecast_start = max(_row["report_date"] for _row in _latest_map.values())
    _current_gap = _latest_map["PS5"]["sum_units"] - _latest_map["NS2"]["sum_units"]

    # 観測窓を変えて、発売期を含む強気・半年平均・足元4週の弱気を表現する。
    _scenario_windows = [("最短", 52), ("真ん中", 26), ("最長", 4)]
    _basis_rows = []
    _forecast_rows = []
    _crossover_rows = []
    _series_rows = []

    for _scenario, _window in _scenario_windows:
        _ns2_sales = df_all.filter(pl.col("hw") == "NS2").sort("report_date").tail(_window)
        _ps5_sales = df_all.filter(pl.col("hw") == "PS5").sort("report_date").tail(_window)
        _ns2_weekly = _ns2_sales["units"].mean()
        _ps5_weekly = _ps5_sales["units"].mean()
        _net_weekly = _ns2_weekly - _ps5_weekly
        _weeks_to_cross = math.ceil(_current_gap / _net_weekly)
        _cross_date = _forecast_start + timedelta(weeks=_weeks_to_cross)

        _basis_rows.append(
            {
                "シナリオ": _scenario,
                "観測期間": f"直近{_window}週",
                "Switch 2週平均": round(_ns2_weekly),
                "PS5週平均": round(_ps5_weekly),
                "週あたり差縮小": round(_net_weekly),
            }
        )
        _forecast_rows.append(
            {
                "シナリオ": _scenario,
                "Switch 2 今後52週": round(_ns2_weekly * 52),
                "PS5 今後52週": round(_ps5_weekly * 52),
                "Switch 2 52週後累計": round(_latest_map["NS2"]["sum_units"] + _ns2_weekly * 52),
                "PS5 52週後累計": round(_latest_map["PS5"]["sum_units"] + _ps5_weekly * 52),
            }
        )
        _crossover_rows.append(
            {
                "シナリオ": _scenario,
                "追越しまで": f"{_weeks_to_cross}週",
                "推測時期": _cross_date,
                "Switch 2推定累計": round(_latest_map["NS2"]["sum_units"] + _ns2_weekly * _weeks_to_cross),
                "PS5推定累計": round(_latest_map["PS5"]["sum_units"] + _ps5_weekly * _weeks_to_cross),
            }
        )

        # 最新時点から104週先まで、一定週平均を置いた累計予測系列を作る。
        for _week in range(105):
            _forecast_date = _forecast_start + timedelta(weeks=_week)
            _series_rows.extend(
                [
                    {
                        "シナリオ": _scenario,
                        "集計日": _forecast_date,
                        "ハード": "Switch 2",
                        "累計台数": round(_latest_map["NS2"]["sum_units"] + _ns2_weekly * _week),
                    },
                    {
                        "シナリオ": _scenario,
                        "集計日": _forecast_date,
                        "ハード": "PS5",
                        "累計台数": round(_latest_map["PS5"]["sum_units"] + _ps5_weekly * _week),
                    },
                ]
            )

    forecast_basis = pl.DataFrame(_basis_rows)
    forecast_values = pl.DataFrame(_forecast_rows)
    crossover_estimates = pl.DataFrame(_crossover_rows)
    forecast_series = pl.DataFrame(_series_rows)

    # 初代Switchとの発売後同時期比較を補助根拠として集計する。
    _aligned_sales = g.sales_by_delta_long(df_all, mode="week", hw=["NS2", "NSW"])
    _ns2_last_delta = _aligned_sales.filter(pl.col("hw") == "NS2")["delta_week"].max()
    _analog_rows = []
    for _window in [4, 26, 52]:
        _same_age = (
            _aligned_sales
            .filter(pl.col("delta_week").is_between(_ns2_last_delta - _window + 1, _ns2_last_delta))
            .group_by("hw")
            .agg(pl.sum("units").alias("units"))
        )
        _same_age_map = dict(_same_age.iter_rows())
        _analog_rows.append(
            {
                "観測期間": f"同経過週の直近{_window}週",
                "Switch 2": _same_age_map["NS2"],
                "初代Switch": _same_age_map["NSW"],
                "Switch 2 / 初代Switch": _same_age_map["NS2"] / _same_age_map["NSW"],
            }
        )
    switch_analog = pl.DataFrame(_analog_rows)

    # PS5の直近52週とその前52週を比較し、成熟期の減速を確認する。
    _ps5_all = df_all.filter(pl.col("hw") == "PS5").sort("report_date")
    _ps5_last_52 = _ps5_all.tail(52)["units"].sum()
    _ps5_prev_52 = _ps5_all.slice(_ps5_all.height - 104, 52)["units"].sum()
    ps5_yearly_trend = pl.DataFrame(
        {
            "期間": ["前52週", "直近52週"],
            "販売台数": [_ps5_prev_52, _ps5_last_52],
            "直近 / 前期": [1.0, _ps5_last_52 / _ps5_prev_52],
        }
    )
    return (
        crossover_estimates,
        forecast_basis,
        forecast_series,
        forecast_values,
        ps5_yearly_trend,
        switch_analog,
    )


@app.cell
def display_ps5_switch2_forecast(
    crossover_estimates,
    forecast_basis,
    forecast_values,
    ps5_yearly_trend,
    switch_analog,
):
    # 予測値と追越し時期を、前提と補助根拠を添えて表示する。
    _short = crossover_estimates.filter(pl.col("シナリオ") == "最短").row(0, named=True)
    _mid = crossover_estimates.filter(pl.col("シナリオ") == "真ん中").row(0, named=True)
    _long = crossover_estimates.filter(pl.col("シナリオ") == "最長").row(0, named=True)
    _ps5_decline = 1 - ps5_yearly_trend.filter(pl.col("期間") == "直近52週")["直近 / 前期"].item()

    mo.vstack(
        [
            mo.md(
                f"""
    ## PS5とSwitch 2の累計逆転予測

    基準日は **2026年7月12日**。累計はPS5が **7,641,444台**、Switch 2が
    **6,026,931台**で、差は **1,614,513台**です。

    - **最短:** {_short['推測時期']:%Y年%m月%d日}ごろ（{_short['追越しまで']}）
    - **真ん中:** {_mid['推測時期']:%Y年%m月%d日}ごろ（{_mid['追越しまで']}）
    - **最長:** {_long['推測時期']:%Y年%m月%d日}ごろ（{_long['追越しまで']}）

    各シナリオは観測期間中の週平均が今後も続く単純投影です。最短は発売期と年末商戦を
    含む直近52週、真ん中は直近半年に相当する26週、最長は足元の低い販売水準を表す4週を使います。
    季節性、値下げ、供給制約、強力なソフト発売は明示的にはモデル化していないため、点予測ではなく
    幅として解釈してください。
                """
            ),
            mo.md("### シナリオの週平均前提"),
            mo.ui.table(forecast_basis, selection=None, pagination=False),
            mo.md("### 今後52週間の販売予測"),
            mo.ui.table(forecast_values, selection=None, pagination=False),
            mo.md("### 累計を追い越す推測時期"),
            mo.ui.table(crossover_estimates, selection=None, pagination=False),
            mo.md(
                f"""
    ### 根拠と注意点

    - Switch 2は、発売後の同じ経過週で初代Switchと比べると、直近52週では
      **{switch_analog.filter(pl.col('観測期間') == '同経過週の直近52週')['Switch 2 / 初代Switch'].item():.2f}倍**、
      直近26週では **{switch_analog.filter(pl.col('観測期間') == '同経過週の直近26週')['Switch 2 / 初代Switch'].item():.2f}倍**です。
      一方、直近4週は **{switch_analog.filter(pl.col('観測期間') == '同経過週の直近4週')['Switch 2 / 初代Switch'].item():.2f}倍**まで低下しています。
      そのため、52週・26週・4週の3窓は上振れ・中心・下振れの幅を表す材料になります。
    - PS5の直近52週販売は **{_ps5_decline:.1%}減**（715,274台、前52週は1,110,779台）です。
      本予測ではこの減速をさらに織り込まず、各窓の週平均を横ばいに置いています。
      したがってPS5側についてはやや保守的で、実際に減速が続けば逆転は表より早まります。
    - 最短ケースはSwitch 2の発売初期を含む高い平均を維持する前提なので、実現には年末商戦、供給、
      ソフトラインアップの強さが必要です。最長ケースは年末商戦の反発を無視するため、下限寄りの試算です。
                """
            ),
            mo.md("### 初代Switchとの同経過週比較"),
            mo.ui.table(switch_analog, selection=None, pagination=False),
            mo.md("### PS5の52週販売トレンド"),
            mo.ui.table(ps5_yearly_trend, selection=None, pagination=False),
        ]
    )
    return


@app.cell
def chart_ps5_switch2_forecast(forecast_series):
    # gamedataの機種カラーを使い、3シナリオの累計推移を比較する。
    _forecast_chart_data = forecast_series.with_columns(
        (pl.col("累計台数") / 1_000_000).alias("累計台数（百万台）")
    )
    _forecast_chart = (
        alt.Chart(_forecast_chart_data)
        .mark_line(strokeWidth=2.5)
        .encode(
            x=alt.X("集計日:T", title="集計日"),
            y=alt.Y("累計台数（百万台）:Q", title="累計台数（百万台）", scale=alt.Scale(zero=False)),
            color=alt.Color(
                "ハード:N",
                title="ハード",
                scale=alt.Scale(domain=["PS5", "Switch 2"], range=g.get_hard_colors(["PS5", "NS2"])),
            ),
            tooltip=["シナリオ:N", "集計日:T", "ハード:N", alt.Tooltip("累計台数:Q", format=",")],
        )
        .properties(width=700, height=170)
        .facet(row=alt.Row("シナリオ:N", title=None, sort=["最短", "真ん中", "最長"]))
        .resolve_scale(y="independent")
    )

    mo.vstack([mo.md("### シナリオ別の累計予測曲線"), _forecast_chart])
    return


if __name__ == "__main__":
    app.run()
