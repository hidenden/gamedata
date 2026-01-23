# GameData分析用のユーティリティ関数群

import sqlite3
from datetime import datetime, timedelta
import pandas as pd
from typing import List


DB_PATH = '/Users/hide/Documents/sqlite3/gamehard.db'

def load_hard_sales() -> pd.DataFrame:
    """
    sqlite3を使用してデータベースからハードウェア販売データを読み込む関数。
    日付関係のカラムをdatetime64[ns]型に変換して返す。
    
    Returns:
        pd.DataFrame: ハードウェア販売データのDataFrame。
                      日付カラム（begin_date, report_date, end_date, launch_date）は
                      datetime64[ns]型に変換済み。
        
        DataFrameのカラム詳細:
        - weekly_id (string): 週次データのID（gamehard_weekly.id）
        - begin_date (datetime64): 集計開始日（週の初日）、月曜日である
        - end_date (datetime64): 集計終了日（週の末日、=report_date）
        - report_date (datetime64): 集計期間の末日、日曜日である
        - quarter (Period): report_dateの四半期（Period型）
        - period_date (int64): 集計日数(通常は7, 稀に14)
        - hw (string): ゲームハードの識別子
        - units (int64): 週次販売台数
        - adjust_units (int64): 週次販売台数の補正値(unitsは補正済みの値である)
        - year (int64): report_dateの年
        - month (int64): report_dateの月
        - mday (int64): report_dateの日
        - week (int64): report_dateがその月の何番目の日曜日か
        - delta_day (int64): 発売日から何日後か
        - delta_week (int64): 発売日から何週間後か
        - delta_month (int64): 発売日から何ヶ月後か
        - delta_year (int64): 発売年から何年後か(同じ年なら0)
        - avg_units (int64): 1日あたりの販売台数 (units / period_date)
        - sum_units (int64): report_date時点での累計販売台数
        - launch_date (datetime64): 発売日
        - maker_name (string): メーカー名
        - full_name (string): ゲームハードの正式名称
    """
    # SQLite3データベースに接続
    conn = sqlite3.connect(DB_PATH)
    # SQLクエリを実行してデータをDataFrameに読み込む
    query = "SELECT * FROM hard_sales ORDER BY weekly_id;"
    df = pd.read_sql_query(query, conn)
    
    # 接続を閉じる
    conn.close()

    # 日付をdatetime64[ns]型に変換
    df['begin_date'] = pd.to_datetime(df['begin_date'])
    df['report_date'] = pd.to_datetime(df['report_date'])
    df['end_date'] = pd.to_datetime(df['end_date'])
    df['launch_date'] = pd.to_datetime(df['launch_date'])
    
    # 四半期のPeriod型カラムを追加
    df['quarter'] = df['report_date'].dt.to_period('Q')

    return df



def current_report_date(df: pd.DataFrame) -> datetime:
    """
    DataFrameから最新の報告日を取得する関数。

    Args:
        df: load_hard_sales()の戻り値のDataFrame

    Returns:
        datetime: 最新の報告日
    """
    return df['report_date'].max()


def get_hw(df: pd.DataFrame) -> List[str]:
    """
    DataFrameからハードウェア名のユニークなリストを取得する。
    
    Args:
        df: load_hard_sales()の戻り値のDataFrame
    
    Returns:
        List[str]: ハードウェア名のユニークなリスト
    """
    return df['hw'].unique().tolist()


def get_active_hw() -> List[str]:
    """
    直近1年間のデータを元にアクティブなハードウェア名のリストを取得する。
    
    Returns:
        List[str]: アクティブなハードウェア名のリスト
    """
    base_df = load_hard_sales()
    now = datetime.now()
    one_year_ago = now - timedelta(days=365)
    recent_df = base_df.loc[base_df['report_date'] >= one_year_ago, :]
    active_hw = get_hw(recent_df)
    return active_hw    


