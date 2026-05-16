# /// script
# [tool.marimo.display]
# theme = "system"
# ///

import marimo

__generated_with = "0.23.6"
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


@app.cell
def _():
    df_all = g.load_hard_sales()
    return (df_all,)


@app.cell
def _(df_all):
    _cmplist = [("PS5", "PS4"), ("PS5", "PS3")]

    pase_df = sales_pase_diffs_long(df_all, cmplist=_cmplist)
    pase_df
    return


@app.cell
def _():
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## sales_pase_diffs_longのシグネチャ

    ```python
    def sales_pase_diffs_long(df: pl.DataFrame,
                          cmplist: list[tuple[str, str]]) -> pl.DataFrame:

        "\"\"
        複数のハードウェア間の相対累計販売台数の差分を計算してDataFrameで返す。

        Args:
            df: load_hard_sales()で取得したDataFrame
            cmplist: 比較するハードウェアのペアのリスト。各タプルは(hw_new, hw_old)の形式で、
                     ハードウェアシンボルのペアを指定する。
                     例えば[("PS5", "PS4"), ("PS5", "PS3")]のように指定する。
                     hw_newの累計販売台数からhw_oldの累計販売台数を引いた差分を計算する。
                     これにより、PS5とPS4の差分、PS5とPS3の差分が計算され､PS5がPS4,
                     PS3と比べて､どの程度早く(あるいは遅く)普及しているかの経緯をを分析できる。

        Returns:
            pl.DataFrame: 各ペアの差分を列として持つDataFrame

    ```
    ## sales_pase_diffs_long()の出力テーブルの構造案

    - index_week: int: 週番号(1から始まる)
    - hw_old: str : 比較対象となる古いマシン
    - hw_new: str : 普及状況を分析したいマシン
    - pair_name: str : PS4_NSW差, PS5_NS2差の様な､比較対象を示す文字列
    - pase_diff : int: hw_oldとhw_newの同じ相対週での累計差分値
    - sum_units_old: int: hw_oldの累計値
    - sum_units_new: int: hw_newの累計値
    - report_date_new: datetime: hw_newのreport_date
    - report_date_old: datetime: hw_oldのreport_date

    ## 出力テーブル構成ロジック

    - cmplistの各ペアについて､上記の形式のdataframeを作成する｡
    - それぞれのdataframeを concatする｡
    - index_weekでソートして､最終的な出力テーブルとする｡

    ## 各ペアのdataframe構成ロジック

    - df_allから､hw_oldとhw_newのデータをそれぞれ別々のdataframeとして抽出する｡
    - カラム名を変更する
        - old側: hw:hw_old, report_date:report_date_old, sum_units: sum_units_old
        - new側: hw:hw_new, report_date:report_date_new, sum_units: sum_units_new
    - 週番号(index_week)を基準をjoinする｡hw_oldを左､hw_newを右にして､週番号で結合する｡
    - selectで必要なカラムを抽出する｡
        - index_week, hw_old, hw_new, report_date_old, report_date_new, sum_units_old, sum_units_new
    - 結合後､pase_diffを計算する｡ sum_units_new - sum_units_old = pase_diff
    - index_weekでソートする
    - pair_nameを作成する｡ f"{hw_new}_{hw_old}差"
    """)
    return


@app.function
def sales_pase_diffs_long(df: pl.DataFrame,
                      cmplist: list[tuple[str, str]]) -> pl.DataFrame:
    """
    複数のハードウェア間の累計販売台数の差分を計算してDataFrameで返す。

    Args:
        df: load_hard_sales()で取得したDataFrame
        cmplist: 比較するハードウェアのペアのリスト。各タプルは(hw_new, hw_old)の形式で、
                 ハードウェアシンボルのペアを指定する。
                例えば[("PS5", "PS4"), ("PS5", "PS3")]のように指定する。
                 hw_newの累計販売台数からhw_oldの累計販売台数を引いた差分を計算する。
                 これにより、PS5とPS4の差分、PS5とPS3の差分が計算され､PS5がPS4,
                 PS3と比べて､どの程度早く(あるいは遅く)普及しているかの経緯をを分析できる。

    Returns:
        pl.DataFrame: 各ペアの差分を列として持つDataFrame
    """
    dfs = []

    def filter_hw_and_rename(df, hw, role):
        return df.filter(pl.col("hw") == hw).select([
            "hw",
            "index_week", 
            "report_date",
            "sum_units"
        ]).rename({
            "hw": f"hw_{role}",
            "report_date": f"report_date_{role}",
            "sum_units": f"sum_units_{role}"
        })

    for hw_new, hw_old in cmplist:
        # old側のデータを抽出
        df_old = filter_hw_and_rename(df, hw_old, "old")       
        # new側のデータを抽出
        df_new = filter_hw_and_rename(df, hw_new, "new")

        # index_weekで結合（old左、new右）
        df_pair = df_old.join(df_new, on="index_week", how="inner")

        # pase_diffを計算
        df_pair = df_pair.with_columns([
            (pl.col("sum_units_new") - pl.col("sum_units_old")).alias("pase_diff")
        ])
        df_pair = df_pair.sort("index_week")

        # pair_nameを作成
        df_pair = df_pair.with_columns(
            pl.concat_str([
                pl.col("hw_new"),
                pl.lit("_"),
                pl.col("hw_old"),
                pl.lit("差")
            ]).alias("pair_name")
        )

        # カラムを再配置
        df_pair = df_pair.select([
            "index_week",
            "hw_new",
            "hw_old",
            "pair_name",
            "pase_diff",
            "sum_units_new",
            "sum_units_old",
            "report_date_new",
            "report_date_old"
        ])

        dfs.append(df_pair)

    # すべてのペアのdataframeを結合
    result = pl.concat(dfs)

    # index_weekでソート
    result = result.sort("index_week")

    return result


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## cumsum_diffs_longのシグネチャ

    ```python
    def cumsum_diffs_long(df: pl.DataFrame,
                          cmplist: list[tuple[str, str]],
                          include_comeback: bool = False) -> pl.DataFrame:

        "\"\"
        複数のハードウェア間の(カレンダー上の)同時期の累計販売台数の差分を計算してDataFrameで返す。

        Args:
            df: load_hard_sales()で取得したDataFrame
            cmplist: 比較するハードウェアのペアのリスト。各タプルは(hw_new, hw_old)の形式で、
                     ハードウェアシンボルのペアを指定する。
                     例えば[("NS2", "PS5"), ("NSW", "PS4")]のように指定する。
                     hw_oldの累計販売台数からhw_newの累計販売台数を引いた差分を計算する。
                     これにより、PS5とNS2の差分、PS4とNSWの差分が計算され､
                     NS2がPS5に､NSWがPS4に追いつく様子を分析できる。
            include_comeback: bool: Falseの場合、cumsum_diffが0未満の最初の行（追いつかれた週）まで残し､
                     以降の行をフィルタリングして除外する。Trueの場合、すべての行を含める。
                     デフォルトはFalseで、逆転を想定していない｡が､これは完璧に実態に沿っているので問題ない｡
        Returns:
            pl.DataFrame: 各ペアの差分を列として持つDataFrame

    ```
    ## cumsum_diffs_long()の出力テーブルの構造案

    - index_week: int: 週番号(1から始まる)
    - report_date: datetime: 集計日
    - hw_new: str : NSW, NS2などの､後から追いかけるマシン
    - hw_old: str: PS4, PS5などの､基準となるマシン(追いつかれる方のマシン)
    - pair_name: str : PS4_NSW差, PS5_NS2差の様な､比較対象を示す文字列
    - cumsum_diff : int: old_hwとnew_hwの同じ集計日の累計差分値 (sum_units_old - sum_units_new)
    - sum_units_new: int: new_hwの累計値
    - sum_units_old: int: old_hwの累計値

    ## 出力テーブル構成ロジック

    - cmplistの各ペアについて､上記の形式のdataframeを作成する｡
    - それぞれのdataframeを concatする｡
    - index_weekでソートして､最終的な出力テーブルとする｡

    ## 各ペアのdataframe構成ロジック

    - df_allから､hw_oldとhw_newのデータをそれぞれ別々のdataframeとして抽出する｡
    - カラム名を変更する
        - old側: hw:hw_old, sum_units: sum_units_old, index_week:index_week_old
        - new側: hw:hw_new, sum_units: sum_units_new, index_week:index_week_new
    - 集計日(report_date)を基準をjoinする｡hw_oldを左､hw_newを右にして､集計日で結合する｡
    - selectで必要なカラムを抽出する｡
        - report_date, hw_old, hw_new, sum_units_old, sum_units_new, index_week_new
    - 結合後､cumsum_diffを計算する｡ sum_units_old - sum_units_new = cumsum_diff
    - report_dateでソートする
    - cumsum_diffの値で以下の条件でフィルタリングする｡
        - cumsum_diffが0以上の行 と
        - cumsum_diffが0未満の最初の行 (つまり､追いつかれた週) までを残す｡ (これはpolarsでどんな処理になる?)
    - pair_nameを作成する｡ f"{hw_new}_{hw_old}差"
    - index_week_newをindex_weekにリネームする
    """)
    return


@app.function
def cumsum_diffs_long(df: pl.DataFrame,
                      cmplist: list[tuple[str, str]],
                      include_comeback: bool = False) -> pl.DataFrame:
    """
    複数のハードウェア間の(カレンダー上の)同時期の累計販売台数の差分を計算してDataFrameで返す。

    Args:
        df: load_hard_sales()で取得したDataFrame
        cmplist: 比較するハードウェアのペアのリスト。各タプルは(hw_new, hw_old)の形式で、
                 ハードウェアシンボルのペアを指定する。
                 例えば[("NS2", "PS5"), ("NSW", "PS4")]のように指定する。
                 hw_oldの累計販売台数からhw_newの累計販売台数を引いた差分を計算する。
                 これにより、PS5とNS2の差分、PS4とNSWの差分が計算され､
                 NS2がPS5に､NSWがPS4に追いつく様子を分析できる。
        include_comeback: bool: Falseの場合、cumsum_diffが0未満の最初の行（追いつかれた週）まで残し､
                 以降の行をフィルタリングして除外する。Trueの場合、すべての行を含める。
                 デフォルトはFalseで、逆転を想定していない｡が､これは完璧に実態に沿っているので問題ない｡

    Returns:
        pl.DataFrame: 各ペアの差分を列として持つDataFrame
    """
    dfs = []

    def filter_hw_and_rename(df: pl.DataFrame, hw: str, role: str) -> pl.DataFrame:
        return df.filter(pl.col("hw") == hw).select([
            "hw",
            "report_date",
            "sum_units",
            "index_week"
        ]).rename({
            "hw": f"hw_{role}",
            "sum_units": f"sum_units_{role}",
            "index_week": f"index_week_{role}"
        })

    for hw_new, hw_old in cmplist:
        # old側のデータを抽出
        df_old = filter_hw_and_rename(df, hw_old, "old")       
        # new側のデータを抽出
        df_new = filter_hw_and_rename(df, hw_new, "new")

        # report_dateで結合（old左、new右）
        df_pair = df_old.join(df_new, on="report_date", how="inner")

        # cumsum_diffを計算
        df_pair = df_pair.with_columns([
            (pl.col("sum_units_old") - pl.col("sum_units_new")).alias("cumsum_diff")
        ])
        df_pair = df_pair.sort("report_date")
        if not include_comeback:
            negative_rows = df_pair.filter(pl.col("cumsum_diff") < 0)
            if negative_rows.shape[0] > 0:
                negative_rows = negative_rows.select(pl.col("report_date")).min()
                df_pair = df_pair.filter(pl.col("report_date") <= negative_rows.item())

        # pair_nameを作成
        df_pair = df_pair.with_columns(
            pl.concat_str([
                pl.col("hw_new"),
                pl.lit("_"),
                pl.col("hw_old"),
                pl.lit("差")
            ]).alias("pair_name")
        )

        # カラムを再配置
        df_pair = df_pair.select([
            "report_date",
            "hw_new",
            "hw_old",
            "pair_name",
            "cumsum_diff",
            "sum_units_new",
            "sum_units_old",
            "index_week_new"
        ]).rename({
            "index_week_new": "index_week"
        })

        dfs.append(df_pair)

    # すべてのペアのdataframeを結合
    result = pl.concat(dfs)

    # index_weekでソート
    result = result.sort("index_week")

    return result


@app.cell
def _(df_all):
    _cmplist = [("NSW", "PS4"), ("NS2", "PS5")]

    difflib_df = cumsum_diffs_long(df_all, cmplist=_cmplist)
    difflib_df
    return


if __name__ == "__main__":
    app.run()
