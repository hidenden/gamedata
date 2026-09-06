# AI向けカタログ

`gamedata.catalog` は、ライブラリの使い方・データの意味・手元のDataFrameの状態を調べる読み取り専用APIです。
marimoに依存せず、通常のPythonからも利用できます。カタログ関数自体はDBに接続せず、キャッシュも更新しません。

```python
import gamedata as g
from gamedata import catalog

print(catalog.render(catalog.overview()))
print(catalog.render(catalog.search("発売からの累計を比較")))
print(catalog.render(catalog.describe("function:cumulative_sales_by_delta_long")))
```

## marimo-pairでの接続案内

接続プロンプトやnotebook冒頭の説明に次の文章を追加してください。
既存notebookのファイル変更は必要ありません。

> 分析前に `from gamedata import catalog` を実行し、`catalog.overview()` を参照してください。
> 販売データは `hard_sales_all_df`、注釈データは `annotation_all_df` にあります。
> `catalog.inspect_frame(hard_sales_all_df, dataset="hard_sales")` で実際の収録範囲を確認し、
> `catalog.search()` と `catalog.describe()` で分析に使う既存関数と列の意味を確認してください。

marimo-pairのscratchpadで呼び出す場合は `print(catalog.render(...))` で結果を出力します。
scratchpadのimportは一時的なので、後の呼び出しでも必要ならimportしてください。
実行中の環境が更新前のライブラリを保持している場合は、環境への更新反映が必要です。
このカタログにはmarimoの非公開APIへの依存はありません。

## API

| 関数 | 内容 |
| --- | --- |
| `overview()` | ライブラリ概要、登録範囲、必読ルール、次の呼び出し例 |
| `search(query, kind=None, limit=10)` | ID・説明の検索。kindはdataset/column/function/recipe。空文字で一覧 |
| `describe(id, sections=None, params=None)` | 詳細定義。sectionsで返す項目を選択。paramsは関数の出力分岐に使用 |
| `inspect_frame(df, dataset=None, profile="basic", sample_rows=0)` | 渡されたPolars DataFrameを検査 |
| `render(result, format="markdown")` | MarkdownまたはJSON文字列に変換 |

`render()` 以外の結果はJSON化できる辞書です。`schema_version=1` はカタログ応答形式の版で、
`overview()` の `library_version` とは別です。返却した辞書を変更しても登録定義には影響しません。

```python
catalog.describe("column:hard_sales.sum_units")
catalog.describe("column:monthly_sales.sum_units")
catalog.describe("dataset:hard_sales", sections=["columns", "semantics"])
catalog.describe("function:weekly_sales", params={"maker_mode": True})
catalog.describe("function:cumulative_sales_by_delta_long", params={"mode": "month"})
```

列IDはデータセットに属します。同じ `sum_units` でも、販売の元データではDB履歴の累計、
`weekly_sales`・`monthly_sales` の出力では抽出期間内の累計です。
関数のシグネチャと引数のデフォルト値は実関数から取得します。
`params` は対象関数を実行しません。`maker_mode` と経過期間の `mode` の出力契約を解決します。
未指定時は実関数のデフォルトの出力と、利用できる分岐を返します。

## 実データの観測

```python
result = catalog.inspect_frame(
    hard_sales_all_df, dataset="hard_sales", profile="full", sample_rows=3
)
print(catalog.render(result, format="json"))
```

- `definition`: 指定したデータセットの定義。
- `observed`: 実際の行数・型・日付範囲・機種など。
- `validation`: 定義との列・型の違い。fullではキーの重複数・欠損行数も含む。
- `unknown`: 来歴・DB更新時刻など、このDataFrameからは確認できない事項。

`basic` は日付列・機種等を走査します。`full` はさらに全列の欠損数、機種別収録範囲を調べます。
`hard_sales` の日付間隔が7日を超える箇所は欠落候補として返しますが、期間抽出や14日集計でも
生じるため欠測と断定しません。キー検査の `duplicate_rows` は一意なキー数を超えた行数です。
`validation.status` はスキーマの一致状況で、キー検査の合否や意味の正しさを保証するものではありません。

`dataset` を省略すると列構成に基づく候補を最大5件返し、定義は確定しません。
指定した場合も、来歴を確認したことにはなりません。型が一致する加工済みデータも存在するためです。
機種・機種別収録範囲・欠落候補は最大20件、サンプルは明示指定した場合のみ最大20行です。
日付はISO形式、NaN/無限大はnull、Decimalは文字列、バイナリはhex、未対応オブジェクトは型名で返します。
`LazyFrame` は暗黙に実行せずTypeErrorになります。

不明なIDはKeyError、不正なオプションはValueError、未対応の入力型はTypeErrorになります。
検索結果が0件でも、その機能がライブラリに存在しないとは限りません。

## 初期版の登録範囲と拡張

販売・ハード情報・注釈の3種と、週次/月次・メーカー別・経過期間別の派生出力を登録しています。
関数はロード3種、date_filter、sales_long、weekly_sales、monthly_sales、monthly_sales_long、
cumulative_sales_by_delta_longの9種です。グラフ・ピボット・レポート関数は未登録です。

定義は `src/gamedata/catalog/datasets.py`、関数契約は `functions.py`、分析例は `recipes.py` にあります。
出力の粒度や累計の起点が異なる場合は別データセットを登録してください。
実関数の代表的な引数で出力スキーマを検証し、定義とのずれをテストで検出します。
説明文は明示的に保守し、docstringや列名だけから意味を自動推測しません。
