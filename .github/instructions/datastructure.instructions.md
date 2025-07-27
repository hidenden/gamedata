---
applyTo: '**/*.py'
applyTo: '**/*.md'
applyTo: '**/*.ipynb'
description: 'プロジェクトで使用するデータ構造の情報を提供します。'
version: 1.0.0
---
このプロジェクトでは、load_hard_sales()を使用して、ビュー `hard_sales` からデータを取得することができます。
このビューは、ゲームハードの週次販売データ、分析指標、およびハード情報を統合して参照できるように設計されています。
ビューのデータは load_hard_sale()内で処理され、Pandas DataFrameとして返されます。
以下に、load_hard_sales()の返すデータ型の詳細を示します。

| カラム名      | 型      | 説明                                                         |
|:------------- |:------- |:------------------------------------------------------------ |
| weekly_id     | string    | 週次データのID（gamehard_weekly.id）                         |
| begin_date    | datetime64   | 集計開始日（週の初日）                                       |
| end_date      | datetime64   | 集計終了日（週の末日、=report_date）                         |
| report_date   | datetime64   | 集計期間の末日                                               |
| period_date   | int64 | 集計日数(通常は7, 稀に14)                                          |
| hw            | string    | ゲームハードの識別子                                         |
| units         | int64 | 週次販売台数                                                 |
| year          | int64 | report_dateの年                                              |
| month         | int64 | report_dateの月                                              |
| mday          | int64 | report_dateの日                                              |
| week          | int64 | report_dateの週番号（ISO週番号）                             |
| delta_day     | int64 | 発売日から何日後か                                           |
| delta_week    | int64 | 発売日から何週間後か                                         |
| delta_year    | int64 | 発売年から何年後か(同じ年なら0)                                |
| avg_units     | int64 | 1日あたりの販売台数 (units / period_date)                     |
| sum_units     | int64 | report_date時点での累計販売台数                              |
| launch_date   | datetime64 | 発売日                                                |
| maker_name    | string  | メーカー名                                                |
| full_name     | string  | ゲームハードの正式名称                                      |　　


