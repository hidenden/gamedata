# GameData分析用のユーティリティ関数群

import sqlite3
from datetime import datetime, timedelta
import polars as pl
from typing import List

# Polars Configuration
(pl.Config.set_tbl_rows(30)
    .set_tbl_cols(-1)
    .set_float_precision(2)
    .set_thousands_separator(',')
    .set_trim_decimal_zeros(True)
    .set_tbl_hide_column_data_types(False)
    .set_tbl_hide_dataframe_shape(True)
    # .set_tbl_column_data_type_inline(True)
)

DB_PATH = '/Users/hide/Documents/sqlite3/gamehard.db'

def load_hard_sales() -> pl.DataFrame:
    """
    sqlite3を使用してデータベースからハードウェア販売データを読み込む関数。
    日付関係のカラムをdate型に変換し、整数カラムを適切なサイズにキャストして返す。
    
    Returns:
        pl.DataFrame: ハードウェア販売データのDataFrame。
                      日付カラムはDate型、整数カラムは最適なサイズに変換済み。
        
        DataFrameのカラム詳細:
        - weekly_id (String): 週次データのID（gamehard_weekly.id）
        - begin_date (Date): 集計開始日（週の初日）、月曜日である
        - end_date (Date): 集計終了日（週の末日、=report_date）
        - report_date (Date): 集計期間の末日、日曜日である
        - quarter (String): report_dateの四半期（例: "2024Q1"）
        - period_date (Int16): 集計日数(通常は7, 稀に14)
        - hw (String): ゲームハードの識別子
        - units (Int64): 週次販売台数
        - adjust_units (Int64): 週次販売台数の補正値(unitsは補正済みの値である)
        - year (Int16): report_dateの年
        - month (Int16): report_dateの月
        - mday (Int16): report_dateの日
        - week (Int16): report_dateがその月の何番目の日曜日か
        - delta_day (Int32): 発売日から何日後か
        - delta_week (Int32): 発売日から何週間後か
        - delta_month (Int16): 発売日から何ヶ月後か
        - delta_year (Int16): 発売年から何年後か(同じ年なら0)
        - avg_units (Int64): 1日あたりの販売台数 (units / period_date)
        - sum_units (Int64): report_date時点での累計販売台数
        - launch_date (Date): 発売日
        - maker_name (String): メーカー名
        - full_name (String): ゲームハードの正式名称
    """
    # SQLite3データベースに接続
    conn = sqlite3.connect(DB_PATH)
    # SQLクエリを実行してデータをDataFrameに読み込む
    query = "SELECT * FROM hard_sales ORDER BY weekly_id;"
    df = pl.read_database(query, conn)
    
    # 接続を閉じる
    conn.close()

    # 日付をDate型に変換, 値の小さな整数はInt16にキャスト
    df = df.with_columns(
        pl.col('begin_date').str.to_date(),
        pl.col('report_date').str.to_date(),
        pl.col('end_date').str.to_date(),
        pl.col('launch_date').str.to_date(),
        pl.col('period_date').cast(pl.Int16),
        pl.col('year').cast(pl.Int16),
        pl.col('month').cast(pl.Int16),
        pl.col('mday').cast(pl.Int16),
        pl.col('week').cast(pl.Int16),
        pl.col('delta_day').cast(pl.Int32),
        pl.col('delta_week').cast(pl.Int32),
        pl.col('delta_month').cast(pl.Int16),
        pl.col('delta_year').cast(pl.Int16),
    )
    
    # 四半期のカラムを追加
    df = df.with_columns(
        quarter = (pl.col('report_date').dt.year().cast(pl.Utf8) + "Q" + 
                    pl.col('report_date').dt.quarter().cast(pl.Utf8))
    )
    df = df.sort('weekly_id')
    return df



def current_report_date(df: pl.DataFrame) -> datetime:
    """
    DataFrameから最新の報告日を取得する関数。

    Args:
        df: load_hard_sales()の戻り値のDataFrame

    Returns:
        datetime: 最新の報告日
    """
    return df.select(pl.col('report_date').max()).item()


def get_hw(df: pl.DataFrame) -> List[str]:
    """
    DataFrameからハードウェア名のユニークなリストを取得する。
    
    Args:
        df: load_hard_sales()の戻り値のDataFrame
    
    Returns:
        List[str]: ハードウェア名のユニークなリスト
    """
    return df['hw'].unique().to_list()


def get_active_hw(days: int = 365) -> List[str]:
    """
    直近1年間のデータを元にアクティブなハードウェア名のリストを取得する。
    
    Returns:
        List[str]: アクティブなハードウェア名のリスト
    """
    base_df = load_hard_sales()
    now = datetime.now()
    one_year_ago = now - timedelta(days=days)
    recent_df = base_df.filter(pl.col('report_date') >= one_year_ago)
    active_hw = get_hw(recent_df)
    return active_hw


def get_maker(df: pl.DataFrame) -> List[str]:
    """
    DataFrameからメーカー名のユニークなリストを取得する。
    
    Args:
        df: load_hard_sales()の戻り値のDataFrame
    
    Returns:
        List[str]: メーカー名のユニークなリスト
    """
    return df['maker_name'].unique().to_list()


def get_active_maker(days: int = 365) -> List[str]:
    """
    直近1年間のデータを元にアクティブなメーカー名のリストを取得する。
    
    Returns:
        List[str]: アクティブなメーカー名のリスト
    """
    base_df = load_hard_sales()
    now = datetime.now()
    one_year_ago = now - timedelta(days=days)
    recent_df = base_df.filter(pl.col('report_date') >= one_year_ago)
    active_maker = get_maker(recent_df)
    return active_maker


def with_units_diff(df: pl.DataFrame) -> pl.DataFrame:
    """
    同じハードウェアの前週比販売台数差分カラムを追加する。

    Args:
        df: load_hard_sales() の戻り値のDataFrame

    Returns:
        pl.DataFrame: units_diff (Int64) カラムを追加したDataFrame。
                      各ハードの初週は null になる。
    """
    df = df.sort('weekly_id')
    return df.with_columns(
        pl.col('units')
          .diff()
          .over('hw')
          .alias('units_diff')
    )

def add_week_number(df: pl.DataFrame) -> pl.DataFrame:
    """
    delta_week が存在する場合に、1始まりの週番号カラム week_number を追加する。

    Args:
        df: ハード販売データのDataFrame。

    Returns:
        pl.DataFrame: week_number カラムを追加したDataFrame。
                      delta_week が無い場合は入力をそのまま返す。
    """
    if "delta_week" in df.columns:
        df = df.with_columns(
            (pl.col("delta_week") + 1).alias("week_number")
        )
    return df

