# GameData グラフ描画用ユーティリティ関数群
from typing import List
from pyspark.sql import functions as F
from pyspark.sql.window import Window
from pyspark.sql.dataframe import DataFrame
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

def plot_monthly_sales_by_hw(df:DataFrame, hw_name:str, years:List[int]) -> None:
    filtered_data = df.filter(df["hw"] == hw_name)

    # 年ごとにデータをグループ化し、月別の販売台数を集計
    sales_by_month = filtered_data.groupBy("year", "month").agg(F.sum("units").alias("monthly_units"))

    # PandasのDataFrameに変換
    sales_by_month_pd = sales_by_month.toPandas()

    # 年ごとのデータフレームを格納するリスト
    yearly_dfs = []

    # 指定された年ごとにデータフレームを作成し、リストに追加
    for year in years:
        yearly_data = sales_by_month_pd[sales_by_month_pd['year'] == year]
        yearly_dfs.append(yearly_data)

    # 棒グラフを描画
    plt.figure(figsize=(12, 6))
    width = 0.1

    # 指定された年ごとに棒グラフを描画し、隣り合わせに配置
    for idx, yearly_df in enumerate(yearly_dfs):
        plt.bar(yearly_df['month'] + idx * width, yearly_df['monthly_units'], width=width, label=f'{years[idx]}')

    # x軸の調整と凡例の表示
    plt.xticks(range(1, 13))
    plt.xlabel("Month")
    plt.ylabel("Sales")
    plt.title(f'Monthly Sales of {hw_name} by Year')
    plt.legend()

    # Y軸のメモリを整数表示に変更
    ax = plt.gca()
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: '{:,.0f}'.format(x)))

    plt.show()

def plot_weekly_sales_by_hw(df:DataFrame, hw_name:str, years:List[int]) -> None:
    filtered_data = df.filter(df["hw"] == hw_name)

    # 年ごとにデータをグループ化し、週別の販売台数を集計
    sales_by_week = filtered_data.groupBy("year", "week").agg(F.sum("units").alias("weekly_units"))

    # PandasのDataFrameに変換
    sales_by_week_pd = sales_by_week.toPandas()

    # 年ごとのデータフレームを格納するリスト
    yearly_dfs = []

    # 指定された年ごとにデータフレームを作成し、リストに追加
    for year in years:
        yearly_data = sales_by_week_pd[sales_by_week_pd['year'] == year]
        yearly_dfs.append(yearly_data)

    # 棒グラフを描画
    plt.figure(figsize=(12, 6))
    width = 0.1

    # 指定された年ごとに棒グラフを描画し、隣り合わせに配置
    for idx, yearly_df in enumerate(yearly_dfs):
        plt.bar(yearly_df['week'] + idx * width, yearly_df['weekly_units'], width=width, label=f'{years[idx]}')

    # x軸の調整と凡例の表示
    plt.xticks(range(1, 53))
    plt.xlabel("Week")
    plt.ylabel("Sales")
    plt.title(f'Weekly Sales of {hw_name} by Year')
    plt.legend()

    # Y軸のメモリを整数表示に変更
    ax = plt.gca()
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: '{:,.0f}'.format(x)))

    plt.show()
