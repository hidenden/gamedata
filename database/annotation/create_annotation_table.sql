/*
 * これはSQLite3用のSQLスクリプトです。
 * gamehard_annotation tableを作成します。
 * このスクリプトは、SQLite3のコマンドラインツールで実行できます。
 */

/* 既存テーブルの削除
 * もしテーブルが存在する場合は削除します。(INDEXも含む)
 */
DROP TABLE IF EXISTS gamehard_annotation;

 /* テーブルの作成
 */

create table if not exists gamehard_annotation (
    id INTEGER PRIMARY KEY,
     -- 注釈の一意の識別子

    date TEXT NOT NULL CHECK(event_date GLOB '????-??-??'), 
    -- 注釈の日付。形式はYYYY-MM-DDである。

    hw TEXT NOT NULL,
    -- hwは gamehard_infoのidと同じ値を持つ外部キーである

    note TEXT NOT NULL,
    -- 注釈の内容。例えば、"ドンキーコングバナンザ発売"や　"PS5値下げセール開始"など。

    level INTEGER NOT NULL,
    -- 注釈のレベル。1が最も高い。
);

CREATE INDEX IF NOT EXISTS idx_gamehard_annotation_event_date ON gamehard_annotation(event_date);