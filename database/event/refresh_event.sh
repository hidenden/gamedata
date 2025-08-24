#!/usr/bin/env bash
# This script initializes the database by creating necessary tables.

# SQLite3コマンドを使用してイベントデータベースを初期化する。

# データベースファイルのパスは環境変数 GAMEHARD_DBから取得
# 環境変数の定義がない場合はエラーメッセージを表示してスクリプトを終了する。
if [ -z "$GAMEHARD_DB" ]; then
    echo "Error: GAMEHARD_DB environment variable is not set."
    exit 1
fi

if ! sqlite3 "$GAMEHARD_DB" < ./create_event_table.sql; then
    echo "Error: Failed to create event table in the database."
    exit 1
fi
echo "Event table created successfully."

# table: gamehard_eventにデータを投入する
# データソースは ./game_event.csv である。
# 1行目はヘッダーとして無視し、残りの行をインポートする。
if ! sqlite3 "$GAMEHARD_DB" <<EOF
.mode csv
.import --skip 1 ./game_event.csv gamehard_event
EOF
then
    echo "Error: Failed to import initial data into gamehard_event table."
    exit 1
fi

exit 0
# スクリプトの終了コードは0で正常終了を示す。
