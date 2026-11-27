-- 週次販売台数の補正値を追加する。既存の行は補正値 0 となる。
ALTER TABLE gamehard_weekly
ADD COLUMN adjust_units INTEGER NOT NULL DEFAULT 0;
