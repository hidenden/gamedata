from datetime import datetime, date
import polars as pl
from typing import List

# プロジェクト内モジュール
from . import hard_sales as hs
from . import hard_sales_filter as hsf
from . import hard_info as hi
from .mode import Mode, parse_mode


def sales_long(
    df: pl.DataFrame,
    hw: List[str] = [],
    begin: datetime | date | None = None,
    end: datetime | date | None = None,
) -> pl.DataFrame:
    """
    ハードウェアの週単位の販売台数をlong形式で返す。

    Args:
        src_df: load_hard_sales()で取得したDataFrame
        hw: 対象ハードウェア名のリスト。[]の場合は全ハードウェアを対象
        begin: 集計開始日
        end: 集計終了日

    Returns:
        pl.DataFrame: long形式の販売台数DataFrame

        DataFrameのカラム構成:
        - report_date (Date): 集計期間の末日（日曜日）
        - hw (String): ゲームハードの識別子
        - units (Int64): 週次販売台数
    """
    df = hsf.date_filter(df, begin=begin, end=end)
    if len(hw) > 0:
        df = df.filter(pl.col("hw").is_in(hw))
    return df.sort("report_date")


def monthly_sales_long(
    df: pl.DataFrame,
    hw: List[str] = [],
    begin: datetime | date | None = None,
    end: datetime | date | None = None,
) -> pl.DataFrame:
    """
    ハードウェアの月単位の販売台数をlong形式で返す。

    Args:
        df: load_hard_sales()で取得したDataFrame
        hw: 対象ハードウェア名のリスト。[]の場合は全ハードウェアを対象
        begin: 集計開始日
        end: 集計終了日

    Returns:
        pl.DataFrame: long形式の月次販売台数DataFrame

        DataFrameのカラム構成:
        - year_month (Date): 月の末日
        - year (Int16): 年
        - month (Int8): 月
        - hw (String): ゲームハードの識別子
        - monthly_units (Int64): 月次販売台数
    """
    df = hsf.monthly_sales(df, begin=begin, end=end)
    if len(hw) > 0:
        df = df.filter(pl.col("hw").is_in(hw))
    df = df.with_columns(
        year_month=pl.date(pl.col("year"), pl.col("month"), 1).dt.month_end()
    ).with_columns(year_month_str=pl.col("year_month").dt.strftime("%Y-%m"))
    return df.select(
        ["year_month", "year_month_str", "year", "month", "hw", "monthly_units"]
    ).sort("year_month")


def quarterly_sales_long(
    df: pl.DataFrame,
    hw: List[str] = [],
    begin: datetime | date | None = None,
    end: datetime | date | None = None,
) -> pl.DataFrame:
    """
    ハードウェアの四半期単位の販売台数をlong形式で返す。

    Args:
        df: load_hard_sales()で取得したDataFrame
        hw: 対象ハードウェア名のリスト。[]の場合は全ハードウェアを対象
        begin: 集計開始日
        end: 集計終了日

    Returns:
        pl.DataFrame: long形式の四半期販売台数DataFrame

        DataFrameのカラム構成:
        - quarter (String): report_dateの四半期（例: "2024Q1"）
        - fiscal_quarter (String): 会計年度の四半期（例: "2024Q1"）
        - year (Int16): 年
        - fiscal_year (Int16): 会計年度
        - q_num (Int8): 四半期番号（1, 2, 3, 4）
        - fq_num (Int8): 会計年度内の四半期番号（1, 2, 3, 4）
        - hw (String): ゲームハードの識別子
        - quarterly_units (Int64): 四半期販売台数
    """
    df = hsf.quarterly_sales(df, begin=begin, end=end)
    if len(hw) > 0:
        df = df.filter(pl.col("hw").is_in(hw))
    return df.select(
        [
            "quarter",
            "fiscal_quarter",
            "year",
            "fiscal_year",
            "q_num",
            "fq_num",
            "hw",
            "quarterly_units",
        ]
    ).sort("quarter")


def yearly_sales_long(
    df: pl.DataFrame,
    hw: List[str] = [],
    begin: datetime | date | None = None,
    end: datetime | date | None = None,
) -> pl.DataFrame:
    """
    ハードウェアの年単位の販売台数をlong形式で返す。

    Args:
        df: load_hard_sales()で取得したDataFrame
        hw: 対象ハードウェア名のリスト。[]の場合は全ハードウェアを対象
        begin: 集計開始日
        end: 集計終了日

    Returns:
        pl.DataFrame: long形式の年次販売台数DataFrame

        DataFrameのカラム構成:
        - year (Int16): report_dateの年
        - hw (String): ゲームハードの識別子
        - yearly_units (Int64): 年次販売台数
    """
    df = hsf.yearly_sales(df, begin=begin, end=end)
    if len(hw) > 0:
        df = df.filter(pl.col("hw").is_in(hw))
    return df.sort("year")


def cumulative_sales_long(
    df: pl.DataFrame,
    hw: List[str] = [],
    begin: datetime | None = None,
    end: datetime | None = None,
    mode: str = "week",
    full_name: bool = False,
) -> pl.DataFrame:
    """
    ハードウェアの累計販売台数をlong形式で返す。

    Args:
        df: load_hard_sales()で取得したDataFrame
        hw: 対象ハードウェア名のリスト。[]の場合は全ハードウェアを対象
        begin: 集計開始日
        end: 集計終了日
        mode: "week"、"month"または"year"を指定。週単位の集計なら"week"、月単位の集計なら"month"、年単位の集計なら"year"を指定。
        full_name: カラム名にフルネームを使用する

    Returns:
        pl.DataFrame: long形式の累計販売台数DataFrame

        DataFrameのカラム構成:
        - report_date (Date): 集計期間の末日（日曜日）
        - hw または full_name (String): ゲームハードの識別子またはフルネーム
        - sum_units (Int64): 累計販売台数
    """
    df = hsf.date_filter(df, begin=begin, end=end)
    if len(hw) > 0:
        df = df.filter(pl.col("hw").is_in(hw))

    columns_name = "full_name" if full_name else "hw"
    long_df = df.sort("report_date")

    mode_enum = parse_mode(mode)
    if mode_enum == Mode.WEEK:
        return long_df

    if mode_enum == Mode.MONTH:
        partition_cols = ["hw", "year", "month"]
    elif mode_enum == Mode.QUARTER:
        partition_cols = ["hw", "year", "q_num"]
    elif mode_enum == Mode.FISCAL_QUARTER:
        partition_cols = ["hw", "fiscal_year", "fq_num"]
    elif mode_enum == Mode.YEAR:
        partition_cols = ["hw", "year"]
    elif mode_enum == Mode.FISCAL_YEAR:
        partition_cols = ["hw", "fiscal_year"]
    else:
        raise ValueError("modeは'week', 'month', 'year'のいずれかを指定してください。")

    long_df = (
        long_df.with_columns(
            pl.col(name="sum_units").max().over(partition_cols).alias("max_units")
        )
        .filter(pl.col("sum_units") == pl.col("max_units"))
        .drop("max_units")
        .sort(by=["report_date"])
    )
    return long_df


def sales_by_delta_long(
    df: pl.DataFrame,
    mode: str = "week",
    begin: int | None = None,
    end: int | None = None,
    hw: List[str] = [],
    full_name: bool = False,
) -> pl.DataFrame:
    """
    ハードウェアの販売台数を発売日からの経過期間をインデックスとしたlong形式で返す。

    Args:
        df: load_hard_sales()で取得したDataFrame
        mode: "week"、"month"または"year"を指定。週単位の集計なら"week"、月単位の集計なら"month"、年単位の集計なら"year"を指定。
        begin: 集計開始（経過期間の最小値）
        end: 集計終了（経過期間の最大値）
        hw: 対象ハードウェア名のリスト。[]の場合は全ハードウェアを対象
        full_name: フルネームを使用するかどうか

    Returns:
        pl.DataFrame: long形式の販売台数DataFrame

        DataFrameのカラム構成:
        - delta_week (Int32): 発売日からの経過週数（modeが"week"の場合）
        - delta_month (Int16): 発売日からの経過ヶ月数（modeが"month"の場合）
        - delta_year (Int16): 発売年からの経過年数（modeが"year"の場合）
        - hw または full_name (String): ゲームハードの識別子またはフルネーム
        - units (Int64): 販売台数
    """
    mode_enum = parse_mode(mode)
    if mode_enum == Mode.WEEK:
        index_col = "delta_week"
        alt_index_col = "index_week"
    elif mode_enum == Mode.MONTH:
        index_col = "delta_month"
        alt_index_col = "index_month"
    elif mode_enum == Mode.YEAR:
        index_col = "delta_year"
        alt_index_col = "index_year"
    else:
        raise ValueError("modeは'week', 'month', 'year'のいずれかを指定してください。")

    if begin:
        df = df.filter(pl.col(index_col) >= begin)
    if end:
        df = df.filter(pl.col(index_col) <= end)

    if len(hw) > 0:
        df = df.filter(pl.col("hw").is_in(hw))

    on_columns = "full_name" if full_name else "hw"

    return (
        df.group_by([index_col, alt_index_col, on_columns])
        .agg(pl.col("units").sum())
        .sort(by=[index_col, alt_index_col, on_columns])
    )


def sales_with_offset_long(
    src_df: pl.DataFrame, hw_periods: List[dict], end: int = 52
) -> pl.DataFrame:
    """
    複数のハードウェアの異なる期間のデータを、各期間の開始点を揃えたlong形式で返す。

    Args:
        src_df: load_hard_sales()で取得したDataFrame
        hw_periods: 各ハードウェアの期間設定のリスト
            各要素は以下のキーを持つ辞書:
            - 'hw' (str, required): ハードウェアの識別子
            - 'begin' (datetime, required): 集計開始日
            - 'label' (str, optional): 列名（省略時はhw名を使用）
        end: 各期間の最大週数（デフォルトは52週）

    Returns:
        pl.DataFrame: long形式のDataFrame

        DataFrameのカラム構成:
        - offset_week (Int32): 各期間の開始日からの経過週数
        - label (String): ハードウェアのラベル
        - units (Int64): 週次販売台数
    """
    all_data = []

    for period in hw_periods:
        hw = period["hw"]
        begin = period["begin"]
        default_label = f"{hw}:{begin.strftime('%Y.%m.%d')}〜"
        label = period.get("label", default_label)

        hw_df = src_df.filter(pl.col("hw") == hw)
        hw_df = hw_df.filter(pl.col("report_date") >= begin)
        hw_df = hw_df.sort("report_date").head(end)

        hw_df = hw_df.with_columns(
            offset_week=((pl.col("report_date") - begin).dt.total_days() / 7).cast(
                pl.Int32
            )
        )

        hw_df = hw_df.select(
            ["offset_week", "units", "report_date", "hw"]
        ).with_columns(label=pl.lit(label))

        all_data.append(hw_df)

    return pl.concat(all_data).sort("offset_week")


def yearly_cumulative_long(
    df: pl.DataFrame,
    year: int = 2026,
    hw: List[str] = [],
    begin: int = 1,
    end: int = 366,
) -> pl.DataFrame:
    """
    複数のハードウェアの同じ年の年次累積データをlong形式で返す。

    Args:
        df: load_hard_sales()で取得したDataFrame
        year: 対象年
        hw: 対象ハードウェア名のリスト。[]の場合は全ハードウェアを対象
        begin: 集計開始（年次累積の最小値、1から始まる）
        end: 集計終了（年次累積の最大値、1から始まる）beginより大きい値を指定すること

    Returns:
        pl.DataFrame: long形式のDataFrame

        DataFrameのカラム構成:
        - yday (Int16): Year of Date, 各期間の開始日からの経過日数
        - year (Int16): report_dateの年
        - hw (String): ゲームハードの識別子
        - yearly_sum_units (Int64): 年次累積販売台数
        - report_date (Date): 集計日 (イベント情報等との結合用)
    """
    if len(hw) > 0:
        df = df.filter(pl.col("hw").is_in(hw))
    df = (
        df.filter(pl.col("year") == year)
        .filter(pl.col("yday") >= begin)
        .filter(pl.col("yday") <= end)
        .sort("yday")
    )
    return df


def yearly_cumulative_by_hwy_long(
    src_df: pl.DataFrame,
    hw_years: list[tuple[str, int]],
    begin: int = 1,
    end: int = 366,
) -> pl.DataFrame:
    """
    複数のハードウェアの異なる年の年次累積データをlong形式で返す。

    Args:
        src_df: load_hard_sales()で取得したDataFrame
        hw_years: 各ハードウェアの年次設定のリスト
            各要素は(hw, year)のタプル形式で、hwはハードウェアの識別子、yearは対象年を指定する。
             例えば[("NS2", 2024), ("PS5", 2020)]のように指定する。
             これにより、NS2の2024年の年次累積とPS5の2020年の年次累積を比較できる。
        begin: 集計開始（年次累積の最小値、1から始まる）
        end: 集計終了（年次累積の最大値、1から始まる）beginより大きい値を指定すること

    Returns:
        pl.DataFrame: long形式のDataFrame

        DataFrameのカラム構成:
        - yday (Int16): Year of Date, 各期間の開始日からの経過日数
        - year (Int16): report_dateの年
        - hw (String): ゲームハードの識別子
        - label (String): ハードウェアのラベル ("{hw}:{year}"の形式)
        - yearly_sum_units (Int64): 年次累積販売台数
        - report_date (Date): 集計日 (イベント情報等との結合用)
    """
    all_data = []

    for hw, year in hw_years:
        hw_df = (
            src_df.filter(pl.col("hw") == hw)
            .filter(pl.col("year") == year)
            .filter(pl.col("yday") >= begin)
            .filter(pl.col("yday") <= end)
        )
        label = f"{hw}:{year}"
        hw_df = hw_df.with_columns(
            label=pl.lit(label),
        )
        all_data.append(hw_df)

    return pl.concat(all_data).sort("yday")


def cumulative_sales_by_delta_long(
    df: pl.DataFrame,
    mode: str = "week",
    hw: List[str] = [],
    begin: int | None = None,
    end: int | None = None,
) -> pl.DataFrame:
    """
    ハードウェアの累計販売台数を発売日からの経過期間をインデックスとしたlong形式で返す。

    Args:
        df: load_hard_sales()で取得したDataFrame
        mode: "week"、"month"または"year"を指定。週単位の集計なら"week"、月単位の集計なら"month"、年単位の集計なら"year"を指定。
        hw: 対象ハードウェア名のリスト。[]の場合は全ハードウェアを対象
        begin: 集計開始（経過期間の最小値）
        end: 集計終了（経過期間の最大値）

    Returns:
        pl.DataFrame: long形式の累計販売台数DataFrame

        DataFrameのカラム構成:
        - delta_week (Int32): 発売日からの経過週数（modeが"week"の場合）
        - delta_month (Int16): 発売日からの経過ヶ月数（modeが"month"の場合）
        - delta_year (Int16): 発売年からの経過年数（modeが"year"の場合）
        - hw (String): ゲームハードの識別子
        - sum_units (Int64): 累計販売台数
    """
    mode_enum = parse_mode(mode)
    if mode_enum == Mode.WEEK:
        index_col = "delta_week"
        alt_index_col = "index_week"
    elif mode_enum == Mode.MONTH:
        index_col = "delta_month"
        alt_index_col = "index_month"
    elif mode_enum == Mode.YEAR:
        index_col = "delta_year"
        alt_index_col = "index_year"
    else:
        raise ValueError("modeは'week', 'month', 'year'のいずれかを指定してください。")

    if begin:
        df = df.filter(pl.col(index_col) >= begin)
    if end:
        df = df.filter(pl.col(index_col) <= end)

    if len(hw) > 0:
        df = df.filter(pl.col("hw").is_in(hw))

    return (
        df.group_by([index_col, alt_index_col, "hw"])
        .agg(pl.col("sum_units").last())
        .sort(by=[index_col, alt_index_col, "hw"])
    )


def maker_long(
    df: pl.DataFrame, begin_year: int | None = None, end_year: int | None = None
) -> pl.DataFrame:
    """
    ハードウェアのメーカー別年次販売台数をlong形式で返す。

    Args:
        df: load_hard_sales()で取得したDataFrame
        begin_year: 開始年（デフォルト: None）
        end_year: 終了年（デフォルト: None）

    Returns:
        pl.DataFrame: long形式のメーカー別年次販売台数DataFrame

        DataFrameのカラム構成:
        - year (Int16): report_dateの年
        - maker_name (String): メーカー名
        - yearly_units (Int64): 年次販売台数
        - yearly_percentage (Float64): 年次販売台数のシェア()
        （同年の全ハードウェアの年次販売台数に対する割合のパーセント）
    """
    begin = None if begin_year is None else datetime(begin_year, 1, 1)
    end = None if end_year is None else datetime(end_year, 12, 31)
    df = hsf.yearly_maker_sales(df, begin=begin, end=end)

    df = df.with_columns(
        yearly_ratio=(
            pl.col("yearly_units") / pl.col("yearly_units").sum().over("year")
        ),
    )
    df = df.with_columns(yearly_pct=pl.col("yearly_ratio") * 100)
    maker_list = hs.get_maker(df)
    df = df.sort(
        by=[
            "year",
            pl.col(name="maker_name").cast(dtype=pl.Enum(categories=maker_list)),
        ]
    )
    return df.select(
        ["year", "maker_name", "yearly_units", "yearly_ratio", "yearly_pct"]
    )


def cumsum_diffs_long(
    df: pl.DataFrame, cmplist: list[tuple[str, str]], include_comeback: bool = False
) -> pl.DataFrame:
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
        - index_week: int: 週番号(1から始まる)
        - report_date: datetime: 集計日
        - hw_new: str : NSW, NS2などの､後から追いかけるマシン
        - hw_old: str: PS4, PS5などの､基準となるマシン(追いつかれる方のマシン)
        - pair_name: str : PS4_NSW差, PS5_NS2差の様な､比較対象を示す文字列
        - cumsum_diff : int: old_hwとnew_hwの同じ集計日の累計差分値 (sum_units_old - sum_units_new)
        - sum_units_new: int: new_hwの累計値
        - sum_units_old: int: old_hwの累計値
    """
    dfs = []

    def filter_hw_and_rename(df: pl.DataFrame, hw: str, role: str) -> pl.DataFrame:
        return (
            df.filter(pl.col("hw") == hw)
            .select(["hw", "report_date", "sum_units", "index_week"])
            .rename(
                {
                    "hw": f"hw_{role}",
                    "sum_units": f"sum_units_{role}",
                    "index_week": f"index_week_{role}",
                }
            )
        )

    for hw_new, hw_old in cmplist:
        # old側のデータを抽出
        df_old = filter_hw_and_rename(df, hw_old, "old")
        # new側のデータを抽出
        df_new = filter_hw_and_rename(df, hw_new, "new")

        # report_dateで結合（old左、new右）
        df_pair = df_old.join(df_new, on="report_date", how="inner")

        # cumsum_diffを計算
        df_pair = df_pair.with_columns(
            [(pl.col("sum_units_old") - pl.col("sum_units_new")).alias("cumsum_diff")]
        )
        df_pair = df_pair.sort("report_date")
        if not include_comeback:
            negative_rows = df_pair.filter(pl.col("cumsum_diff") < 0)
            if negative_rows.shape[0] > 0:
                negative_rows = negative_rows.select(pl.col("report_date")).min()
                df_pair = df_pair.filter(pl.col("report_date") <= negative_rows.item())

        # pair_nameを作成
        df_pair = df_pair.with_columns(
            pl.concat_str(
                [pl.col("hw_new"), pl.lit("_"), pl.col("hw_old"), pl.lit("差")]
            ).alias("pair_name")
        )

        # カラムを再配置
        df_pair = df_pair.select(
            [
                "report_date",
                "hw_new",
                "hw_old",
                "pair_name",
                "cumsum_diff",
                "sum_units_new",
                "sum_units_old",
                "index_week_new",
            ]
        ).rename({"index_week_new": "index_week"})

        dfs.append(df_pair)

    # すべてのペアのdataframeを結合
    result = pl.concat(dfs)

    # index_weekでソート
    result = result.sort("index_week")

    return result


def sales_pase_diffs_long(
    df: pl.DataFrame, cmplist: list[tuple[str, str]]
) -> pl.DataFrame:
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
        - index_week: int: 週番号(1から始まる)
        - hw_old: str : 比較対象となる古いマシン
        - hw_new: str : 普及状況を分析したいマシン
        - pair_name: str : PS4_NSW差, PS5_NS2差の様な､比較対象を示す文字列
        - pase_diff : int: hw_oldとhw_newの同じ相対週での累計差分値
        - sum_units_old: int: hw_oldの累計値
        - sum_units_new: int: hw_newの累計値
        - report_date_new: datetime: hw_newのreport_date
        - report_date_old: datetime: hw_oldのreport_date
    """
    dfs = []

    def filter_hw_and_rename(df, hw, role):
        return (
            df.filter(pl.col("hw") == hw)
            .select(["hw", "index_week", "report_date", "sum_units"])
            .rename(
                {
                    "hw": f"hw_{role}",
                    "report_date": f"report_date_{role}",
                    "sum_units": f"sum_units_{role}",
                }
            )
        )

    for hw_new, hw_old in cmplist:
        # old側のデータを抽出
        df_old = filter_hw_and_rename(df, hw_old, "old")
        # new側のデータを抽出
        df_new = filter_hw_and_rename(df, hw_new, "new")

        # index_weekで結合（old左、new右）
        df_pair = df_old.join(df_new, on="index_week", how="inner")

        # pase_diffを計算
        df_pair = df_pair.with_columns(
            [(pl.col("sum_units_new") - pl.col("sum_units_old")).alias("pase_diff")]
        )
        df_pair = df_pair.sort("index_week")

        # pair_nameを作成
        df_pair = df_pair.with_columns(
            pl.concat_str(
                [pl.col("hw_new"), pl.lit("_"), pl.col("hw_old"), pl.lit("差")]
            ).alias("pair_name")
        )

        # カラムを再配置
        df_pair = df_pair.select(
            [
                "index_week",
                "hw_new",
                "hw_old",
                "pair_name",
                "pase_diff",
                "sum_units_new",
                "sum_units_old",
                "report_date_new",
                "report_date_old",
            ]
        )

        dfs.append(df_pair)

    # すべてのペアのdataframeを結合
    result = pl.concat(dfs)

    # index_weekでソート
    result = result.sort("index_week")

    return result
