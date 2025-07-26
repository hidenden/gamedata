/*
 * これはSQLite3用のSQLスクリプトです。
 * データベースのテーブルを作成します。
 * このスクリプトは、SQLite3のコマンドラインツールで実行できます。
 */

/* 既存テーブルの削除
 * もしテーブルが存在する場合は削除します。(INDEXも含む)
 */
DROP TABLE IF EXISTS gamehard_weekly;
DROP TABLE IF EXISTS gamehard_info;
DROP TABLE IF EXISTS gamehard_events;

 /* テーブルの作成
 */
CREATE TABLE IF NOT EXISTS gamehard_info (
    id TEXT PRIMARY KEY,
    /* idはゲームハードの識別子である。
     * 例えば、"NSW"や"PS5"など。
     * このidは、gamehard_weeklyのhwカラムと対応する。
     */
    launch_date TEXT NOT NULL CHECK(launch_date GLOB '????-??-??'),
    /* launch_dateはゲームハードの発売日である。
     * 形式はYYYY-MM-DDである。
     * 例えば、"2020-11-12"など。
     */
    maker_name TEXT NOT NULL,
    /* maker_nameはゲームハードのメーカー名である。
     * 例えば、"Nintendo"や"Sony"など。
     */
    full_name TEXT NOT NULL
    -- full_nameはゲームハードの正式名称である。例えば、"Nintendo Switch"や"PlayStation 5"など。
    );

create table if not exists gamehard_weekly (
    id TEXT PRIMARY KEY,
    /* idは report_date と hwを繋いだ文字列である。
     * 例えば、2023-10-01のSwitchのデータは "2023-10-01_Switch" となる。
     * これにより、同じ機種、同じ日のデータは重複しない。
     */

    report_date TEXT NOT NULL CHECK(report_date GLOB '????-??-??'),
    -- 従来の end_dateに相当する。集計された末の日付。基本に日曜日〆である

    period_date INTEGER not null,
    -- 集計日数を表す。つまり集計開始日は report_date - period_days + 1 となる。
    -- 通常は7であるが、時々14になることもある。
    

    hw TEXT NOT NULL,
    -- hwは gamehard_infoのidと同じ値を持つ外部キーである　

    units INTEGER NOT NULL CHECK(units >= 0),
    -- 売上台数。売上金額ではない

    FOREIGN KEY (hw) REFERENCES gamehard_info(id) ON DELETE CASCADE
    /* 外部キー制約。hw gamehard_infoのidを参照する。
     * ON DELETE CASCADEは、gamehard_infoの行が削除された場合、
     * gamehard_weeklyの対応する行も削除されることを意味します
     */
);


create table if not exists gamehard_events (
    id TEXT PRIMARY KEY,
    /* idはイベントの識別子である。
     * これは event_date と hw を繋いだ文字列である。    
     * 例えば、"2025-06-05_NS2"など。
     */

    event_date TEXT NOT NULL CHECK(event_date GLOB '????-??-??'),
    -- イベントの日付。形式はYYYY-MM-DDである。

    hw TEXT NOT NULL,
    -- hwは gamehard_infoのidと同じ値を持つ外部キーである

    event_name TEXT NOT NULL,
    -- イベント名。例えば、"ドンキーコングバナンザ発売"や　"PS5値下げセール開始"など。

    FOREIGN KEY (hw) REFERENCES gamehard_info(id) ON DELETE CASCADE
    /* 外部キー制約。hw gamehard_infoのidを参照する。
     * ON DELETE CASCADEは、gamehard_infoの行が削除された場合、
     * gamehard_weeklyの対応する行も削除されることを意味します
     */
);

CREATE INDEX IF NOT EXISTS idx_gamehard_weekly_report_date ON gamehard_weekly(report_date);
CREATE INDEX IF NOT EXISTS idx_gamehard_weekly_hw ON gamehard_weekly(hw);


