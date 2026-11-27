# /// script
# [tool.marimo.display]
# theme = "system"
# ///

import marimo

__generated_with = "0.23.15"
app = marimo.App(width="medium")

with app.setup:
    # 標準ライブラリ
    from datetime import date, datetime

    import marimo as mo
    import altair as alt

    # サードパーティライブラリ
    import polars as pl

    # import polars.selectors as cs
    # プロジェクト内モジュール
    import gamedata as g


@app.cell
def md_alt_title():
    mo.md(r"""
    # 盃休みの背景を偲ぶ

    2011/08/11 12:48に2chゲハ板で歴史に残る発言がなされました｡

    ***「盃休みとか一族集まるんだからみんなで大テレビでPS3でもやるわ普通はw」***

    - 盃休み
    - 一族
    - 大テレビ

    当時も､どこからツッコメばいいのか判断に苦しむ発言として､ゲハ住民の心に強く印象付けられました｡
    しかし､この発言は当時のPS3の苦境に心を痛めたPSファンの心情を表すものとして､
    後世に語り継がれることとなりました｡

    このレポートでは､そんなPSファンを偲び､当時のPS3の状況を振り返ることで､
    盃休み発言の背景を考察していきます｡
    """)
    return


@app.cell
def _():
    df_all = g.load_hard_sales()
    df_all
    return


@app.cell
def md_market_position_intro():
    mo.md(r"""
    ## 「みんなでPS3」は市場全体から見ると普通だったか

    「一族が大テレビに集まり、みんなでPS3を遊ぶ」という情景は、2011年のゲーム機市場においてどの程度「普通」だったのでしょうか。
    ここでは同時期に販売されていた据置機の **PS3・Wii・Xbox 360** に、携帯機の **PSP・ニンテンドー3DS・ニンテンドーDS** を加えて比較します。

    まず2011年の1年間に消費者が実際に選んだハードを確認し、次に各機種が国内市場で最終的に積み上げた累計販売台数を見ます。
    """)
    return


@app.cell
def calc_market_position_data():
    # 2011年当時に競合していた据置機と携帯機を比較対象にする
    report_hws = ["PS3", "Wii", "XB360", "PSP", "3DS", "DS", "Vita"]

    # gamedataの集計関数を使い、2011年の年間販売台数と対象機種内の構成比を求める
    _report_all = g.load_hard_sales()
    _report_2011_raw = g.yearly_sales(
        _report_all,
        begin=date(2011, 1, 1),
        end=date(2011, 12, 31),
    ).filter(pl.col("hw").is_in(report_hws))
    _report_2011_total = _report_2011_raw.select(pl.col("yearly_units").sum()).item()
    report_2011_table = (
        _report_2011_raw
        .with_columns(
            (pl.col("yearly_units") / _report_2011_total * 100).round(1).alias("構成比(%)")
        )
        .with_columns(pl.col("hw").replace(g.get_hard_dict()).alias("ハード"))
        .select(
            "ハード",
            pl.col("yearly_units").alias("2011年販売台数"),
            "構成比(%)",
        )
        .sort("2011年販売台数", descending=True)
    )

    # 各機種の最終記録から、生涯累計販売台数と集計終了日を取り出す
    report_cumulative_table = (
        g.extract_total(_report_all, compact=True)
        .filter(pl.col("hw").is_in(report_hws))
        .with_columns(pl.col("hw").replace(g.get_hard_dict()).alias("ハード"))
        .select(
            "ハード",
            pl.col("sum_units").alias("累計販売台数"),
            pl.col("report_date").alias("集計終了日"),
        )
        .sort("累計販売台数", descending=True)
    )
    return report_2011_table, report_cumulative_table, report_hws


@app.cell
def md_2011_sales():
    mo.md(r"""
    ### 2011年の販売台数

    据置機だけを見るとPS3は首位でした。しかし市場全体へ視野を広げると、販売の中心は携帯機です。
    「みんなで大テレビ」という据置機中心の情景と、実際の購買行動には大きな隔たりがありました。
    """)
    return


@app.cell
def chart_2011_sales(report_hws):
    # gamedataの既存棒グラフを使い、対象機種の2011年販売台数を比較する
    g.chart_bar_sales(
        hw=report_hws,
        begin=date(2011, 1, 1),
        end=date(2011, 12, 31),
        mode="year",
        stacked=False,
        size=(720, 420),
    )
    return


@app.cell
def table_2011_sales(report_2011_table):
    # 台数だけでなく対象6機種内の構成比も表で確認する
    report_2011_table
    return


@app.cell
def md_cumulative_sales():
    mo.md(r"""
    ### 各機種が最終的に積み上げた累計販売台数

    2011年の断面だけでは、各機種が市場に残した規模までは分かりません。
    そこで発売から集計終了までの累計推移と、データに記録された最終累計を比較します。

    携帯機のDSとPSPが巨大な普及台数を築いた一方、据置機ではWiiとPS3が市場を分け合いました。
    PS3は決して売れていないハードではありませんが、「誰もが一家で遊ぶ普通の選択」と呼べるほど市場を独占していたわけでもありません。
    """)
    return


@app.cell
def chart_cumulative_sales(report_hws):
    # gamedataの既存累計グラフで、各機種が国内市場に普及した過程を示す
    _cumulative_sales_base = g.chart_line_cumulative(
        hw=report_hws,
        begin=datetime(2006, 1, 1),
        end=datetime(2012, 8, 31),
        mode="week",
        multi_line=True,
        size=(720, 420),
    )

    # 盃休み発言があった2011年8月11日の位置に縦の基準線を重ねる
    g.chart_rule_xy(
        base_chart=_cumulative_sales_base,
        x=date(2011, 8, 11),
        stroke=[6, 4],
        size=3,
        color="black",
    )
    return


@app.cell
def table_cumulative_sales(report_cumulative_table):
    # 集計期間が機種ごとに異なるため、最終累計と集計終了日を併記する
    report_cumulative_table
    return


@app.cell
def md_market_position_conclusion():
    mo.md(r"""
    ### 小括

    2011年のPS3は、WiiやXbox 360を上回る**据置機の有力な選択肢**でした。この点では、発言者がPS3に期待を寄せたこと自体は市場から完全に浮いていたわけではありません。

    しかし、同年の販売首位はニンテンドー3DSで、PSPもPS3を上回っています。生涯累計でもDSとPSPという携帯機の存在感は大きく、娯楽の中心が必ずしも「一家で囲む大テレビ」だったとは言えません。

    したがって、「盃休みにPS3を遊ぶ家庭」はあり得ても、それを**“普通”と一般化したところ**に、この発言の忘れがたい飛躍があったと考えられます。
    """)
    return


@app.cell
def md_weekly_2011_intro():
    mo.md(r"""
    ## 盃休み発言の前後で週販はどう変わったか

    2011年1月から12月までのPS3とニンテンドー3DSの週間販売台数を比較します。
    3DSは2011年2月26日発売のため、年初には販売実績がありません。

    3DSは7月28日に値下げを発表し、盃休み発言と同じ**8月11日**に希望小売価格を25,000円から15,000円へ改定しました。
    グラフには「3DS値下げ発表」「3DS新価格」「盃休み発言」も注記しています。
    """)
    return


@app.cell
def chart_weekly_ps3_3ds_2011():
    # gamedataの既存週販グラフを使い、PS3と最大の競合となった3DSを通年で比較する
    # アノテーションには3DSの値下げ発表・新価格と盃休み発言を表示する
    g.chart_line_sales(
        hw=["PS3", "3DS", "Wii", "XB360", "PSP", "Vita"],
        mode="week",
        begin=date(2011, 1, 1),
        end=date(2011, 12, 31),
        annotation_level=13,
        with_point=True,
        multi_line=True,
        size=(760, 440),
    )
    return


@app.cell
def calc_ps3_3ds_cut_summaries():
    # 8月11日を含む週は8月14日集計なので、8月7日までを「以前」、8月14日からを「以後」とする
    _cut_source = (
        g.load_hard_sales()
        .filter(
            pl.col("hw").is_in(["PS3", "3DS"]),
            pl.col("report_date").is_between(date(2011, 1, 1), date(2011, 12, 31)),
        )
        .with_columns(
            pl.when(pl.col("report_date") <= date(2011, 8, 7))
            .then(pl.lit("8月11日以前"))
            .otherwise(pl.lit("8月11日以後"))
            .alias("期間")
        )
    )

    # 3DSは発売後の行だけが存在するため、以前の平均に未発売期間は含まれない
    ps3_3ds_cut_summary = (
        _cut_source
        .group_by(["期間", "hw"])
        .agg(
            pl.len().alias("集計週数"),
            pl.col("units").sum().alias("販売台数合計"),
            pl.col("units").mean().round(0).cast(pl.Int64).alias("週平均"),
            pl.col("units").median().round(0).cast(pl.Int64).alias("中央値"),
            pl.col("units").max().alias("週間最高"),
        )
        .with_columns(pl.col("hw").replace(g.get_hard_dict()).alias("ハード"))
        .select("期間", "ハード", "集計週数", "販売台数合計", "週平均", "中央値", "週間最高")
        .sort(["期間", "販売台数合計"], descending=[True, True])
    )

    # 価格改定直前4週と直後4週を揃え、短期的な変化も比較する
    _short_source = g.load_hard_sales().filter(
        pl.col("hw").is_in(["PS3", "3DS"]),
        pl.col("report_date").is_between(date(2011, 7, 17), date(2011, 9, 4)),
    ).with_columns(
        pl.when(pl.col("report_date") <= date(2011, 8, 7))
        .then(pl.lit("直前4週"))
        .otherwise(pl.lit("直後4週"))
        .alias("期間")
    )
    ps3_3ds_short_summary = (
        _short_source
        .group_by(["期間", "hw"])
        .agg(
            pl.col("units").sum().alias("4週間合計"),
            pl.col("units").mean().round(0).cast(pl.Int64).alias("週平均"),
        )
        .with_columns(pl.col("hw").replace(g.get_hard_dict()).alias("ハード"))
        .select("期間", "ハード", "4週間合計", "週平均")
        .sort(["期間", "4週間合計"], descending=[True, True])
    )
    return ps3_3ds_cut_summary, ps3_3ds_short_summary


@app.cell
def table_ps3_3ds_cut_summary(ps3_3ds_cut_summary):
    # 発言前後の長期的な販売水準を、平均だけでなく中央値と最高値でも確認する
    ps3_3ds_cut_summary
    return


@app.cell
def table_ps3_3ds_short_summary(ps3_3ds_short_summary):
    # 季節要因を小さくするため、価格改定の直前・直後を同じ4週間で比較する
    ps3_3ds_short_summary
    return


@app.cell
def md_before_august_11():
    mo.md(r"""
    ### 8月11日以前

    PS3は年初からおおむね週2万台前後で推移し、8月7日集計までの週平均は**21,981台**、中央値は**21,919台**でした。安定はしていたものの、大きな成長局面にはありませんでした。

    一方、2月末発売の3DSは発売週に大きく立ち上がった後、春から初夏にかけて急速に販売水準を落としました。それでも発売後から8月7日までの週平均は**58,759台**で、PS3を上回っています。7月31日には15,819台まで落ち込みましたが、値下げ発表後の8月7日集計では107,410台へ急伸しました。

    価格改定の適用日は8月11日なので、データ上の急増がその直前週から始まっている点には注意が必要です。少なくとも、8月11日だけを境に単純な因果関係を置くのではなく、7月28日の値下げ発表から需要や販売計上の動きが変わったと見るのが妥当です。
    """)
    return


@app.cell
def md_after_august_11():
    mo.md(r"""
    ### 8月11日以後

    3DSは新価格が適用された週から8月21日集計まで10万台超を維持し、その後も年末商戦で大きく伸びました。8月14日以後の週平均は**136,091台**、中央値も**81,806台**で、改定前の販売水準を明確に上回ります。年間販売約413万台のうち約272万台、すなわちおよそ3分の2を8月14日以後の20週間で販売しました。

    PS3も発言直後に回復しています。8月14日集計は9,586台でしたが、8月21日は30,342台、8月28日は32,235台、9月11日には62,266台へ上昇しました。8月14日以後の週平均は**35,568台**で、それ以前の約2.2万台を上回ります。

    ただし両機の差は大きく、改定直後4週間の週平均は3DSが**82,016台**、PS3が**26,283台**でした。PS3にも盃休み後の上向きは見られるものの、市場の主役となったのは1万円の値下げで勢いを得た3DSです。

    「一族で大テレビを囲んでPS3」という期待とは対照的に、同じ日に価格改定された携帯機がその後の販売を圧倒しました。盃休み発言は、PS3がまったく売れていなかったから面白いのではなく、**PS3も回復する中で、より大きな市場の波が3DSへ向かっていた**という文脈に置くと、いっそう味わい深くなります。
    """)
    return


@app.cell
def md_ps_generations_intro():
    mo.md(r"""
    ## 発売から同じ週数でPS3・PS4・PS5を比較する

    PS3の発売日は2006年11月11日です。盃休み発言があった2011年8月11日は、発売から**1,734日（247週と5日）後**、すなわち**発売248週目**に当たります。

    週販データでこの時点までに完了している最新の集計は2011年8月7日で、`index_week=248`です。そこでPS3・PS4・PS5をすべて**発売第248週まで**に揃え、週平均販売台数と累計販売台数を比較します。
    """)
    return


@app.cell
def calc_ps_generations_248():
    # 2011年8月11日はPS3の発売248週目なので、3世代とも第248週までに揃える
    ps_generation_target_week = 248
    _ps_generation_hws = ["PS3", "PS4", "PS5"]
    _ps_generation_source = g.load_hard_sales().filter(
        pl.col("hw").is_in(_ps_generation_hws),
        pl.col("index_week") <= ps_generation_target_week,
    )

    # 同一週数までの週平均・累計と、各機種で第248週に対応する日付を集計する
    _ps_generation_raw = (
        _ps_generation_source
        .group_by("hw")
        .agg(
            pl.col("launch_date").first().alias("発売日"),
            pl.col("report_date").max().alias("第248週集計日"),
            pl.len().alias("集計週数"),
            pl.col("units").mean().round(0).cast(pl.Int64).alias("週平均販売台数"),
            pl.col("sum_units").max().alias("第248週累計"),
        )
    )
    _ps3_total_at_248 = _ps_generation_raw.filter(pl.col("hw") == "PS3").select("第248週累計").item()

    # PS3との差を台数と比率で示し、世代間の規模を比較しやすくする
    ps_generation_248_summary = (
        _ps_generation_raw
        .with_columns(
            (pl.col("第248週累計") - _ps3_total_at_248).alias("PS3との差"),
            ((pl.col("第248週累計") / _ps3_total_at_248 - 1) * 100).round(1).alias("PS3比(%)"),
            pl.col("hw").replace(g.get_hard_dict()).alias("ハード"),
        )
        .select(
            "ハード",
            "発売日",
            "第248週集計日",
            "集計週数",
            "週平均販売台数",
            "第248週累計",
            "PS3との差",
            "PS3比(%)",
        )
        .sort("第248週累計", descending=True)
    )
    return ps_generation_248_summary, ps_generation_target_week


@app.cell
def table_ps_generations_248(ps_generation_248_summary):
    # 3機種を同じ248週間で揃え、販売ペースと累計を表で比較する
    ps_generation_248_summary
    return


@app.cell
def md_ps_generations_chart():
    mo.md(r"""
    ### 発売第248週までの累計販売台数推移

    暦年ではなく発売後の週数を横軸にすることで、発売時期が異なる3世代を同じ条件で比較します。
    """)
    return


@app.cell
def chart_ps_generations_cumulative_248(ps_generation_target_week):
    # gamedataの既存相対累計グラフを使い、発売第1週から第248週までを揃えて表示する
    g.chart_line_cumulative_delta(
        hw=["PS3", "PS4", "PS5"],
        mode="week",
        begin=1,
        end=ps_generation_target_week,
        index_mode=True,
        multi_line=True,
        size=(760, 440),
    )
    return


@app.cell
def md_ps_generations_evaluation():
    mo.md(r"""
    ### 評価

    発売第248週までの累計は、PS4が**7,187,861台**、PS5が**6,954,944台**、PS3が**6,601,535台**でした。週平均はそれぞれ約29,000台、28,000台、26,600台です。

    PS3はPS4より累計で**586,326台（約8.9%）**、PS5より**353,409台（約5.4%）**少なく、3世代の中では最下位です。この意味では、2011年8月時点のPS3が後継機ほどの販売ペースを築けておらず、ファンが苦境や物足りなさを感じる余地はありました。

    一方で、差は1割未満に収まっています。PS3は約4年9か月で国内660万台に達しており、後継世代から大きく脱落した失敗機というほど弱くありません。むしろPS4・PS5にかなり近い規模を、より低い週平均ながら積み上げていました。

    したがって、盃休み発言当時のPS3は、**後継機と比べればやや劣勢だが、PlayStation据置機として十分に標準的な普及規模にあった**と評価できます。「誰もが一族で遊ぶ普通の存在」という主張は飛躍ですが、PS3そのものが市場から見放されていたわけではありません。
    """)
    return


@app.cell
def _():
    # 週販グラフの8/11近辺の拡大
    g.chart_line_sales(
        hw=["PS3", "3DS", "Wii", "XB360", "PSP"],
        mode="week",
        begin=date(2011, 4, 1),
        end=date(2011, 9, 15),
        annotation_level=13,
        with_point=True,
        multi_line=True,
        size=(760, 440),
    )
  
  
    return


@app.cell
def md_ps3_lifetime_intro():
    mo.md(r"""
    ## PS3のライフタイムにおける2011年

    PS3の発売年から国内集計が終了するまでの年間販売台数を比較し、盃休み発言のあった2011年が製品ライフサイクルのどこに位置していたかを確認します。
    """)
    return


@app.cell
def chart_ps3_yearly_lifetime():
    # gamedataの既存年次棒グラフで、PS3の発売年から集計終了年までを表示する
    g.chart_bar_sales(
        hw=["PS3"],
        mode="year",
        stacked=False,
        size=(760, 420),
    )
    return


@app.cell
def calc_ps3_lifetime_yearly():
    # PS3の年次販売台数を集計し、2011年までの累計比率も確認する
    _ps3_lifetime_source = g.load_hard_sales().filter(pl.col("hw") == "PS3")
    ps3_yearly_lifetime_table = (
        g.yearly_sales(_ps3_lifetime_source)
        .select(
            pl.col("year").alias("年"),
            pl.col("yearly_units").alias("年間販売台数"),
        )
        .sort("年")
    )
    _ps3_final_total = g.extract_total(_ps3_lifetime_source, compact=True).select("sum_units").item()
    _ps3_through_2011 = ps3_yearly_lifetime_table.filter(pl.col("年") <= 2011).select(pl.col("年間販売台数").sum()).item()
    ps3_lifetime_position_2011 = pl.DataFrame({
        "2011年販売台数": [ps3_yearly_lifetime_table.filter(pl.col("年") == 2011).select("年間販売台数").item()],
        "2011年末までの累計": [_ps3_through_2011],
        "最終累計": [_ps3_final_total],
        "2011年末時点の到達率(%)": [round(_ps3_through_2011 / _ps3_final_total * 100, 1)],
    })
    return ps3_lifetime_position_2011, ps3_yearly_lifetime_table


@app.cell
def table_ps3_yearly_lifetime(ps3_yearly_lifetime_table):
    # グラフの値を年次表でも確認する
    ps3_yearly_lifetime_table
    return


@app.cell
def table_ps3_lifetime_position_2011(ps3_lifetime_position_2011):
    # 2011年末時点で最終累計の何割まで到達していたかを表示する
    ps3_lifetime_position_2011
    return


@app.cell
def md_ps3_lifetime_evaluation():
    mo.md(r"""
    ### 評価

    PS3の年間販売は2009年の**1,723,036台**を頂点に、2010年が約150万台、2011年が**1,414,745台**、2012年も約133万台でした。2011年はピークを越えてはいますが、急激な衰退局面ではなく、年間130万～150万台を維持した成熟期の中央にあります。

    2011年の販売台数はPS3の全年度中で4番目に多く、翌2012年も大きくは崩れていません。本格的な縮小が明瞭になるのは、PS4発売前年の2013年以降です。

    2011年末の累計は**7,312,895台**で、最終累計10,080,894台の**72.5%**に到達していました。すでに十分普及していましたが、その後も約277万台を積み上げています。

    したがって、2011年のPS3を「末期」と呼ぶのは早く、**ピーク後ではあるが販売規模を保っていた成熟期**と位置づけるのが適切です。盃休み発言は、消えゆくハードへの断末魔というより、携帯機が勢力を強める市場で、まだ現役だった据置機文化の優位を主張した発言と見るほうが実態に合います。
    """)
    return


@app.cell
def md_seventh_generation_yearly_intro():
    mo.md(r"""
    ## 据置機市場におけるPS3・Wii・Xbox 360

    携帯機を除き、同世代の据置機であるPS3・Wii・Xbox 360の年間販売台数を比較します。期間はXbox 360発売年の2005年から、3機種が終盤を迎える2014年までです。
    """)
    return


@app.cell
def chart_seventh_generation_yearly():
    # gamedataの既存年次棒グラフを使い、同世代据置機を横並びで比較する
    g.chart_bar_sales(
        hw=["PS3", "Wii", "XB360", "WiiU"],
        begin=date(2005, 1, 1),
        end=date(2014, 12, 31),
        mode="year",
        stacked=False,
        size=(780, 440),
    )
    return


if __name__ == "__main__":
    app.run()
