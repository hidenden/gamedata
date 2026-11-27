# /// script
# [tool.marimo.display]
# theme = "system"
# ///

import marimo

__generated_with = "0.23.4"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import altair as alt
    # 標準ライブラリ
    from datetime import datetime, timedelta, date

    # サードパーティライブラリ
    import polars as pl
    # import polars.selectors as cs

    # プロジェクト内モジュール
    import gamedata as g
    g.set_dispfunc(func=None)
    return alt, date, g, mo, pl


@app.cell
def _(g):
    df_all = g.load_hard_sales()
    df_all
    return (df_all,)


@app.cell
def _(date, df_all, g):
    df1 = g.date_filter(df_all, 
    begin=date(2023, 1, 1), 
    end=date(2026, 3, 31))
    df1
    return (df1,)


@app.cell
def _(alt, df1, mo):

    base = alt.Chart(df1).encode(
            x='report_date:T',
            y='units:Q',
            color='hw:N',
        )

    chart = mo.ui.altair_chart(
        ((base.mark_point() + base.mark_line())).properties(
            width=1000,
            height=500,
            title='Units Sold Over Time by Hardware'
        )
    )
    chart
    return (chart,)


@app.cell
def _(chart):
    type(chart.value)
    return


@app.cell
def _(alt, chart, mo):
    df2 = chart.value
    base2 = alt.Chart(df2).encode(
            x='report_date:T',
            y='units:Q',
            color='hw:N',
        )
    chart2 = mo.ui.altair_chart(
        ((base2.mark_point() + base2.mark_line())).properties(
            width=1000,
            height=500,
            title='Units Sold Over Time by Hardware (from Chart Data)'
        )
    )
    chart2
    return


@app.cell
def _(df_all, g):
    rolled_df = df_all
    rolled_df
    return (rolled_df,)


@app.cell
def _(alt, mo, pl, rolled_df):
    fold_cols = ['units', 'ma4w','ma13w', 'ma52w']

    ps5_df = rolled_df.filter(pl.col('hw') == 'PS5')
    base_ps5 = alt.Chart(ps5_df).transform_fold(
        fold_cols,
        as_=['metric', 'value']
    ).encode(  
            x='report_date:T',
            y='value:Q',
            color='metric:N',
    )

    chart_ps5 = mo.ui.altair_chart(
        (base_ps5.mark_point() + base_ps5.mark_line()).properties(
            width=1000,
            height=500,
            title='PS5 Units and Moving Averages Over Time'
        )
    )
    chart_ps5
    return (chart_ps5,)


@app.cell
def _(chart_ps5):
    # chart_ps5.valueの型を表示
    type(chart_ps5.value)
    return


@app.cell
def _(chart_ps5):
    dfx = chart_ps5.value
    dfx
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## データの段階でLong形式に変換する

    polarsのunpivotを使用して、データをLong形式に変換します。これにより、Altairでのグラフ作成が容易になります。
    polars側で整えたデータをChartに渡すことで、Chart.valueで選択範囲のデータが適切に取得できるか確認します｡

    pivotで縦に並ぶカラム
    - units (販売台数)
    - ma4w (4週間移動平均)
    - ma13w (13週間移動平均)
    - ma52w (52週間移動平均)

    値を保持するカラム
    - value

    縦のカラムのタイプを保持するカラム
    - metric

    他のカラムは元の状態を維持する｡

    入力Dataframe: rolled_df
    出力Dataframe: long_df
    """)
    return


@app.cell
def _(rolled_df):
    rolled_df
    return


@app.cell
def _(rolled_df):
    long_df = rolled_df.unpivot(
        index=['report_date', 'hw'],
        on=['units', 'ma4w','ma13w', 'ma52w', 'sum_units'],
        variable_name='metric',
        value_name='value'
    ).sort(['report_date', 'hw'])
    return (long_df,)


@app.cell
def _(long_df):
    long_df
    return


@app.cell
def _(g, mo):
    hwlist = g.get_hw_all()
    hwdropdown = mo.ui.dropdown(options=hwlist, value="NSW")
    hwdropdown
    return (hwdropdown,)


@app.cell
def _(alt, hwdropdown, long_df, mo, pl):
    hw_long_df = long_df.filter(pl.col('hw') == hwdropdown.value).filter(pl.col('metric') != 'sum_units')


    base_long = alt.Chart(hw_long_df).encode(  
            x='report_date:T',
            y='value:Q',
            color='metric:N',
    )

    chart_long = mo.ui.altair_chart(
        (base_long.mark_point() + base_long.mark_line()).properties(
            width=1000,
            height=500,
            title='HW Units and Moving Averages Over Time'
        )
    )
    chart_long
    return (chart_long,)


@app.cell
def _(chart_long):
    selected_df =  chart_long.value
    return (selected_df,)


@app.cell
def _(alt, mo, selected_df):
    c2 = alt.Chart(selected_df).mark_line().encode(
        x='report_date:T',
        y='value:Q',
        color='metric:N'
    ).properties(
        width=1000,
        height=500,
        title='Selected HW Units and Moving Averages Over Time (from Chart Data)'
    )

    chartZ = mo.ui.altair_chart(c2)
    chartZ
    return


if __name__ == "__main__":
    app.run()
