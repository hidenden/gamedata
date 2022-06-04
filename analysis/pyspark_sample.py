#!/usr/bin/env python3

# from pyspark.sql.functions import * とする場合もありますが、
# Fで関数の名前空間を明示した方がわかりやすくて好きです。
# ただ、FだとPEP8に違反していますが。。。
from pyspark.sql import functions as F
from pyspark.sql.types import FloatType, TimestampType, StringType
from pyspark.sql.window import Window
from pyspark import SparkContext
from pyspark.sql import SparkSession
from pyspark.sql.utils import AnalysisException
import pandas as pd
import numpy as np
import datetime
import re
import matplotlib.pyplot as plt
import matplotlib as mpl
import japanize_matplotlib

# spark initialization
spark = SparkSession.builder.appName("gamedata").getOrCreate()

df = spark.read.parquet("../transform/hard_spark")
print(df.schema)

df_hw = df.select("hw").distinct()
for r in df_hw.collect():
    print(r['hw'])

print(df_hw.count())


