# データソースについて

初期データの入手と変換を行うコンポーネント｡
現在は既に入手､変換した初期データに対して､
毎週の更新を行っているため､
このデータソースのプログラムやデータは使われていない｡

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

