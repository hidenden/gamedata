from datetime import datetime
import polars as pl


def date_filter(src_df: pl.DataFrame, 
                 begin: datetime | None = None, end: datetime | None = None) -> pl.DataFrame:
    """
    日付でDataFrameをフィルタリングする内部関数。
    Args:
        src_df: load_hard_sales()の戻り値のDataFrame
        begin: 集計開始日
        end: 集計終了日 
    Returns:
        pl.DataFrame: 日付でフィルタリングしたDataFrame
    """
    if begin is not None and end is not None:
        df = src_df.filter((pl.col('report_date') >= begin) & (pl.col('report_date') <= end))
    elif begin is not None:
        df = src_df.filter(pl.col('report_date') >= begin)
    elif end is not None:
        df = src_df.filter(pl.col('report_date') <= end)
    else:
        df = src_df.clone()
    return df

def weekly_sales(src_df: pl.DataFrame, 
                  begin: datetime | None = None, end: datetime | None = None,
                  maker_mode:bool = False) -> pl.DataFrame:
    """
    週毎の販売台数と、その週までの累計販売台数（sum_units）を集計して返す。
    
    Args:
        src_df: load_hard_sales()の戻り値のDataFrame
        begin: 集計開始日
        end: 集計終了日
        maker_mode: Trueの場合、メーカー毎に集計。Falseの場合、ハード毎に集計。

    Returns:
        pl.DataFrame: 週毎の販売台数（weekly_units）と累計販売台数（sum_units）を含むDataFrame
        
        DataFrameのカラム詳細:
        - report_date (Date): 集計期間の末日、日曜日である
        - hw (String): ゲームハードの識別子 (maker_mode=Falseの場合)
        - maker_name (String): メーカー名 (maker_mode=Trueの場合)
        - weekly_units (Int64): 週次販売台数
        - sum_units (Int64): report_date時点での累計販売台数
    """
    df = date_filter(src_df, begin=begin, end=end)

    # 週ごとの販売台数を集計
    if maker_mode:
        key_column = 'maker_name'
    else:
        key_column = 'hw'
    
    weekly_sales = (
        df.group_by(['report_date', key_column])
        .agg(pl.col('units').sum().alias('weekly_units'))
        .sort([key_column, 'report_date'])
        .with_columns(
            pl.col('weekly_units').cum_sum().over(key_column).alias('sum_units')
        )
    ).sort(by = ['report_date', 'weekly_units'], descending=[False, True])
    return weekly_sales


def monthly_sales(src_df: pl.DataFrame, 
                  begin: datetime | None = None, end: datetime | None = None,
                  maker_mode:bool = False) -> pl.DataFrame:
    """
    月毎の販売台数と、その月までの累計販売台数（sum_units）を集計して返す。
    
    Args:
        src_df: load_hard_sales()の戻り値のDataFrame
        begin: 集計開始日
        end: 集計終了日
        maker_mode: Trueの場合、メーカー毎に集計。Falseの場合、ハード毎に集計。

    Returns:
        pl.DataFrame: 月毎の販売台数（monthly_units）と累計販売台数（sum_units）を含むDataFrame
        
        DataFrameのカラム詳細:
        - year (Int16): report_dateの年
        - month (Int16): report_dateの月
        - hw (String): ゲームハードの識別子 (maker_mode=Falseの場合) 
        - maker_name (String): メーカー名 (maker_mode=Trueの場合)
        - monthly_units (Int64): 月次販売台数
        - sum_units (Int64): その月時点での累計販売台数
    """
    df = date_filter(src_df, begin=begin, end=end)

    # 月ごとの販売台数を集計
    if maker_mode:
        key_column = 'maker_name'
    else:
        key_column = 'hw'
    
    monthly_sales = (
        df.group_by(['year', 'month', key_column])
        .agg(pl.col('units').sum().alias('monthly_units'))
        .sort([key_column, 'year', 'month'])
        .with_columns(
            pl.col('monthly_units').cum_sum().over(key_column).alias('sum_units')
        )
    ).sort(by = ['year', 'month', 'monthly_units'], descending=[False, False, True])
    return monthly_sales


def quarterly_sales(src_df: pl.DataFrame, 
                  begin: datetime | None = None, end: datetime | None = None,
                  maker_mode:bool = False) -> pl.DataFrame:
    """
    四半期毎の販売台数と、その四半期までの累計販売台数（sum_units）を集計して返す。

    Args:
        src_df: load_hard_sales()の戻り値のDataFrame
        begin: 集計開始日
        end: 集計終了日
        maker_mode: Trueの場合、メーカー毎に集計。Falseの場合、ハード毎に集計。

    Returns:
        pl.DataFrame: 四半期毎の販売台数（quarterly_units）と累計販売台数（sum_units）を含むDataFrame
        
        DataFrameのカラム詳細:
        - quarter (String): report_dateの四半期（例: "2024Q1"）
        - year (Int16): report_dateの年
        - q_num (Int16): report_dateの四半期番号(1~4)
        - hw (String): ゲームハードの識別子 (maker_mode=Falseの場合) 
        - maker_name (String): メーカー名 (maker_mode=Trueの場合)
        - quarterly_units (Int64): 四半期販売台数
        - sum_units (Int64): その四半期時点での累計販売台数
    """
    df = date_filter(src_df, begin=begin, end=end)

    # 四半期ごとの販売台数を集計
    if maker_mode:
        key_column = 'maker_name'
    else:
        key_column = 'hw'
    
    # quarterカラムから年と四半期番号を抽出
    quarterly_sales = (
        df.group_by(['quarter', key_column])
        .agg(pl.col('units').sum().alias('quarterly_units'))
        .with_columns([
            pl.col('quarter').str.slice(0, 4).cast(pl.Int64).alias('year'),
            pl.col('quarter').str.slice(5, 1).cast(pl.Int64).alias('q_num')
        ])
        .sort([key_column, 'quarter'])
        .with_columns(
            pl.col('quarterly_units').cum_sum().over(key_column).alias('sum_units')
        )
        .sort(by = ['quarter', 'quarterly_units'], descending=[False, True])
    )
    return quarterly_sales


def yearly_sales(src_df: pl.DataFrame, 
                 begin: datetime | None = None, end: datetime | None = None,
                 maker_mode:bool = False) -> pl.DataFrame:
    """
    年毎の販売台数と、その年までの累計販売台数（sum_units）を集計して返す。

    Args:
        src_df: load_hard_sales()の戻り値のDataFrame
        begin: 集計開始日
        end: 集計終了日
        maker_mode: Trueの場合、メーカー毎に集計。Falseの場合、ハード毎に集計。

    Returns:
        pl.DataFrame: 年毎の販売台数（yearly_units）と累計販売台数（sum_units）を含むDataFrame
        
        DataFrameのカラム詳細:
        - year (Int16): report_dateの年
        - hw (String): ゲームハードの識別子 (maker_mode=Falseの場合) 
        - maker_name (String): メーカー名 (maker_mode=Trueの場合)
        - yearly_units (Int64): 年次販売台数
        - sum_units (Int64): その年時点での累計販売台数
    """
    df = date_filter(src_df, begin=begin, end=end)

    # 年ごとの販売台数を集計
    if maker_mode:
        key_column = 'maker_name'
    else:
        key_column = 'hw'

    yearly_sales = (
        df.group_by(['year', key_column])
        .agg(pl.col('units').sum().alias('yearly_units'))
        .sort([key_column, 'year'])
        .with_columns(
            pl.col('yearly_units').cum_sum().over(key_column).alias('sum_units')
        )
        .sort(by = ['year', 'yearly_units'], descending=[False, True])
    )

    return yearly_sales


def yearly_maker_sales(src_df: pl.DataFrame, 
                begin: datetime | None = None, end: datetime | None = None) -> pl.DataFrame:
    """
    年毎、メーカー毎の販売台数を集計して返す。

    Args:
        src_df: load_hard_sales()の戻り値のDataFrame
        begin: 集計開始日
        end: 集計終了日

    Returns:
        pl.DataFrame: 年毎、メーカー毎の販売台数を含むDataFrame

        DataFrameのカラム詳細:
        - year (Int16): report_dateの年
        - maker_name (String): メーカー名
        - yearly_units (Int64): 年次販売台数
    """
    df = yearly_sales(src_df, begin=begin, end=end, maker_mode=True)
    ## dfからsum_unitsを削除する
    return df.drop('sum_units')


def delta_yearly_sales(df: pl.DataFrame) -> pl.DataFrame:
    """
    販売開始からの経過年毎の販売台数と、その経過年までの累計販売台数（sum_units）を集計して返す。

    Args:
        df: load_hard_sales()の戻り値のDataFrame
    
    Returns:
        pl.DataFrame: 経過年毎の販売台数（yearly_units）と累計販売台数（sum_units）を含むDataFrame
        
        DataFrameのカラム詳細:
        - delta_year (Int16): 発売年から何年後か(同じ年なら0)
        - hw (String): ゲームハードの識別子
        - yearly_units (Int64): 経過年次販売台数
        - sum_units (Int64): その経過年時点での累計販売台数
    """
    # 年ごとの販売台数を集計
    delta_yearly_sales = (
        df.group_by(['delta_year', 'hw'])
        .agg(pl.col('units').sum().alias('yearly_units'))
        .sort(['hw', 'delta_year'])
        .with_columns(
            pl.col('yearly_units').cum_sum().over('hw').alias('sum_units')
        )
        .sort(by = ['delta_year', 'yearly_units'], descending=[False, True])
    )
    return delta_yearly_sales

