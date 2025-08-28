# レポートのアップデート手順

## 事前準備

1. 新レポートに入れ込む機能追加はmasterにマージする
2. 手元のレポジトリをfetchして最新化しておく

## 新規データの取り込み

1. ***database/update/famitsu.py <今週のハード／ソフト集計ページURL>*** を実行して新規データを取り込み
2. ***database/update/refresh_analysis.py*** を実行してデータ更新を実施

## 新レポートの作成

1. 新レポート作成ブランチ **report_YYYYMMDD** をmasterから派生させる (YYYYMMDDは集計期間末日にあたる日曜日の日付)
2. **report_YYYYMMDD** をチェックアウトする
3. ***notebook/analysis/report_date.py*** を編集。YYYYMMDDに合わせた日付に更新
4. ***notebook/analysis/weekly_report_2025.ipynb*** を開いて再実行
5. weekly_report_2025.ipynb の新規データの確認
6. weekly_report_2025.ipynb に最新データに基づいたコメントを追記

## 新レポートの発行

1. ***notebook/analysis/pub_report.ipynb*** を開いて実行
2. ***public/*** 配下に新しいレポートHTML ***weekly_report_YYYYMMDD.html*** が生成されていることを確認。一応中身も確認
3. **report_YYYYMMDD** ブランチに更新ファイルをgit commit/push
4. **pub** ブランチをチェックアウト
5. カレントブランチ(pub)に　**report_YYYYMMDD** を git merge
6. カレントブランチ(pub)をpush

## 新レポートの広報

- URLは https://gamehardrecord.netlify.app/weekly_report_YYYYMMDD.html 
- 実際にブラウザで開いてURLをコピペし X.com にポストする




