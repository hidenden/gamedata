import altair as alt
# 標準ライブラリ
from datetime import datetime, date
from typing import List

# サードパーティライブラリ
import polars as pl

# プロジェクト内モジュール
# プロジェクト内モジュール
from . import hard_sales as hs
from . import hard_sales_long as hsl
from . import hard_info as hi
from . import hard_event as he
from . import chart_config as cc


def _chart_bar_sales(
    src_df: pl.DataFrame,
    alt_x:alt.X,
    alt_y:alt.Y,
    color:alt.Color,
    ymin: int = 0,
    ymax :int | None = None,
    title :str | None = None,
    xoffset:str | None = None,
) -> alt.Chart:
    """売上の棒グラフを作成する内部関数

    Args:
        src_df: データフレーム
        alt_x: X軸の設定
        alt_y: Y軸の設定
        color: カラーの設定
        ymin: Y軸の最小値
        ymax: Y軸の最大値（オプション）
        title: チャートのタイトル（オプション）

    Returns:
        alt.Chart: 売上の棒グラフ
    """

    # Y上限の設定
    if ymax is not None:
        alt_y = alt_y.scale(domain=[ymin, ymax])

    base_chart = alt.Chart(src_df).encode(
        x=alt_x,
        y=alt_y,
        color=color,
    )
    chart = base_chart.mark_bar().properties(
        width=cc.CONFIG['width'], 
        height=cc.CONFIG['height'])

    if title is not None:
        chart = chart.properties(title=title)
    if xoffset is not None:
        chart = chart.encode(xOffset=xoffset)
    return chart


def chart_bar_sales(hw:list[str] = [], 
                            begin:datetime | date | None = None, 
                            end:datetime | date | None = None,
                            mode:str = "month",
                            stacked:bool=False,
                            ymax:int | None = None,

                            ) -> alt.Chart:
    """ハード別の月次売上棒グラフを作成する関数
    Args:
        hw: ハードのリスト
        begin: データの開始日（オプション）
        end: データの終了日（オプション）
        mode: 集計の単位（"month", "quarter", または"year"、デフォルトは"month"）
        stacked: 棒グラフを積み上げ表示するかどうか（デフォルトはFalse）
        ymax: Y軸の最大値（オプション）

    Returns:
        alt.Chart: ハード別の月次売上棒グラフ
    """
    df_all = hs.load_hard_sales()

    if mode == "month":
        src_df = hsl.monthly_sales_long(df_all, hw=hw, begin=begin, end=end)
        alt_x = alt.X('year_month:O', title='年月',
                axis=alt.Axis(format="%Y-%m", formatType='time'))
        alt_y = alt.Y('monthly_units:Q', title='販売台数')
        title = "月次販売台数"
    elif mode == "quarter":
        src_df = hsl.quarterly_sales_long(df_all, hw=hw, begin=begin, end=end)
        alt_x = alt.X("quarter:O", title="四半期")
        alt_y = alt.Y("quarterly_units:Q", title="販売台数")
        title = "四半期販売台数"
    elif mode == "year":
        src_df = hsl.yearly_sales_long(df_all, hw=hw, begin=begin, end=end)
        alt_x = alt.X("year:O", title="年")
        alt_y = alt.Y("yearly_units:Q", title="販売台数")
        title = "年次販売台数"
    else:
        raise ValueError("modeは'month', 'quarter', または 'year'のいずれかでなければなりません")
    
        # ハードウェアごとの色を取得
    current_hw = hs.get_hw(src_df)
    hw_colors = hi.get_hard_colors(current_hw)
    alt_color = alt.Color("hw:N", title='ハード',
                scale=alt.Scale(domain=current_hw, range=hw_colors))
    xoffset = 'hw:N' if not stacked else None


    return _chart_bar_sales(
        src_df=src_df,
        alt_x=alt_x,
        alt_y=alt_y,
        color=alt_color,
        title=title,
        ymax=ymax,
        ymin=0,
        xoffset=xoffset
    )


def chart_bar_hwsales_by_year(hw:str, 
                            begin:datetime | date | None = None, 
                            end:datetime | date | None = None,
                            mode:str = "month",
                            ymax:int | None = None) -> alt.Chart:
    """
    指定したハードウェアの月間販売台数を年別に棒グラフで表示する

    Args:
        hw: ハードウェア名
        begin: データの開始日（オプション）
        end: データの終了日（オプション）
        mode: 集計の単位（"month", "quarter",デフォルトは"month"）
        ymax: Y軸の最大値（オプション）
    Returns:
        alt.Chart: 年別の月間販売台数を表示する棒グラフ
    """
    df_all = hs.load_hard_sales()

    if mode == "month":
        src_df = hsl.monthly_sales_long(df_all, hw=[hw], begin=begin, end=end)
        alt_x = alt.X('month:O', title='月')
        alt_y = alt.Y('monthly_units:Q', title='販売台数')
        title = "月間販売推移"
    elif mode == "quarter":
        src_df = hsl.quarterly_sales_long(df_all, hw=[hw], begin=begin, end=end)
        alt_x = alt.X("q_num:O", title="四半期")
        alt_y = alt.Y("quarterly_units:Q", title="販売台数")
        title = "四半期販売推移"
    else:
        raise ValueError("modeは'month'または'quarter'のいずれかでなければなりません")

    alt_color = alt.Color("year:O", title='年')
    xoffset = 'year:O'
    
    return _chart_bar_sales(
        src_df=src_df,
        alt_x=alt_x,
        alt_y=alt_y,
        color=alt_color,
        title=title,
        ymax=ymax,
        xoffset=xoffset
    )

def chart_hbar_yearly_share_by_maker(
    begin:datetime | date | None = None,
    end: datetime | date | None = None
) -> alt.Chart:
    """メーカー別の年次シェアを100%積み上げ横棒グラフで表示する。

    Args:
        begin: 集計開始日（オプション）。
        end: 集計終了日（オプション）。

    Returns:
        alt.Chart: 年ごとのメーカーシェアと割合ラベルを表示するチャート。
    """
    _df_all = hs.load_hard_sales()
    _df = hsl.maker_long(_df_all, begin_year=begin, end_year=end)
    _df = (
        _df
        .with_columns(
        ((pl.col('yearly_pct').cum_sum().over('year') - pl.col('yearly_pct') / 2) / 100)
        .alias('mid_point'),
        (pl.col('yearly_pct').round(1).cast(pl.String) + '%')
        .alias('pct_label'),
        )
    )

    maker_list = hs.get_maker(_df)
    maker_color = hi.get_maker_colors(maker_list)
    _base = alt.Chart(_df).encode(
        y=alt.Y('year:O', sort='descending', title='年'),
        x=alt.X('yearly_pct:Q', stack='normalize', title='メーカーシェア'),
        color=alt.Color('maker_name:N', title='メーカー',
                        scale=alt.Scale(domain=maker_list, range=maker_color)),
        order=alt.Order('mid_point:Q'),
    )

    _bars = _base.mark_bar()
    _text = _base.mark_text(size=12, baseline='middle').encode(
        detail='maker_name:N',
        color=alt.value('white'),
        text=alt.Text('pct_label:N'),
        x=alt.X('mid_point:Q'),
    )
    return (_bars + _text).properties(
        width=cc.CONFIG['width'], height=cc.CONFIG['height'],
        title='年間シェア推移')
    