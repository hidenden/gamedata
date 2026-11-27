# /// script
# requires-python = ">=3.11"
# [tool.marimo.display]
# theme = "system"
# ///

import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium")

with app.setup:
    # 標準ライブラリ
    from datetime import date, datetime
    from pathlib import Path
    import sys

    # サードパーティライブラリ
    import marimo as mo
    import altair as alt
    import polars as pl
    # import polars.selectors as cs

    import scipy as sp
    import statsmodels.api as sm
    import holidays as holidays
    import ruptures as rpt
    import vl_convert as vlc

    # プロジェクト内モジュール
    import gamedata as g


@app.cell
def load_db():
    hard_sales_all_df: pl.DataFrame = g.load_hard_sales(True)
    annotation_all_df: pl.DataFrame = g.load_hard_annotation(no_cache=True)
    return (hard_sales_all_df,)


@app.cell(hide_code=True)
def md_prologue():
    mo.md(r"""
    # ゲームハードウェア分析 notebook

    - このnotebookは日本国内のゲームハードウェア販売状況をデータから分析するものです｡
    - ハードウェアの販売データは hard_sales_all_df に格納されています。これは毎週の各ハードウェアの販売台数が格納されています｡
    - 注釈データは annotation_all_df に格納されています。これはゲーム関係のイベントと日付が格納されています｡売上の変化に影響を与える要因として利用してください｡
    - データ分析時には､出来るだけ import済みの gamedataライブラリを使用して下さい｡
    - gamedataライブラリで不足する場合は､新たな関数を実装して分析と可視化を行って下さい。
    - 新たな関数が将来の分析でも使える汎用性を持つと判断される場合には､出来るだけ汎用な形式で関数化を試み､その旨を報告して下さい｡
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## 開発者用メモ

    marimo起動方法

    ```shell
    uv run marimo edit --no-token --no-sandbox <notebook_file_path>
    ```

    marimo-pair接続プロンプト

    ```text
    marimo-pair http://localhost:2718 の既存セッションで､以下に示すnotebookとpairしてください。
    新しいmarimoサーバーは起動しないでください。
    sandbox内から接続できない場合は、接続スクリプトをsandbox外で実行してください。

    notebook名:
    ```
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## AIへの指示

    分析前に `from gamedata import catalog` を実行し、`catalog.overview()` を参照してください。
    販売データは `hard_sales_all_df`、注釈データは `annotation_all_df` にあります。
    `catalog.inspect_frame(hard_sales_all_df, dataset="hard_sales")` で実際の収録範囲を確認し、
    `catalog.search()` と `catalog.describe()` で分析に使う既存関数と列の意味を確認してください。
    """)
    return


@app.cell(hide_code=True)
def forecast_notes():
    mo.md(r"""
    ## 年末の年間販売台数予測

    `units` の当年累計を、次の独立した仮定で12月31日時点の年間販売台数へ外挿します。

    1. **直近52週ランレート**: 直近52週の販売台数を収録日数で割った日次ペースが年末まで続く。
    2. **メーカー別四半期構成比**: 過去5年のメーカー別・四半期別年間構成比（中央値）が今年も続く。進行中の四半期は経過日数で按分する。
    3. **前年季節ナイーブ**: 前年の同日以降の販売パターンが続く。ただし当年/前年YTD比（0.25〜4倍）で水準を補正する。
    4. **中央値アンサンブル**: 利用できる各モデルの中央値。単一モデルの極端な予測の影響を抑える。

    新発売ハードは前年値がないため「前年季節ナイーブ」が欠損します。四半期モデルはハード固有でなくメーカー全体の季節性を利用するため、発売時期や世代交代などの構造変化は別途考慮が必要です。
    """)
    return


@app.cell
def forecast_functions():
    from importlib import reload as _reload
    import gamedata.forecast as _forecast

    _reload(_forecast)
    forecast_year_end_all = _forecast.forecast_year_end_all
    return (forecast_year_end_all,)


@app.cell
def forecast_results(forecast_year_end_all, hard_sales_all_df: pl.DataFrame):
    year_end_forecasts_df = forecast_year_end_all(hard_sales_all_df, hw=['NS2', 'PS5'])
    mo.vstack([
        mo.md(f"### 予測基準日: {year_end_forecasts_df['as_of'][0]}") ,
        mo.ui.table(year_end_forecasts_df),
    ])
    return


@app.cell(hide_code=True)
def backtest_notes():
    mo.md(r"""
    ## 過去10年の8月末時点バックテスト

    2016〜2025年の各年について、その年の8月に収録された最終週までしか分からない状態を再現し、年末の**年間販売台数**を予測します。その後、同年の年末実績と比較します。

    - 主指標は **WAPE**（絶対誤差合計 ÷ 実績合計）。販売規模を加味し、小規模機種によるMAPEの暴騰を抑えます。
    - **MAE** は1機種・1年あたり平均で何台外したかを示します。
    - **中央値APE** は典型的な相対誤差、**bias_pct** は過大・過小予測の方向を示します。
    - メーカー、発売後年数（0〜2年／3〜5年／6年以上）、8月末YTD販売規模で層別します。
    - 年末累計台数も保存しますが、モデルの直接の予測対象に合わせ、精度指標は年間販売台数で計算します。

    層別結果はサンプル数が少ない場合があるため、`observations` と `hardware_count` を必ず併読します。
    """)
    return


@app.cell
def backtest_functions(forecast_year_end_all):
    def backtest_year_end_models(
        sales_df: pl.DataFrame,
        years: int = 10,
        cutoff_month: int = 8,
        hw: list[str] = [],
    ) -> pl.DataFrame:
        """過去の月末時点へ巻き戻し、各年末予測モデルを時系列バックテストする。

        Args:
            sales_df: `g.load_hard_sales()` と同じ形式の週次販売データ。
            years: 評価対象とする直近の完了年数。既定値は10年。
            cutoff_month: 各年の予測基準月。月内の最終 `report_date` を使う。
                既定値は8月。
            hw: 評価対象のハードウェア識別子。空リストは全ハード。

        Returns:
            年・ハード・モデルごとの予測値、年末実績、誤差、発売後年数、
            メーカー、YTD販売規模を持つPolars DataFrame。

        Raises:
            ValueError: 条件を満たす完了年または予測結果が存在しない場合。

        Notes:
            完了年は12月の販売レコードが存在する年と定義する。各年の対象は
            カットオフ当日に販売レコードがあるハードに限定する。モデルには
            カットオフ以降の販売実績を渡さず、年末実績は評価時だけ結合する。
            `forecast_error_units` は「予測−実績」で、正は過大予測を表す。
        """
        if years <= 0:
            raise ValueError("yearsは1以上を指定してください")
        if not 1 <= cutoff_month <= 12:
            raise ValueError("cutoff_monthは1〜12を指定してください")

        _complete_years = (
            sales_df.group_by("year")
            .agg(
                pl.col("report_date").max().alias("last_report_date"),
                pl.col("month").unique().alias("observed_months"),
            )
            .filter(
                pl.col("observed_months").list.contains(12)
                & pl.col("observed_months").list.contains(cutoff_month)
            )
            .sort("year", descending=True)
            .head(years)["year"]
            .sort()
            .to_list()
        )
        if not _complete_years:
            raise ValueError("バックテスト可能な完了年がありません")

        _rows = []
        for _year in _complete_years:
            _cutoff = sales_df.filter(
                (pl.col("year") == _year) & (pl.col("month") == cutoff_month)
            ).select(pl.col("report_date").max()).item()
            _cutoff_hw = sales_df.filter(
                pl.col("report_date") == _cutoff
            )["hw"].unique().to_list()
            _target_hw = [
                _hw for _hw in _cutoff_hw if not hw or _hw in hw
            ]
            _forecast = forecast_year_end_all(sales_df, as_of=_cutoff, hw=_target_hw)
            _actual = (
                sales_df.filter(pl.col("year") == _year)
                .group_by("hw")
                .agg(
                    pl.col("units").sum().alias("actual_year_units"),
                    pl.col("launch_date").first().alias("launch_date"),
                    pl.col("full_name").first().alias("full_name"),
                )
            )
            _actual_cumulative = (
                sales_df.filter(pl.col("year") == _year)
                .sort("report_date")
                .group_by("hw")
                .agg(pl.col("sum_units").last().alias("actual_year_end_cumulative_units"))
            )
            _evaluated = (
                _forecast.join(_actual, on="hw", how="inner")
                .join(_actual_cumulative, on="hw", how="left")
                .with_columns(
                    pl.lit(_year).cast(pl.Int16).alias("year"),
                    (pl.col("forecast_year_units") - pl.col("actual_year_units"))
                    .alias("forecast_error_units"),
                    (pl.col("forecast_cumulative_units") - pl.col("actual_year_end_cumulative_units"))
                    .alias("cumulative_error_units"),
                    ((pl.col("as_of") - pl.col("launch_date")).dt.total_days() / 365.25)
                    .floor().cast(pl.Int16).alias("launch_age_years"),
                )
                .with_columns(
                    pl.col("forecast_error_units").abs().alias("absolute_error_units"),
                    pl.when(pl.col("actual_year_units") > 0)
                    .then(pl.col("forecast_error_units").abs() / pl.col("actual_year_units"))
                    .otherwise(None).alias("absolute_percentage_error"),
                    pl.when(pl.col("launch_age_years") < 3).then(pl.lit("0-2年"))
                    .when(pl.col("launch_age_years") < 6).then(pl.lit("3-5年"))
                    .otherwise(pl.lit("6年以上")).alias("lifecycle_stage"),
                    pl.when(pl.col("actual_ytd_units") < 100_000).then(pl.lit("10万台未満"))
                    .when(pl.col("actual_ytd_units") < 500_000).then(pl.lit("10-50万台"))
                    .otherwise(pl.lit("50万台以上")).alias("ytd_volume_band"),
                )
            )
            _rows.append(_evaluated)

        if not _rows:
            raise ValueError("予測結果を作成できませんでした")
        return pl.concat(_rows, how="vertical_relaxed").sort(["year", "hw", "model"])


    def summarize_forecast_accuracy(
        backtest_df: pl.DataFrame,
        by: list[str] = [],
    ) -> pl.DataFrame:
        """バックテスト結果をモデル別に集約し、予測精度指標を計算する。

        Args:
            backtest_df: `backtest_year_end_models()` の返却DataFrame。
            by: モデル以外の集約軸。例: `["maker_name"]`、
                `["lifecycle_stage"]`。空リストはモデル全体で集約する。

        Returns:
            観測数、対象機種数・年数、MAE、RMSE、MAPE、中央値APE、WAPE、
            平均バイアスと総販売台数比バイアスを持つPolars DataFrame。

        Notes:
            `wape_pct` は全絶対誤差÷全実績で、販売規模を加味した主指標。
            `bias_pct` は正なら過大予測、負なら過小予測の傾向を表す。
            少数サンプルのグループは偶然の影響が大きいため、`observations`
            と `hardware_count` を併せて確認すること。
        """
        _group_columns = [*by, "model"]
        return (
            backtest_df.filter(
                pl.col("forecast_year_units").is_not_null()
                & pl.col("actual_year_units").is_not_null()
            )
            .group_by(_group_columns)
            .agg(
                pl.len().alias("observations"),
                pl.col("hw").n_unique().alias("hardware_count"),
                pl.col("year").n_unique().alias("year_count"),
                pl.col("absolute_error_units").mean().round(0).cast(pl.Int64).alias("mae_units"),
                pl.col("absolute_error_units").median().round(0).cast(pl.Int64).alias("median_ae_units"),
                (pl.col("forecast_error_units").pow(2).mean().sqrt()).round(0).cast(pl.Int64).alias("rmse_units"),
                (pl.col("absolute_percentage_error").mean() * 100).round(1).alias("mape_pct"),
                (pl.col("absolute_percentage_error").median() * 100).round(1).alias("median_ape_pct"),
                (pl.col("absolute_error_units").sum() / pl.col("actual_year_units").sum() * 100).round(1).alias("wape_pct"),
                pl.col("forecast_error_units").mean().round(0).cast(pl.Int64).alias("bias_units"),
                (pl.col("forecast_error_units").sum() / pl.col("actual_year_units").sum() * 100).round(1).alias("bias_pct"),
            )
            .sort([*by, "wape_pct"])
        )


    def select_best_forecast_models(
        accuracy_df: pl.DataFrame,
        by: list[str] = [],
        metric: str = "wape_pct",
        min_observations: int = 3,
    ) -> pl.DataFrame:
        """精度集計からグループごとに最良スコアのモデルを選ぶ。

        Args:
            accuracy_df: `summarize_forecast_accuracy()` の返却DataFrame。
            by: 選択単位の列。例: `["maker_name"]`。空なら全体で1モデル。
            metric: 小さいほど良い評価指標の列名。既定値は `wape_pct`。
            min_observations: 採用に必要な最小観測数。既定値は3。

        Returns:
            指定条件を満たし、各グループで評価指標が最小のモデル。
        """
        if metric not in accuracy_df.columns:
            raise ValueError(f"評価指標が存在しません: {metric}")
        _eligible = accuracy_df.filter(pl.col("observations") >= min_observations)
        if not by:
            return _eligible.sort(metric).head(1)
        return _eligible.sort([*by, metric]).group_by(by, maintain_order=True).first()


    return (
        backtest_year_end_models,
        select_best_forecast_models,
        summarize_forecast_accuracy,
    )


@app.cell
def backtest_results(
    backtest_year_end_models,
    hard_sales_all_df: pl.DataFrame,
    select_best_forecast_models,
    summarize_forecast_accuracy,
):
    forecast_backtest_df = backtest_year_end_models(hard_sales_all_df, years=10, cutoff_month=8)
    accuracy_overall_df = summarize_forecast_accuracy(forecast_backtest_df)
    accuracy_by_maker_df = summarize_forecast_accuracy(forecast_backtest_df, by=["maker_name"])
    accuracy_by_lifecycle_df = summarize_forecast_accuracy(forecast_backtest_df, by=["lifecycle_stage"])
    accuracy_by_volume_df = summarize_forecast_accuracy(forecast_backtest_df, by=["ytd_volume_band"])
    accuracy_by_maker_lifecycle_df = summarize_forecast_accuracy(
        forecast_backtest_df,
        by=["maker_name", "lifecycle_stage"],
    )
    best_overall_df = select_best_forecast_models(accuracy_overall_df)
    best_by_maker_df = select_best_forecast_models(accuracy_by_maker_df, by=["maker_name"], min_observations=3)
    best_by_lifecycle_df = select_best_forecast_models(accuracy_by_lifecycle_df, by=["lifecycle_stage"], min_observations=3)
    best_by_volume_df = select_best_forecast_models(accuracy_by_volume_df, by=["ytd_volume_band"], min_observations=3)

    mo.vstack([
        mo.md("### 全体精度"),
        mo.ui.table(accuracy_overall_df),
        mo.md("### メーカー別の推奨モデル"),
        mo.ui.table(best_by_maker_df),
        mo.md("### 発売後年数別の推奨モデル"),
        mo.ui.table(best_by_lifecycle_df),
        mo.md("### 8月末YTD販売規模別の推奨モデル"),
        mo.ui.table(best_by_volume_df),
        mo.accordion({
            "メーカー別・全モデル": mo.ui.table(accuracy_by_maker_df),
            "発売後年数別・全モデル": mo.ui.table(accuracy_by_lifecycle_df),
            "販売規模別・全モデル": mo.ui.table(accuracy_by_volume_df),
            "メーカー×発売後年数": mo.ui.table(accuracy_by_maker_lifecycle_df),
            "全バックテスト明細": mo.ui.table(forecast_backtest_df),
        }),
    ])
    return


@app.cell(hide_code=True)
def backtest_findings():
    mo.md(r"""
    ## バックテストから得られた示唆

    ### 全体

    - **直近52週ランレート**がWAPE **12.4%**で最良。バイアスは**-2.0%**で、全体として過大・過小の偏りも小さい。
    - **中央値アンサンブル**はWAPE **12.7%**でほぼ同等。中央値APEは17.9%で52週方式の19.6%より良く、典型的なケースでは安定する一方、販売規模を加味した総誤差ではわずかに劣る。
    - メーカー四半期構成比はWAPE 15.9%、前年季節ナイーブは17.0%。両者とも全体では過大予測傾向がある。

    ### 使い分けの候補

    - **Microsoft**: 52週方式がWAPE 7.4%で明確に優位。
    - **SONY**: 52週方式がWAPE 11.0%で最良。ただし発売3〜5年ではメーカー四半期方式5.6%、アンサンブル5.7%、52週6.1%と僅差。
    - **Nintendo**: アンサンブル12.8%と52週方式約13%がほぼ同等。単一方式を固定する根拠は弱く、アンサンブルが無難。
    - **発売0〜2年**: 前年実績が存在する場合は前年季節方式がWAPE 11.1%で最良。ただし9観測・5機種であり、発売初年には前年値がないため利用不能。
    - **発売3〜5年**: 52週方式がWAPE 6.4%、バイアス-0.3%で最も安定。
    - **発売6年以上**: 52週方式がWAPE 12.1%で最良だが、中央値APEは23.3%。販売規模縮小期の個別予測は難しい。
    - **8月末YTD 50万台以上**: 52週方式がWAPE 11.5%で安定。
    - **50万台未満**: 最良方式でもWAPE 23.9〜25.5%。方式選択より、予測レンジを広く取ることが重要。

    ### 暫定的な採用ルール

    1. 基本方式は直近52週ランレート。
    2. Nintendoは中央値アンサンブルも併記する。
    3. 発売後3年未満で前年実績が十分ある場合は前年季節方式を候補にする。
    4. SONYの発売3〜5年はメーカー四半期方式・52週方式・アンサンブルを併記する。
    5. 低販売規模、発売初年、世代交代、供給制約、値下げ、外的ショックの年は点予測だけで判断しない。

    2020年Nintendo Switchの前年季節方式には約276万台の過大予測があり、急激な需要変化を前年パターンで増幅する弱点が確認された。現状は10年・9機種と標本が小さいため、このルールは確定版ではなく、データ更新後に再評価する。
    """)
    return


if __name__ == "__main__":
    app.run()
