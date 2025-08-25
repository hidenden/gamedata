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
DROP TABLE IF EXISTS gamehard_weekly_analysis;

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

CREATE TABLE IF NOT EXISTS gamehard_weekly_analysis (
    id TEXT PRIMARY KEY, -- gamehard_weeklyのidと同じ。PKかつFK
    begin_date TEXT NOT NULL CHECK(begin_date GLOB '????-??-??'), -- 集計開始日
    -- つまり report_date - period_days + 1 となる。
    year INTEGER NOT NULL,      -- report_dateの年
    month INTEGER NOT NULL,     -- report_dateの月
    mday INTEGER NOT NULL,      -- report_dateの日
    week INTEGER NOT NULL,      -- report_dateの週番号（ISO週番号）
    delta_day INTEGER NOT NULL, -- 発売から何日後か
    delta_week INTEGER NOT NULL,-- 発売から何週間後か
    delta_month INTEGER NOT NULL,-- 発売から何ヶ月後か
    delta_year INTEGER NOT NULL,-- 発売から何年後か
    avg_units INTEGER NOT NULL, -- 1日あたりの販売台数
    sum_units INTEGER NOT NULL, -- report_date時点での累計台数
    FOREIGN KEY (id) REFERENCES gamehard_weekly(id) ON DELETE CASCADE
);

DROP VIEW IF EXISTS hard_sales;

CREATE VIEW hard_sales AS
SELECT
    gw.id AS weekly_id,
    gwa.begin_date as begin_date,
    gw.report_date as end_date,
    gw.report_date as report_date,
    gw.period_date as period_date,
    gw.hw as hw,
    gw.units as units,
    gwa.year as year,
    gwa.month as month,
    gwa.mday as mday,
    gwa.week as week,
    gwa.delta_day as delta_day,
    gwa.delta_week as delta_week,
    gwa.delta_month as delta_month,
    gwa.delta_year as delta_year,
    gwa.avg_units as avg_units,
    gwa.sum_units as sum_units,
    gi.launch_date as launch_date,
    gi.maker_name as maker_name,
    gi.full_name as full_name
FROM
    gamehard_weekly gw
    INNER JOIN gamehard_weekly_analysis gwa ON gw.id = gwa.id
    INNER JOIN gamehard_info gi ON gw.hw = gi.id;

CREATE INDEX IF NOT EXISTS idx_gamehard_weekly_report_date ON gamehard_weekly(report_date);
CREATE INDEX IF NOT EXISTS idx_gamehard_weekly_hw ON gamehard_weekly(hw);


