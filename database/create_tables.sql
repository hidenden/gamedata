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

    flag INTEGER,
    -- フラグ。アプリケーションが定めるビットマップフラグが格納される。

    update_at TEXT DEFAULT (CURRENT_TIMESTAMP),
    -- 最終更新日時。レコードが最後に更新された日時が格納される。

    FOREIGN KEY (hw) REFERENCES gamehard_info(id) ON DELETE CASCADE
    /* 外部キー制約。hw gamehard_infoのidを参照する。
     * ON DELETE CASCADEは、gamehard_infoの行が削除された場合、
     * gamehard_weeklyの対応する行も削除されることを意味します
     */
);

DROP TRIGGER IF EXISTS update_gamehard_weekly_update_at;
CREATE TRIGGER IF NOT EXISTS update_gamehard_weekly_update_at
AFTER UPDATE ON gamehard_weekly
FOR EACH ROW
-- 明示的に update_at を更新していない更新のみ反応（再帰防止にもなる）
WHEN NEW.update_at = OLD.update_at
BEGIN
    UPDATE gamehard_weekly
    SET update_at = CURRENT_TIMESTAMP
    WHERE id = NEW.id;
END;

CREATE INDEX IF NOT EXISTS idx_gamehard_weekly_report_date ON gamehard_weekly(report_date);
CREATE INDEX IF NOT EXISTS idx_gamehard_weekly_hw ON gamehard_weekly(hw);


