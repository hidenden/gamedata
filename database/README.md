# データベース設計概要

このリポジトリのデータベースは、ゲームハードの情報・週次販売データ・関連イベント情報を管理するためのSQLite3用スキーマです。  
本READMEでは、`create_tables.sql` で定義されているテーブル構造とその設計意図について説明します。

---

## テーブル一覧

### 1. `gamehard_info`

ゲームハード（コンソール）の基本情報を管理します。

| カラム名      | 型    | 制約・説明                                                                 |
|:------------- |:----- |:-------------------------------------------------------------------------- |
| id            | TEXT  | PRIMARY KEY。ゲームハードの識別子（例: "NSW", "PS5" など）                |
| launch_date   | TEXT  | NOT NULL。発売日（YYYY-MM-DD形式）。形式チェックあり                       |
| maker_name    | TEXT  | NOT NULL。メーカー名（例: "Nintendo", "Sony" など）                        |
| full_name     | TEXT  | NOT NULL。正式名称（例: "Nintendo Switch", "PlayStation 5" など）          |

- `id` は他テーブルの外部キーとして参照されます。
- `launch_date` には `GLOB '????-??-??'` による形式チェックが入っています（数字であることや実在日付までは保証しません）。

---

### 2. `gamehard_weekly`

ゲームハードごとの週次販売データを管理します。

| カラム名      | 型    | 制約・説明                                                                 |
|:------------- |:----- |:-------------------------------------------------------------------------- |
| id            | TEXT  | PRIMARY KEY。`report_date` と `hw` を連結した文字列（例: "2023-10-01_NSW"）|
| report_date   | TEXT  | NOT NULL。集計期間の末日（YYYY-MM-DD形式）。形式チェックあり                |
| period_date   | INTEGER| NOT NULL。集計日数（通常7、時々14など）                                   |
| hw            | TEXT  | NOT NULL。ゲームハードの識別子。`gamehard_info(id)` への外部キー           |
| units         | INTEGER| NOT NULL。売上台数（0以上）。                                             |

- `hw` は `gamehard_info(id)` を参照する外部キーです（ON DELETE CASCADE）。
- `report_date` には `GLOB '????-??-??'` による形式チェックがあります。
- `units` は0以上の整数のみ許可されます。

---

### 3. `gamehard_events`

ゲームハードに関連するイベント情報を管理します。

| カラム名      | 型    | 制約・説明                                                                 |
|:------------- |:----- |:-------------------------------------------------------------------------- |
| id            | TEXT  | PRIMARY KEY。`event_date` と `hw` を連結した文字列（例: "2025-06-05_NS2"） |
| event_date    | TEXT  | NOT NULL。イベント日（YYYY-MM-DD形式）。形式チェックあり                   |
| hw            | TEXT  | NOT NULL。ゲームハードの識別子。`gamehard_info(id)` への外部キー           |
| event_name    | TEXT  | NOT NULL。イベント名（例: "PS5値下げセール開始" など）                     |

- `hw` は `gamehard_info(id)` を参照する外部キーです（ON DELETE CASCADE）。
- `event_date` には `GLOB '????-??-??'` による形式チェックがあります。

---

### 4. `gamehard_weekly_analysis`

週次販売データとゲームハード情報をもとに、分析用の指標をまとめたテーブルです。

| カラム名      | 型      | 制約・説明                                                                                  |
|:------------- |:------- |:------------------------------------------------------------------------------------------ |
| id            | TEXT    | PRIMARY KEY。`gamehard_weekly(id)` と同じ値。外部キーでもある                              |
| year          | INTEGER | `report_date` の年                                                                         |
| month         | INTEGER | `report_date` の月                                                                         |
| mday          | INTEGER | `report_date` の日                                                                         |
| week          | INTEGER | `report_date` の週番号（ISO週番号）                                                        |
| delta_day     | INTEGER | 発売日から何日後か（発売日と同じなら0）                                                    |
| delta_week    | INTEGER | 発売日から何週間後か（発売週と同じなら0）                                                  |
| delta_year    | INTEGER | 発売年から何年後か（発売年と同じなら0、翌年なら1、整数）                                   |
| avg_units     | INTEGER | 1日あたりの販売台数。`units` の値を `period_date`の値で割ったもの。整数、小数点以下切り捨て   |
| sum_units     | INTEGER | `report_date` 時点でのそのゲーム機の累計台数（その週の `units` も加算済み）                |

- `id` は `gamehard_weekly(id)` を参照する外部キーです（ON DELETE CASCADE）。
- このテーブルは、`gamehard_weekly` と `gamehard_info` のデータをもとに、分析や可視化に便利な形で指標をまとめています。
- `sum_units` は各ハードごとに `report_date` 昇順で累積計算されます。

---

## インデックス

- `gamehard_weekly(report_date)` に `idx_gamehard_weekly_report_date`
- `gamehard_weekly(hw)` に `idx_gamehard_weekly_hw`

これにより、週次データの検索効率が向上します。

---

## 注意事項

- 日付カラム（`launch_date`, `report_date`, `event_date`）は `YYYY-MM-DD` 形式の文字列で保存されますが、実在する日付かどうかまではDB制約で保証されません。
- 外部キー制約（ON DELETE CASCADE）により、親テーブル（`gamehard_info`）の行が削除されると、関連する子テーブル（`gamehard_weekly`, `gamehard_events`）の行も自動的に削除されます。
- テーブル作成前に既存テーブルをDROPするため、再実行時も安全です。

---

## テーブル間のリレーション

```mermaid
erDiagram
    gamehard_info ||--o{ gamehard_weekly : "id = hw"
    gamehard_info ||--o{ gamehard_events : "id = hw"
    gamehard_weekly ||--|| gamehard_weekly_analysis : "id = id"

    gamehard_info {
        TEXT id PK
        TEXT launch_date
        TEXT maker_name
        TEXT full_name
    }
    gamehard_weekly {
        TEXT id PK
        TEXT report_date
        INTEGER period_date
        TEXT hw FK
        INTEGER units
    }
    gamehard_events {
        TEXT id PK
        TEXT event_date
        TEXT hw FK
        TEXT event_name
    }
    gamehard_weekly_analysis {
        TEXT id PK, FK
        INTEGER year
        INTEGER month
        INTEGER mday
        INTEGER week
        INTEGER delta_day
        INTEGER delta_week
        INTEGER delta_year
        INTEGER avg_units
        INTEGER sum_units
    }
```

---

## 実行方法

SQLite3コマンドラインで以下のように実行できます。

```sh
sqlite3 your_database.db < [create_tables.sql](http://_vscodecontentref_/0)


