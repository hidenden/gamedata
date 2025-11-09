-- 目的:
-- gamehard_weekly テーブルに対して、一時的または恒久的な販売台数の調整値を保持する
-- adjust_units カラムを追加します。主にデータ補正や手動調整を記録する用途です。
--
-- 注意事項:
-- - NOT NULL DEFAULT 0 にしてあるため既存行は自動で 0 に設定されます。
-- - 必要に応じてマイグレーション実行後にバックフィル処理を行ってください。
-- - 集計ビュー(hard_sales 等)を利用している場合は、ビュー定義を更新して
--   adjust_units を考慮した指標に変更する必要があります。

ALTER TABLE gamehard_weekly
ADD COLUMN adjust_units INTEGER NOT NULL DEFAULT 0;


-- ビュー再作成:
-- hard_sales ビューを再作成して、gamehard_weekly.adjust_units を考慮した units を返すようにします。
-- 注意:
-- - units は元の units と adjust_units の合算で返します (units + IFNULL(adjust_units, 0))。
-- - ビュー名やカラムに依存する他のクエリ／ビューがあれば、合わせて修正・テストしてください。
-- - 大規模テーブルでの ALTER/ビュー再作成は運用影響があるため、実行時期とバックアップを確認してください。

DROP VIEW IF EXISTS hard_sales;

CREATE VIEW hard_sales AS
SELECT
    gw.id AS weekly_id,
    gwa.begin_date as begin_date,
    gw.report_date as end_date,
    gw.report_date as report_date,
    gw.period_date as period_date,
    gw.hw as hw,
    -- units は元の units と adjust_units の合算で返す
    (gw.units + IFNULL(gw.adjust_units, 0)) AS units,
    gw.adjust_units as adjust_units,
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


