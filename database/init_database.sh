#!/usr/bin/env bash
# This script initializes the database by creating necessary tables.

# SQLite3コマンドを使用してデータベースを初期化する。

# データベースファイルのパスは環境変数 GAMEHARD_DBから取得
# 環境変数の定義がない場合はエラーメッセージを表示してスクリプトを終了する。
if [ -z "$GAMEHARD_DB" ]; then
    echo "Error: GAMEHARD_DB environment variable is not set."
    exit 1
fi

# データベースファイルが存在しない場合は作成する。
if [ ! -f "$GAMEHARD_DB" ]; then
    touch "$GAMEHARD_DB"
    echo "Database file created at $GAMEHARD_DB"
else
    echo "Database file already exists at $GAMEHARD_DB"
fi  

# SQLスクリプトを実行してテーブルを作成する。
# エラーが発生した場合はエラーメッセージを表示してスクリプトを終了する。
# テーブル作成のSQLスクリプトは ./create_tables.sql に保存されている。

if ! sqlite3 "$GAMEHARD_DB" < ./create_tables.sql; then
    echo "Error: Failed to create tables in the database."
    exit 1
fi

echo "Database tables and views created successfully."

# table: gamehard_infoに初期データを投入する
# 初期データソースは ./hard_info.csv である。
# 1行目はヘッダーとして無視し、残りの行をインポートする。
if ! sqlite3 "$GAMEHARD_DB" <<EOF
.mode csv
.import --skip 1 ./hard_info.csv gamehard_info
EOF
then
    echo "Error: Failed to import initial data into gamehard_info table."
    exit 1
fi

# table: gamehard_weeklyに初期データを投入する
# 初期データソースは ../data_source/hard_weekly_init.csv である。
if ! sqlite3 "$GAMEHARD_DB" <<EOF
.mode csv
.import --skip 1 ../data_source/hard_weekly_init.csv gamehard_weekly
EOF
then
    echo "Error: Failed to import initial data into gamehard_weekly table."
    exit 1
fi

exit 0
# スクリプトの終了コードは0で正常終了を示す。
