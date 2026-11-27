# SPA ダッシュボードの開発と公開

公開先は `/dashboard/` です。サンプルでは直近12週から集計週を選び、その週の販売台数、機種別の内訳、注釈件数を確認できます。ブラウザ内の Python が表示を更新します。

## 初期ビルドとプレビュー

リポジトリのルートで実行します。uv と、`gamehard_info`、`gamehard_weekly`、`gamehard_annotation` を収録した SQLite データベースを用意します。

```bash
export GAMEHARD_DB=/path/to/gamehard.db
dashboard/tools/build.sh
python3 -m http.server 8000 --bind 127.0.0.1 --directory public
```

`GAMEHARD_DB` の既定値は `/Users/hide/Documents/sqlite3/gamehard.db` です。`dashboard/tools/build.sh --db /path/to/gamehard.db` でもビルド元を指定できます。

[ローカルプレビュー](http://127.0.0.1:8000/dashboard/) を開き、週を切り替えて合計と機種別内訳を確認します。初回は CDN から marimo、Pyodide、依存パッケージを取得するため、インターネット接続が必要です。`public` を HTTP サーバーのルートにすると、本番と同じ URL で wheel とデータを読み込めます。

| 入力 | 生成コマンド | 公開資材 |
| --- | --- | --- |
| SQLite の3表 | `uv run --locked python dashboard/tools/export_parquet.py` | `public/dashboard/data/` の Zstandard 圧縮 Parquet 3個と `manifest.json` |
| `src/gamedata/` | `uv run --locked python dashboard/tools/build_wheel.py` | `public/dashboard/packages/` の wheel とファイル名を示す `wheel.json` |
| `dashboard/notebooks/**/*.py` | `uv run --locked python dashboard/tools/export_notebooks.py` | 各 notebook と同じ相対パスの単一 HTML。入口は `public/dashboard/index.html` |

`build.sh` は上の3コマンドを順に実行します。Parquet の出力先は `export_parquet.py --output ディレクトリ` で変更できます。エクスポーターは SQLite の読み取り専用トランザクションで3表の全行・全列をまとめて取得します。週次販売テーブルでは管理列の `flag` と `update_at` も収録します。ブラウザ側では読み込む各表の SHA-256 と列の型を検証します。

## notebook の開発

```bash
uv run --locked marimo edit dashboard/notebooks/index.py
```

ローカルでは `import gamedata as g` のあと、通常どおり `g.load_hard_sales()`、`g.load_hard_info()`、`g.load_hard_annotation()` を使えます。公開版では最初のセルが同じサイトの wheel をインストールし、ローダーが WebAssembly 環境を検出して `/dashboard/data/` に HTTP GET します。週の切替には読み込み済みのデータを使用します。

ページを増やすには、`dashboard/notebooks/index.py` を同じディレクトリに別名でコピーし、先頭の初期化セルを残してタイトルと表示セルを編集します。たとえば `ranking.py` をエクスポートすると `/dashboard/ranking.html` で開けます。ブラウザで追加パッケージを使う場合は初期化セルの依存一覧に Pyodide 対応のパッケージを加えます。

## 初期デプロイ

1. 作業ブランチで一括ビルドとプレビューを実行します。
2. 実装と一緒に `public/dashboard/` 一式をコミットします。生成済みの HTML、wheel、Parquet が Git に含まれていることは `git ls-files public/dashboard` で確認できます。
3. 下記のコマンドを作業ブランチから実行します。既存の Netlify 連携が `pub` の push を検知して `public/` を配信します。

```bash
release_commit=$(git rev-parse HEAD)
git switch pub
git pull --ff-only origin pub
git restore --source="$release_commit" --staged --worktree -- public/dashboard
git diff --cached --stat
git commit -m "Publish dashboard"
git push origin pub
git switch -
```

Netlify のデプロイ完了後、公開サイトの `/dashboard/` を開き、最新の集計週と機種別台数を確認します。

## 更新デプロイ

| 変更内容 | 作業ブランチでの操作 |
| --- | --- |
| 週次データ・注釈の更新 | SQLite の更新後、`export_parquet.py` を実行し、`public/dashboard/data/` をまとめてコミット |
| 表示・操作・ページ追加 | `export_notebooks.py` を実行し、notebook と生成 HTML をコミット。改名・削除した場合は旧 HTML も削除 |
| 集計ロジックの変更 | `build_wheel.py` を実行し、ソース、wheel、`wheel.json` をコミット |
| 公開スキーマの変更 | `SCHEMA_VERSION` と読み書き両側を更新し、`build.sh` で一式を再生成してコミット |

作業開始時は直近の公開資材を含むブランチを使用します。プレビュー後、初期デプロイの `release_commit=...` から始まる手順で更新を公開します。データだけを公開する場合、`git restore` の末尾を `-- public/dashboard/data` にすると、週次更新の対象を3表とマニフェストに絞れます。公開後はページを再読み込みし、新しい集計週を確認します。

公開したダッシュボードを以前の状態へ戻す場合は、`pub` で上記の公開コミットを `git revert <公開コミットのSHA>` し、`git push origin pub` します。
