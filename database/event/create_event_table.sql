/*
 * これはSQLite3用のSQLスクリプトです。
 * gamehard_event tableを作成します。
 * このスクリプトは、SQLite3のコマンドラインツールで実行できます。
 */

/* 既存テーブルの削除
 * もしテーブルが存在する場合は削除します。(INDEXも含む)
 */
DROP TABLE IF EXISTS gamehard_event;
DROP TABLE IF EXISTS gamehard_events;

 /* テーブルの作成
 */

create table if not exists gamehard_event (
    event_date TEXT NOT NULL CHECK(event_date GLOB '????-??-??'), 
    -- イベントの日付。形式はYYYY-MM-DDである。

    hw TEXT NOT NULL,
    -- hwは gamehard_infoのidと同じ値を持つ外部キーである

    event_name TEXT NOT NULL PRIMARY KEY,
    -- イベント名。例えば、"ドンキーコングバナンザ発売"や　"PS5値下げセール開始"など。

    priority REAL NOT NULL,
    -- イベントの優先度。1が最も高い。

    FOREIGN KEY (hw) REFERENCES gamehard_info(id) ON DELETE CASCADE

    /* 外部キー制約。hw, hw gamehard_infoのidを参照する。
     * ON DELETE CASCADEは、gamehard_infoの行が削除された場合、
     * gamehard_weeklyの対応する行も削除されることを意味します
     */
);

CREATE INDEX IF NOT EXISTS idx_gamehard_event_event_date ON gamehard_event(event_date);