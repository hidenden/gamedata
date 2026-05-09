import marimo

__generated_with = "0.23.3"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import altair as alt
    # 標準ライブラリ
    from datetime import datetime, timedelta, date
    from typing import List, Optional

    # サードパーティライブラリ
    import polars as pl
    # import polars.selectors as cs

    # プロジェクト内モジュール
    import gamedata as g

    return List, alt, date, datetime, g, mo, pl


@app.cell
def _(alt, pl):
    def inner_chart_sales(
        src_df: pl.DataFrame,
        alt_x:alt.X,
        alt_y:alt.Y,
        color:alt.Color,
        ymin: int = 0,
        ymax :int | None = None,
        title :str | None = None,
        event_joinner = lambda df: df,
        with_point:bool = True
    ) -> alt.Chart:
        """売上のチャートを作成する関数

        Args:
            src_df: データフレーム
            event_joinner: イベント結合関数
            labeler: ラベル付け関数（オプション）

        Returns:
            alt.Chart: 売上のチャート
        """
        # データの取得とイベントの結合
        df: pl.DataFrame = event_joinner(src_df)
    
        # Y上限の設定
        if ymax is not None:
            alt_y = alt_y.scale(domain=[ymin, ymax])

        # チャートの作成
        base_chart = (
            alt.Chart(df)
            .encode(
                x=alt_x,
                y=alt_y,
                color=color
            )
        )
        chart = base_chart.mark_line()
        if with_point:
            chart += base_chart.mark_point()

        # dfがカラム evenv_name を持っている場合は、mark_text()でイベント名を表示する
        if "event_name" in df.columns:
            event_chart = base_chart.transform_filter(
                alt.datum.event_name != None).mark_text(
                align="center",
                baseline="middle",
                dx=10,
                dy=-10,
                limit=80
            ).encode(text="event_name:N")
            chart += event_chart
        
        chart = chart.properties(width=960, height=480) 
        if title is not None:
            chart = chart.properties(title=title)

        return chart


    return (inner_chart_sales,)


@app.cell
def _(List, alt, date, datetime, g, inner_chart_sales, pl):
    def chart_sales(hw: List[str] = [], mode: str = "week",
                    begin: datetime | date | None = None, end: datetime | date | None = None,
                    ymin: int = 0,
                    ymax: int | None = None,
                    event_mask: g.EventMasks | None = None
    ) -> alt.Chart:
        """売上のチャートを作成する関数

        Args:
            hw: ハードウェアのリスト
            mode: 集計モード（例: "week", "month"）
            begin: 集計開始日
            end: 集計終了日
            event_mask: イベントマスク（オプション）

        Returns:
            alt.Chart: 売上のチャート
        """
        # データソースの定義
        src_df = g.load_hard_sales()
    
        if mode == "month":
            df = g.monthly_sales_long(src_df, hw=hw, begin=begin, end=end)
            alt_x = alt.X("year_month:T", title="年月")
            alt_y = alt.Y("monthly_units:Q", title="販売台数")
            title = "月次販売台数"
        elif mode == "quarter":
            df = g.quarterly_sales_long(src_df, hw=hw, begin=begin, end=end)
            alt_x = alt.X("quarter:O", title="四半期")
            alt_y = alt.Y("quarterly_units:Q", title="販売台数")
            title = "四半期販売台数"
        elif mode == "year":
            df = g.yearly_sales_long(src_df, hw=hw, begin=begin, end=end)
            alt_x = alt.X("year:O", title="年")
            alt_y = alt.Y("yearly_units:Q", title="販売台数")
            title = "年次販売台数"
        else:
            df = g.sales_long(src_df, hw=hw, begin=begin, end=end)
            alt_x = alt.X("report_date:T", title="日付")
            alt_y = alt.Y("units:Q", title="販売台数")
            title = "週次販売台数"

        # ハードウェアごとの色を取得
        current_hw = g.get_hw(df, False)
        hw_colors = g.get_hard_colors(current_hw)
        alt_color = alt.Color("hw:N", scale=alt.Scale(domain=current_hw, range=hw_colors))

        # イベント結合関数の定義
        def event_joinner(df: pl.DataFrame) -> pl.DataFrame:
            if (event_mask is not None) and (mode == "week"):
                event_df = g.mask_event(g.load_hard_event(), event_mask)
                df_with_event = df.join(other=event_df, left_on=["report_date", "hw"], 
                                                   right_on=["report_date", "hw"], how="left")
                return df_with_event
            else:
                return df

        # チャートの作成
        return inner_chart_sales(src_df=df, 
                                alt_x=alt_x, 
                                alt_y=alt_y, 
                                ymax = ymax,
                                ymin = ymin,
                                color=alt_color,
                                title=title,    
                                event_joinner=event_joinner)


    return (chart_sales,)


@app.cell
def _(chart_sales, datetime, g, mo):
    _begin = datetime(2022, 9, 1)
    _end = datetime(2026, 4, 30)

    mo.ui.altair_chart(
    chart_sales(begin=_begin, end=_end, mode="week", 
                            event_mask=g.EVENT_MASK_MIDDLE).interactive()
    )
    return


@app.cell
def _(List, alt, g, inner_chart_sales):
    def chart_sales_with_offset(hw_periods: List[dict] = [], 
                                end:int = 52,
                                ymax:int | None=None,
                                ymin:int = 0
                                ) -> alt.Chart:
        """
        各ハードウェアの異なる期間の販売台数推移を、各期間の開始点を揃えてプロットする
        Args:
            hw_periods: プロットしたいハードウェア名と期間のリスト。各要素は以下のキーを持つ辞書:
                - 'hw' (str, required): ハードウェアの識別子
                - 'begin' (datetime, required): 集計開始日
                - 'label' (str, optional): 列名（省略時はhw名を使用）
            end: 各期間の最大週数（デフォルトは52週）
            ymax: Y軸の上限値（省略時は自動調整）
        Returns:
            alt.Chart: 作成されたAltairチャートオブジェクト
        """

        # データソースの定義
        df_all = g.load_hard_sales()
        src_df = g.sales_with_offset_long(df_all, hw_periods=hw_periods, end=end)

        alt_x = alt.X("offset_week:Q", title="週数")
        alt_y = alt.Y("units:Q", title="販売台数")
        alt_color = alt.Color("label:N", title="機種:時期")
        event_joinner = lambda df: df  # イベント結合は行わない
        # チャートの作成
        return inner_chart_sales(src_df=src_df, 
                                alt_x=alt_x, 
                                alt_y=alt_y, 
                                ymax = ymax,
                                ymin = ymin,
                                title="週販推移比較",
                                color=alt_color)




    return (chart_sales_with_offset,)


@app.cell
def _(chart_sales_with_offset, datetime, mo):
    chart_offset = chart_sales_with_offset(
      hw_periods=[
          {'hw': 'PS5', 'begin': datetime(2023,3,1)},
          {'hw': 'PS5', 'begin': datetime(2024,3,1)},
          {'hw': 'PS5', 'begin': datetime(2025,3,1)},
          {'hw': 'PS5', 'begin': datetime(2026,3,1)},
          ],
      end = 20)

    mo_chart_offset = mo.ui.altair_chart(chart_offset)
    mo_chart_offset
    return


@app.cell
def _(List, alt, date, datetime, g, inner_chart_sales, pl):
    def chart_cumulative_sales(
        hw: List[str] = [], mode: str = "week",
        begin: datetime | date | None = None, end: datetime | date | None = None,
        ymin: int = 0,
        ymax: int | None = None,
        event_mask: g.EventMasks | None = None
    ) -> alt.Chart:
        """累計販売台数のチャートを作成する関数
        Args:
            hw: ハードウェアのリスト
            mode: 集計モード（例: "week", "month"）
            begin: 集計開始日
            end: 集計終了日
            event_mask: イベントマスク（オプション）
        Returns:
            alt.Chart: 累計販売台数のチャート
        """
        df_all = g.load_hard_sales()
        src_df = g.cumulative_sales_long(df_all, hw=hw, mode=mode,
                                                    begin=begin, end=end)
        alt_x = alt.X("report_date:T", title="販売年月")
        alt_y = alt.Y("sum_units:Q", title="累計販売台数")
        title = "累計販売台数"

        # ハードウェアごとの色を取得
        current_hw = g.get_hw(src_df, False)
        hw_colors = g.get_hard_colors(current_hw)
        alt_color = alt.Color("hw:N", scale=alt.Scale(domain=current_hw, range=hw_colors))

        def event_joinner(df: pl.DataFrame) -> pl.DataFrame:
            if (event_mask is not None) and (mode == "week"):
                event_df = g.mask_event(g.load_hard_event(), event_mask)
                df_with_event = df.join(other=event_df, left_on=["report_date", "hw"], 
                                                   right_on=["report_date", "hw"], how="left")
                return df_with_event
            else:
                return df

        return inner_chart_sales(src_df=src_df, 
                                alt_x=alt_x, 
                                alt_y=alt_y, 
                                ymax = None,
                                ymin = ymin,
                                color=alt_color,
                                title="累計販売台数",    
                                event_joinner=event_joinner,
                                with_point=False)
    

    chart_cumulative_sales(hw=["NSW", "PS5", "NS2", "XSX"], mode="week", 
                            begin=datetime(2017,3,3),
                            event_mask=g.EVENT_MASK_LONG)


    return


@app.cell
def _(List, alt, g, inner_chart_sales, mo, pl):
    def chart_cumulative_sales_by_delta(
        hw: List[str] = [], mode: str = "week",
        begin: int | None = None, end: int | None = None,
        ymin: int = 0,
        ymax: int | None = None,
        event_mask: g.EventMasks | None = None
    ) -> alt.Chart:
        """累計販売台数のチャートを作成する関数
        Args:
            hw: ハードウェアのリスト
            mode: "week"、"month"または"year"を指定。週単位の集計なら"week"、月単位の集計なら"month"、年単位の集計なら"year"を指定。
            begin: 集計開始（経過期間の最小値）
            end: 集計終了（経過期間の最大値）
            event_mask: イベントマスク（オプション）
        Returns:
            alt.Chart: 相対累計販売台数のチャート
        """
        df_all = g.load_hard_sales()
        src_df = g.cumulative_sales_by_delta_long(df_all, hw=hw, mode=mode,
                                                            begin=begin, end=end)
        alt_y = alt.Y("sum_units:Q", title="累計販売台数")
        title = "累計販売台数"
        if mode == "month":
            alt_x = alt.X("delta_month:Q", title="月数")
        elif mode == "year":
            alt_x = alt.X("delta_year:Q", title="年数")
        else:
            alt_x = alt.X("delta_week:Q", title="週数", axis=alt.Axis(grid=True, tickCount=20))

        # ハードウェアごとの色を取得
        current_hw = g.get_hw(src_df, False)
        hw_colors = g.get_hard_colors(current_hw)
        alt_color = alt.Color("hw:N", scale=alt.Scale(domain=current_hw, range=hw_colors))

        def event_joinner(df: pl.DataFrame) -> pl.DataFrame:
            if (event_mask is not None) and (mode == "week"):
                event_df = g.mask_event(g.load_hard_event(True), event_mask)
                df_with_event = df.join(other=event_df, left_on=["delta_week", "hw"], 
                                                   right_on=["delta_week", "hw"], how="left")
                return df_with_event
            else:
                return df

        return inner_chart_sales(src_df=src_df, 
                                alt_x=alt_x, 
                                alt_y=alt_y, 
                                ymax = None,
                                color=alt_color,
                                title="累計販売台数",    
                                event_joinner=event_joinner,
                                with_point=False)
    

    mo.ui.altair_chart(chart_cumulative_sales_by_delta(hw=["NS2", "NSW", "PS5", "3DS", "DS", "GBA", "PS2", "Wii"], mode="week", 
                            end=80,
                            event_mask=g.EVENT_MASK_SHORT))


    return


if __name__ == "__main__":
    app.run()
