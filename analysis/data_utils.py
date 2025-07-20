# GameData分析用のユーティリティ関数群
from pyspark.sql import functions as F
from pyspark.sql import SparkSession
from pyspark.sql.window import Window
from pyspark.sql.dataframe import DataFrame
from pyspark.sql import Row
from typing import List, Optional

def load_hard_sales() -> DataFrame:
    # spark initialization
    spark = SparkSession.builder.appName("gamedata").getOrCreate()
    # load master database
    return spark.read.parquet("../database/parquet/hard_sales")


# 累計販売台数が指定の値を超えた最初の週を見つける関数
def extract_week_reached_units(hard_sales:DataFrame, threshold_units:int) -> DataFrame:
    # 累計販売台数が指定の値を超えた最初の週を見つけるためのウィンドウ定義
    window_spec = Window.partitionBy("hw").orderBy("begin_date")

    # 累計販売台数が指定の値を超えた週を見つける
    sales_with_reached_units = hard_sales.withColumn(
        "reached_units",
        F.when(hard_sales["sum_units"] >= threshold_units, F.lit(1)).otherwise(F.lit(0))
    )

    # 各ゲーム機で指定の台数に到達回数が1回目の週だけ抽出
    sales_with_reached_units_flag = sales_with_reached_units.withColumn(
        "reach_count", F.sum("reached_units").over(window_spec)
    )

    reached_weeks = sales_with_reached_units_flag.filter(
        sales_with_reached_units_flag["reach_count"] == 1
    ).select(
        "hw", "maker", "full_name", "begin_date", "end_date",
        "year", "month", "launch_day", "launch_year", "sum_units", "delta_week"
    )
    return reached_weeks

def extract_by_date(df:DataFrame, date_str:str, hw_names:Optional[List[str]] = None) -> DataFrame:
    target_date = F.to_date(F.lit(date_str))
    out_df = df.filter(F.col("begin_date") <= target_date).filter(target_date <= F.col("end_date"))
    if hw_names != None:
        out_df = out_df.filter(out_df['hw'].isin(*hw_names))

    return out_df

def extract_latest(df:DataFrame) -> DataFrame:
    target_date = df.orderBy(F.desc("begin_date")).first()["begin_date"]
    return df.filter(F.col("begin_date") == target_date)
