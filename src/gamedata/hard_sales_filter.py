from datetime import datetime
import pandas as pd


def _date_filter(src_df: pd.DataFrame, 
                 begin: datetime | None = None, end: datetime | None = None) -> pd.DataFrame:
    """
    日付でDataFrameをフィルタリングする内部関数。
    Args:
        src_df: load_hard_sales()の戻り値のDataFrame
        begin: 集計開始日
        end: 集計終了日 
    Returns:
        pd.DataFrame: 日付でフィルタリングしたDataFrame
    """
    if begin is not None and end is not None:
        df = src_df.loc[(src_df['report_date'] >= begin) & (src_df['report_date'] <= end), :].copy()
    elif begin is not None:
        df = src_df.loc[src_df['report_date'] >= begin, :].copy()
    elif end is not None:
        df = src_df.loc[src_df['report_date'] <= end, :].copy()
    else:
        df = src_df.copy()
    return df

def weekly_sales(src_df: pd.DataFrame, 
                  begin: datetime | None = None, end: datetime | None = None,
                  maker_mode:bool = False) -> pd.DataFrame:
    """
    週毎の販売台数と、その週までの累計販売台数（sum_units）を集計して返す。
    
    Args:
        src_df: load_hard_sales()の戻り値のDataFrame
        begin: 集計開始日
        end: 集計終了日
        maker_mode: Trueの場合、メーカー毎に集計。Falseの場合、ハード毎に集計。

    Returns:
        pd.DataFrame: 週毎の販売台数（weekly_units）と累計販売台数（sum_units）を含むDataFrame
        
        DataFrameのカラム詳細:
        - report_date (datetime64): 集計期間の末日、日曜日である
        - hw (string): ゲームハードの識別子 (maker_mode=Falseの場合)
        - maker_name (string): メーカー名 (maker_mode=Trueの場合)
        - weekly_units (int64): 週次販売台数
        - sum_units (int64): report_date時点での累計販売台数
    """
    df = _date_filter(src_df, begin=begin, end=end)

    # 週ごとの販売台数を集計
    if maker_mode:
        key_column = 'maker_name'
    else:
        key_column = 'hw'
    
    weekly_sales = df.groupby(['report_date', key_column]).agg({'units': 'sum'}).reset_index()
    weekly_sales.rename(columns={'units': 'weekly_units'}, inplace=True)

    # 週ごとの累計販売台数を計算
    weekly_sales['sum_units'] = (
        weekly_sales
        .sort_values([key_column, 'report_date'])
        .groupby(key_column)['weekly_units']
        .cumsum()
    )
    return weekly_sales


def monthly_sales(src_df: pd.DataFrame, 
                  begin: datetime | None = None, end: datetime | None = None,
                  maker_mode:bool = False) -> pd.DataFrame:
    """
    月毎の販売台数と、その月までの累計販売台数（sum_units）を集計して返す。
    
    Args:
        src_df: load_hard_sales()の戻り値のDataFrame
        begin: 集計開始日
        end: 集計終了日
        maker_mode: Trueの場合、メーカー毎に集計。Falseの場合、ハード毎に集計。

    Returns:
        pd.DataFrame: 月毎の販売台数（monthly_units）と累計販売台数（sum_units）を含むDataFrame
        
        DataFrameのカラム詳細:
        - year (int64): report_dateの年
        - month (int64): report_dateの月
        - hw (string): ゲームハードの識別子 (maker_mode=Falseの場合) 
        - maker_name (string): メーカー名 (maker_mode=Trueの場合)
        - monthly_units (int64): 月次販売台数
        - sum_units (int64): その月時点での累計販売台数
    """
    df = _date_filter(src_df, begin=begin, end=end)

    # 月ごとの販売台数を集計
    if maker_mode:
        key_column = 'maker_name'
    else:
        key_column = 'hw'
    
    monthly_sales = df.groupby(['year', 'month', key_column]).agg({'units': 'sum'}).reset_index()
    monthly_sales.rename(columns={'units': 'monthly_units'}, inplace=True)

    # 月ごとの累計販売台数を計算
    monthly_sales['sum_units'] = (
        monthly_sales
        .sort_values([key_column, 'year', 'month'])
        .groupby(key_column)['monthly_units']
        .cumsum()
    )
    return monthly_sales


def quarterly_sales(src_df: pd.DataFrame, 
                  begin: datetime | None = None, end: datetime | None = None,
                  maker_mode:bool = False) -> pd.DataFrame:
    """
    四半期毎の販売台数と、その四半期までの累計販売台数（sum_units）を集計して返す。

    Args:
        src_df: load_hard_sales()の戻り値のDataFrame
        begin: 集計開始日
        end: 集計終了日
        maker_mode: Trueの場合、メーカー毎に集計。Falseの場合、ハード毎に集計。

    Returns:
        pd.DataFrame: 四半期毎の販売台数（quarterly_units）と累計販売台数（sum_units）を含むDataFrame
        
        DataFrameのカラム詳細:
        - quarter (Period): report_dateの四半期（Period型）
        - hw (string): ゲームハードの識別子 (maker_mode=Falseの場合) 
        - maker_name (string): メーカー名 (maker_mode=Trueの場合)
        - quarterly_units (int64): 四半期販売台数
        - sum_units (int64): その四半期時点での累計販売台数
    """
    df = _date_filter(src_df, begin=begin, end=end)

    # 四半期ごとの販売台数を集計
    if maker_mode:
        key_column = 'maker_name'
    else:
        key_column = 'hw'
    
    quarterly_sales = df.groupby(['quarter', key_column]).agg({'units': 'sum'}).reset_index()
    quarterly_sales.rename(columns={'units': 'quarterly_units'}, inplace=True)

    # 四半期ごとの累計販売台数を計算
    quarterly_sales['sum_units'] = (
        quarterly_sales
        .sort_values([key_column, 'quarter'])
        .groupby(key_column)['quarterly_units']
        .cumsum()
    )
    return quarterly_sales


def yearly_sales(src_df: pd.DataFrame, 
                 begin: datetime | None = None, end: datetime | None = None,
                 maker_mode:bool = False) -> pd.DataFrame:
    """
    年毎の販売台数と、その年までの累計販売台数（sum_units）を集計して返す。

    Args:
        src_df: load_hard_sales()の戻り値のDataFrame
        begin: 集計開始日
        end: 集計終了日
        maker_mode: Trueの場合、メーカー毎に集計。Falseの場合、ハード毎に集計。

    Returns:
        pd.DataFrame: 年毎の販売台数（yearly_units）と累計販売台数（sum_units）を含むDataFrame
        
        DataFrameのカラム詳細:
        - year (int64): report_dateの年
        - hw (string): ゲームハードの識別子 (maker_mode=Falseの場合) 
        - maker_name (string): メーカー名 (maker_mode=Trueの場合)
        - yearly_units (int64): 年次販売台数
        - sum_units (int64): その年時点での累計販売台数
    """
    df = _date_filter(src_df, begin=begin, end=end)

    # 年ごとの販売台数を集計
    if maker_mode:
        key_column = 'maker_name'
    else:
        key_column = 'hw'

    yearly_sales = df.groupby(['year', key_column]).agg({'units': 'sum'}).reset_index()
    yearly_sales.rename(columns={'units': 'yearly_units'}, inplace=True)

    # 年ごとの累計販売台数を計算
    yearly_sales['sum_units'] = (
        yearly_sales
        .sort_values([key_column, 'year'])
        .groupby(key_column)['yearly_units']
        .cumsum()
    )

    return yearly_sales


def yearly_maker_sales(src_df: pd.DataFrame, 
                begin: datetime | None = None, end: datetime | None = None) -> pd.DataFrame:
    """
    年毎、メーカー毎の販売台数を集計して返す。

    Args:
        src_df: load_hard_sales()の戻り値のDataFrame
        begin: 集計開始日
        end: 集計終了日

    Returns:
        pd.DataFrame: 年毎、メーカー毎の販売台数を含むDataFrame

        DataFrameのカラム詳細:
        - year (int64): report_dateの年
        - maker_name (string): メーカー名
        - yearly_units (int64): 年次販売台数
    """
    df = yearly_sales(src_df, begin=begin, end=end, maker_mode=True)
    ## dfからsum_unitsを削除する
    return df.drop(columns=['sum_units'])


def delta_yearly_sales(df: pd.DataFrame) -> pd.DataFrame:
    """
    販売開始からの経過年毎の販売台数と、その経過年までの累計販売台数（sum_units）を集計して返す。

    Args:
        df: load_hard_sales()の戻り値のDataFrame
    
    Returns:
        pd.DataFrame: 経過年毎の販売台数（yearly_units）と累計販売台数（sum_units）を含むDataFrame
        
        DataFrameのカラム詳細:
        - delta_year (int64): 発売年から何年後か(同じ年なら0)
        - hw (string): ゲームハードの識別子
        - yearly_units (int64): 経過年次販売台数
        - sum_units (int64): その経過年時点での累計販売台数
    """
    # 年ごとの販売台数を集計
    delta_yearly_sales = df.groupby(['delta_year', 'hw']).agg({'units': 'sum'}).reset_index()
    delta_yearly_sales.rename(columns={'units': 'yearly_units'}, inplace=True)

    # 年ごとの累計販売台数を計算
    delta_yearly_sales['sum_units'] = (
        delta_yearly_sales
        .sort_values(['hw', 'delta_year'])
        .groupby('hw')['yearly_units']
        .cumsum()
    )
    return delta_yearly_sales

