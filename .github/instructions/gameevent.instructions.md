---
applyTo: '**'
description: 'プロジェクトで使用するゲームイベントのデータ構造の情報を提供します。'
version: 1.1.0
---
- このプロジェクトでは、load_hard_event()を使用して、テーブル `gamehard_event` からデータを取得することができます。
- このテーブルは、ゲームハードの売り上げに影響があったイベントを保存／参照するよう設計されています。
- テーブルのデータは load_hard_event()内で処理され、Pandas DataFrameとして返されます。

以下に、load_hard_event()の返すデータ型の詳細を示します。

event_date: datetime イベントが発生した日付
event_name: str イベントの名前
hw: str イベント売り上げに影響を与えたハードウェアの識別子
hw2: str イベント売り上げに影響を与えたハードウェアの識別子 その2（hwよりは影響が小さい場合に使用）
priority: int イベントの重要度。重要性順に 1 > 2 > 3
report_date: datetime 発生したイベントが売り上げに影響を与えた集計日(index)


