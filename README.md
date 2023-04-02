# Japan Game Data Analysis

## 使い方

1. ./update.sh を実行し定点観測サイトから最新のデータをロードします
2. pyspark を実行し PySparkを起動します
3. ブラウザ上のPySpark画面上で database/parquet/build.ipynb を実行します

## Pの考え方

- データソース毎にプロジェクトを作成する
  - DataSource-XXXX
  - raw/ 生データの格納場所(手差しの場合､オンライン接続するならこれは無い)
  - clean/ データの型変換､欠損部､不要部の除去
  - processed/ データ構造の変形､テーブルのjoin(データソース内), 分割
  - shared/ 整ったデータ(大抵は processedの最終段のコピーそのまま)
- Objectプロジェクト
  - processed/ (必要があれば)複数のデータソースのsharedのデータを組み合わせ､変形
  - shared/ 整ったデータ (データソースのsharedからちょくで来る場合もある)
- Ontology
  - グローバルで共通｡プロジェクトには属さない｡
  - Objectプロジェクトの sharedの写像
  - WriteBackでもOntologyのバックに必ずデータフレームが必要


## ゲームデータ分析の現実

- データソースは3箇所
  - 定点観測 2016〜現在｡ 日付のIndexと機種名のヘッダを持つCSV
     - raw/teitenkansoku/build.py
  - geimin_net 過去の記録｡ セル内の加工が結構必要
     - build.py
  - gamesdata 2015/12末のみのデータ｡手差し｡ 整形済み
     - gamesdata_2015_12.csv
- データ変換 tansform/
  - build.py  他の変換処理の呼び出し､ gamesdataのコピー
  - geimin_filter.py  scheme変換しgeimin_weekly_hard_1999_2015.csvを生成
  - teiten_filter.py  scheme変換しteiten_weekly_hard_2016_2022.csvを生成
  - nayose.py  上記3つを連結しHW名を統一する nayose_weekly_hard_1999_2022.csv
  - saven_days.py 7日単位に正規化する weekly_hard_1999_2022.csv
- 分析用データ準備 processed/
  - build.py transformのweekly_hard_1999_2022.csvのコピー､変形
  - hw_sum.py 絶対日付累計データ､ 相対日付累計データの生成
- analyzed/ 分析の実施場所 
  - jupyterのnotobookで構成される分析過程､結果が格納される

### 気になる点

- transform/ がデータソースの種類関係なく煩雑
- processed/ が煩雑である｡神様データがどれかよくわからん
- analyzed/ 分析過程のデータをここに置くのか? 
- Pの考え方とちょっと違う


## ゲームデータ分析の構造検討

- data_source/
  - teitenkansoku/
    - raw/build.py
    - processed/teiten_filter.py
    - 最終データは直下に配置 teiten_hard_weekly_2016_2022.csv
  - geimin_net/
    - raw/build.py
    - processed/geimin_filter.py
    - 最終データは直下に配置 geimin_hard_weekly_1999_2015.csv
  - gamesdata/
    - 手差しデータを直下に配置 gamesdata_hard_weekly_2015_15.csv
- database/
  - processed/nayose.py, saven_days.py
  - hard_weekly.csv  マスターデータを直下に
  - pkl/   pandas pkl形式の派生データと生成スクリプト群
  - parquet/ pyspark parquet形式の派生データと生成スクリプト群
- analysis/ 分析の実施場所    
  - jupyterのnotobookで構成される分析過程､結果が格納される

## 処理の定型化

Makefile(make)によるデータの半自動更新｡

