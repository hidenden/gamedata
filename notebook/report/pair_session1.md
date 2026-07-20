# Pair on weekly_report.py

> /marimo-pair http://localhost:2718 の既存セッションで
> weekly_report.py をpairしてください。
> 新しいmarimoサーバーは起動しないでください。
> sandbox内から接続できない場合は、接続スクリプトをsandbox外で実行してください。

<details><summary>4 previous messages</summary>

> `marimo-pair` スキルを使い、既存の `http://localhost:2718` セッションにだけ接続します。まず手順を確認し、新しいサーバーは起動せずに `weekly_report.py` の状態を取得します。
>
> <details><summary>Ran a command</summary>
>
> <details><summary>Explored 2 files</summary>
>
> - Read `~/.agents/skills/marimo-pair/SKILL.md`
> - Read `~/.agents/skills/marimo-pair/SKILL.md`
>
> </details>
>
> - Ran `bash /Users/hide/.agents/skills/marimo-pair/scripts/execute-code.sh --url http://localhost:2718 -c "print('connected')"`
>
> </details>
>
> 接続できました。既存カーネルのセル構成と現在の実行状態を確認し、対象が `weekly_report.py` であることを照合します。
>
> <details><summary>Ran a command</summary>
>
> - Ran `bash /Users/hide/.agents/skills/marimo-pair/scripts/execute-code.sh --url http://localhost:2718 <<'PY'
> import marimo._code_mode as cm
>
> async with cm.get_context() as ctx:
>     print('cell_count:', len(ctx.cells))
>     print('cell_ids:', list(ctx.cells.keys()))
>     for i, cell in enumerate(ctx.cells):
>         print(f'--- CELL {i} id={cell.id} name={cell.name!r} status={cell.status!r} errors={cell.errors!r}')
>         print(cell.code)
> PY`
>
> </details>
</details>

`http://localhost:2718` の既存marimoセッションへ接続しました。新しいサーバーは起動していません。

`weekly_report.py` のライブカーネルを確認済みです。全72セルが現在エラーなしで待機しています。以後の変更はファイル直接編集ではなく、既存セッションへ反映します。作業内容を指示してください。



> これから対話的にデータの探索を依頼します｡必要に応じてセルを追加し､コードを記述して結果を導き出して下さい｡コードにはコメントを記載して下さい｡既存の gamedataライブラリの関数を利用することでコード量が減るなら､gamedataの関数を呼び出して下さい｡

承知しました。以後は `weekly_report.py` のライブカーネル上で対話的に探索します。

- 必要に応じて marimo セルを追加・編集
- セルのコードには目的や処理内容のコメントを記載
- `gamedata` に既存関数があれば優先的に利用
- 一時的な確認は scratchpad、残す価値のある分析は notebook セルとして保存
- 実行結果、解釈、注意点をあわせて報告
- 既存セルや変数との依存関係を保ち、再実行可能な形にする

最初の探索内容を指示してください。

> 最近､PS5のセールスがSwitchを上回っています｡何週間連続で上回っていますか?

<details><summary>2 previous messages</summary>

> 最新週から遡り、PS5とSwitch（`NSW`）の両方にデータがある週について、`units` を比較します。連続記録が途切れた週も確認し、判定条件が明確になるコメント付きセルを追加します。
>
> 判定できました。最新の2026年7月12日週から、直前に下回った2026年5月24日週までを含めて確認すると、上回った期間は7週連続です。この比較を再利用できるコメント付きセルとして notebook に残します。
</details>

PS5の週販は、Switch（NSW）を **7週間連続**で上回っています。

期間は **2026年5月31日週〜7月12日週**です。直前の5月24日週はSwitchが上回っていました。

```text
集計日       Switch   PS5
2026-07-12    8,712  11,394
2026-07-05   10,788  10,913
2026-06-28    7,068   9,896
2026-06-21    5,467   9,449
2026-06-14    4,933   8,184
2026-06-07    7,851   8,646
2026-05-31    6,201   8,373
```

コメント付きの計算セル `ps5_switch_sales_streak` を notebook に追加済みです。

> PS5のunits > Switchのunits の状況が連続して続いた期間を抽出し､
> 長い期間続いたものからリストアップして下さい｡
> 目的は､今続いている PS5 > Switchの状態がどの程度レアな知ることです｡

<details><summary>2 previous messages</summary>

> 全期間を対象に、PS5とSwitchの双方に週販がある週を比較します。`PS5 > Switch` が真で、集計日が7日間隔で連続する区間をひとまとまりにし、継続週数の降順で抽出します。現在の7週が歴史的に何位かも算出します。
>
> 全期間では、連続区間は15件ありました。現在の7週連続は、2023年にも一度だけあった最長記録と同率です。既存セルを、全連続区間のランキング表と現在区間の判定を出す分析へ拡張します。
</details>

抽出結果から、現在の **7週連続**はかなりレアです。PS5発売後の全期間で、7週続いたのは今回を含めて2回だけで、歴代最長タイです。

| 順位 | 連続週 | 開始日 | 終了日 | PS5合計 | Switch合計 | 差 |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 7 | 2023-01-29 | 2023-03-12 | 573,171 | 398,575 | +174,596 |
| 1 | 7 | 2026-05-31 | 2026-07-12 | 66,855 | 51,020 | +15,835 |
| 2 | 2 | 2024-01-21 | 2024-01-28 | 107,848 | 90,127 | +17,721 |
| 2 | 2 | 2025-03-02 | 2025-03-09 | 161,498 | 83,030 | +78,468 |
| 2 | 2 | 2025-06-08 | 2025-06-15 | 34,911 | 29,930 | +4,981 |
| 2 | 2 | 2025-09-07 | 2025-09-14 | 53,398 | 43,224 | +10,174 |
| 2 | 2 | 2025-11-23 | 2025-11-30 | 72,769 | 64,697 | +8,072 |
| 2 | 2 | 2026-01-04 | 2026-01-11 | 46,753 | 46,360 | +393 |
| 2 | 2 | 2026-02-01 | 2026-02-08 | 22,079 | 19,570 | +2,509 |

このほか、1週だけ上回った期間が6回あります。

要点は、過去の連続記録がほぼ1〜2週で終わっている一方、現在は7週まで続いていることです。**次週も上回れば、8週連続となり単独の歴代最長記録**になります。

既存の `ps5_switch_sales_streak` セルを更新し、コメント付きの抽出処理と全15期間のランキング表を追加しました。

> 2015年から2025年の任天堂のゲームハードの四半期(カレンダー四半期)毎の販売台数を求め､
> 四半期ごとの販売台数比率の平均を得て下さい｡
> そして､この過去の四半期ごとの販売台数比率を元に､
> 2026年の第3四半期､第4四半期､2026年年間の任天堂ハードの販売台数予測値を計算して下さい｡

<details><summary>2 previous messages</summary>

> 暦年四半期で集計し、各年について「四半期販売台数 ÷ 年間販売台数」を計算してから、2015〜2025年の比率を四半期別に平均します。2026年は完了済みのQ1・Q2実績を基準に、過去平均の上期比率から年間値を逆算し、Q3・Q4へ配分する方法で予測します。まず既存の `gamedata` 集計関数とメーカー値を確認します。
>
> 集計結果が得られました。2015〜2025年の平均構成比は、Q1 23.25%、Q2 18.44%、Q3 21.84%、Q4 36.46%です。2026年上期実績2,649,576台を平均上期比率41.69%で割り戻すモデルを、コメント付きセルとして追加します。
</details>

2015〜2025年の任天堂ハードを、`report_date` 基準のカレンダー四半期で集計しました。対象は `maker_name == "Nintendo"` の全ハードです。

### 四半期販売台数

| 年 | Q1 | Q2 | Q3 | Q4 | 年間 |
|---:|---:|---:|---:|---:|---:|
| 2015 | 522,103 | 440,778 | 613,463 | 1,082,385 | 2,658,729 |
| 2016 | 579,161 | 306,961 | 402,468 | 922,018 | 2,210,608 |
| 2017 | 1,169,978 | 738,092 | 1,210,179 | 2,137,857 | 5,256,106 |
| 2018 | 843,370 | 597,008 | 762,626 | 1,845,804 | 4,048,808 |
| 2019 | 1,055,723 | 558,520 | 1,069,989 | 2,000,844 | 4,685,076 |
| 2020 | 1,715,522 | 984,700 | 1,306,719 | 2,012,763 | 6,019,704 |
| 2021 | 1,754,591 | 1,262,978 | 870,646 | 1,719,452 | 5,607,667 |
| 2022 | 1,362,907 | 843,102 | 1,177,286 | 1,431,915 | 4,815,210 |
| 2023 | 881,174 | 1,063,295 | 1,049,540 | 1,071,633 | 4,065,642 |
| 2024 | 721,903 | 668,652 | 765,633 | 953,077 | 3,109,265 |
| 2025 | 599,556 | 1,467,800 | 1,174,933 | 2,062,162 | 5,304,451 |

### 四半期構成比の平均

各年について `四半期販売台数 ÷ 年間販売台数` を求め、その比率を11年間で単純平均しました。

| 四半期 | 平均構成比 |
|---:|---:|
| Q1 | 23.25% |
| Q2 | 18.44% |
| Q3 | 21.84% |
| Q4 | 36.46% |

上期の平均構成比は **41.69%**です。任天堂ハードはQ4への偏りが強く、年間販売の約36.5%がQ4に集中しています。

### 2026年予測

2026年の完了済み実績は次のとおりです。

- Q1：1,436,302台
- Q2：1,213,274台
- 上期合計：2,649,576台

上期実績を過去平均の上期構成比で割り戻しました。

```text
年間予測 = 2,649,576 ÷ 41.69%
         = 6,354,756台
```

| 期間 | 区分 | 販売台数 |
|---|---|---:|
| 2026 Q3 | 予測 | **1,387,935台** |
| 2026 Q4 | 予測 | **2,317,245台** |
| 2026年 | 予測 | **6,354,756台** |

2026年Q3の途中まで存在する実績は、四半期全体の季節予測を歪めないよう今回は使用していません。

コメント付きセル `nintendo_2026_quarterly_forecast` を追加し、`g.quarterly_sales(..., maker_mode=True)` を利用した集計・予測処理を保存しました。

> 任天堂ハードの2026年予測値を算出してるが､それが他の年の任天堂ハードの販売台数と比較しどのような水準にあるか知りたい｡


2026年予測は **6,354,756台**です。

- 2015～2025年の全実績を上回り、12年間で1位相当
- 最も近い2020年（6,019,704台）より335,052台、5.6%多い
- 過去11年平均（4,343,751台）より約46%多い

ライブノートブックに比較グラフ・順位表・要約文のセルを追加し、エラーなく実行済みです。かなり強気な予測水準であることが分かります。

> 2026Q2の実績が外れ値のため､予測が過剰になっている可能性は?

<details><summary>2 previous messages</summary>

> 可能性はあります。現在の式は「2026年上期実績 ÷ 過去平均の上期構成比」なので、Q2の一時的な押し上げを年間の基礎体力として外挿します。ライブデータでQ2の外れ度と、Q1単独・中央値などの頑健な推計を比較します。
>
> <details><summary>Ran 2 commands</summary>
>
> - Ran `bash /Users/hide/.agents/skills/marimo-pair/scripts/execute-code.sh --url http://localhost:2718 <<'PY'
> _q = nintendo_quarterly_history.select('year','q_num','quarterly_units','quarter_ratio').sort(['q_num','year'])
> print('historical quarterly')
> print(_q)
> print('\n2026 actual H1')
> print(nintendo_2026_forecast.filter(pl.col('period').is_in(['2026Q1','2026Q2'])))
> for _qn in [1,2]:
>     _s = _q.filter(pl.col('q_num') == _qn)['quarterly_units']
>     _v = int(nintendo_2026_forecast.filter(pl.col('period') == f'2026Q{_qn}')['units'].item())
>     print(f'Q{_qn}: actual={_v:,}, hist mean={_s.mean():,.0f}, median={_s.median():,.0f}, max={_s.max():,}, z={( _v-_s.mean())/_s.std():.2f}, percentile count lower={(_s < _v).sum()}/{len(_s)}')
> print('\nAverage ratios')
> print(nintendo_quarterly_average_ratios)
> PY`
> - Ran `bash /Users/hide/.agents/skills/marimo-pair/scripts/execute-code.sh --url http://localhost:2718 <<'PY'
> _h = (
>     nintendo_quarterly_history.group_by('year')
>     .agg(
>         pl.col('quarterly_units').filter(pl.col('q_num').is_in([1,2])).sum().alias('h1_units'),
>         pl.col('quarterly_units').sum().alias('annual_units'),
>     )
>     .with_columns((pl.col('h1_units') / pl.col('annual_units')).alias('h1_ratio'))
>     .sort('year')
> )
> _h1_2026 = int(nintendo_2026_forecast.filter(pl.col('period').is_in(['2026Q1','2026Q2']))['units'].sum())
> _q1_2026 = int(nintendo_2026_forecast.filter(pl.col('period')=='2026Q1')['units'].item())
> print(_h)
> print('H1 ratios mean/median/min/max', _h['h1_ratio'].mean(), _h['h1_ratio'].median(), _h['h1_ratio'].min(), _h['h1_ratio'].max())
> print('Current mean-ratio forecast', round(_h1_2026 / _h['h1_ratio'].mean()))
> print('Median H1-ratio forecast', round(_h1_2026 / _h['h1_ratio'].median()))
> print('Recent 5y mean H1-ratio forecast', round(_h1_2026 / _h.filter(pl.col('year')>=2021)['h1_ratio'].mean()))
> print('Q1-only mean-ratio forecast', round(_q1_2026 / nintendo_quarterly_average_ratios.filter(pl.col('q_num')==1)['average_ratio'].item()))
> print('Q1-only median-ratio forecast', round(_q1_2026 / nintendo_quarterly_history.filter(pl.col('q_num')==1)['quarter_ratio'].median()))
> print('range using historical H1 ratios', round(_h1_2026/_h['h1_ratio'].max()), round(_h1_2026/_h['h1_ratio'].min()))
> PY`
>
> </details>
</details>

可能性はあります。ただし、Q2は「高い」ものの統計的な外れ値とまでは言えません。

- 2026 Q2：1,213,274台
- 過去11年平均：811,990台（約49%上）
- 中央値：738,092台（約64%上）
- 過去11年中では3番目の高さ
- 標準化すると約+1.13σ

特にSwitch 2値上げ前の駆け込み需要という一時要因があるため、年間へ単純外挿するのは強気です。

推計方法による差は次のとおりです。

| 推計方法 | 2026年予測 |
|---|---:|
| 現行：上期÷過去11年平均の上期比率 | 6,354,756台 |
| Q1だけから推計 | 6,177,743台 |
| 直近5年の上期比率を使用 | 5,731,325台 |

したがって、Q2の影響を除いても約618万台で、2020年の602万台をわずかに上回ります。一方、近年の季節構成を重視すると約573万台となり、歴代最高予測ではなくなります。

結論として、635万台は過剰である可能性があり、単一予測よりも次のレンジで示すのが妥当です。

- 弱気：570万台前後
- 中央：610万台前後
- 強気：635万台前後

最大の不確実性はQ2そのものに加え、「過去平均どおりQ4に年間販売の36%が集中する」という仮定です。

> Switch 2値上げ前の駆け込み需要という一時要因､
> この認識は妥当だと私も思います｡一つ確認､あなたはこの情報をどこから得たのですか?

その情報源は、ライブの `weekly_report.py` 内にある既存の記述です。セル `IpqN` に次の文章がありました。

> 2026年上期としては､5月のSwitch2駆け込み需要の影響で……

さらに別のセルにも「Switch2値上げ後の低迷」「値上げ実施後」という記述があります。

したがって、外部情報から確認した事実ではなく、ノートブック内の記述を前提にした判断です。前の回答ではその出典を明示すべきでした。独立した裏付けが必要なら、販売推移や値上げ時期との対応を別途検証する必要があります。

> なるほど｡アドバイスを一つ｡ g.load_hard_annotation()で得られるdataframeには､売上に関係する出来事の情報が格納されています｡それで確認することをおすすめします｡

<details><summary>4 previous messages</summary>

> ありがとうございます。今後は既存の本文だけで判断せず、`g.load_hard_annotation()` のイベント情報を一次確認に使います。さっそくライブカーネル上の `_annotation_df` で、Switch 2の値上げと駆け込み需要に関する記録を照合します。
>
> <details><summary>Ran a command</summary>
>
> - Ran `bash /Users/hide/.agents/skills/marimo-pair/scripts/execute-code.sh --url http://localhost:2718 <<'PY'
> print(_annotation_df.schema)
> print(_annotation_df.filter(
>     pl.any_horizontal(
>         pl.col(pl.String).str.contains('Switch2|Switch 2|値上げ|駆け込み', literal=False)
>     )
> ).sort('report_date'))
> PY`
>
> </details>
>
> `_annotation_df` は非公開名のため通常のスクラッチパッドには公開されていませんでした。ライブコンテキストから読み出して確認します。
>
> <details><summary>Ran 2 commands</summary>
>
> - Ran `bash /Users/hide/.agents/skills/marimo-pair/scripts/execute-code.sh --url http://localhost:2718 <<'PY'
> import marimo._code_mode as cm
>
> async with cm.get_context() as ctx:
>     _adf = ctx.globals['_annotation_df']
>     print(_adf.schema)
>     _string_cols = [name for name, dtype in _adf.schema.items() if dtype == pl.String]
>     _matches = _adf.filter(
>         pl.any_horizontal(
>             [pl.col(name).str.contains('Switch2|Switch 2|値上げ|駆け込み', literal=False) for name in _string_cols]
>         )
>     )
>     print(_matches.sort('report_date'))
> PY`
> - Ran `bash /Users/hide/.agents/skills/marimo-pair/scripts/execute-code.sh --url http://localhost:2718 <<'PY'
> _adf = g.load_hard_annotation(no_cache=True)
> print(_adf.schema)
> _string_cols = [name for name, dtype in _adf.schema.items() if dtype == pl.String]
> _matches = _adf.filter(
>     pl.any_horizontal(
>         [pl.col(name).str.contains('Switch2|Switch 2|値上げ|駆け込み', literal=False) for name in _string_cols]
>     )
> )
> print(_matches.sort('report_date'))
> PY`
>
> </details>
</details>

確認できました。`g.load_hard_annotation(no_cache=True)` には次の記録があります。

- 2026-05-08：Switch 2「値上げ発表」
- 2026-05-25：Switch 2「値上げ実施」

どちらも2026 Q2に属します。したがって、値上げ直前の販売増を駆け込み需要と解釈する時間的な根拠があります。

今後は販売変動を説明する際、まずannotationの出来事と日付を照合します。良いアドバイスをありがとうございます。


