# Japan Game Data Analysis


## 全体の構造

- data_source/ :   オリジナルのデータスクレイパーとその出力データ(今は使わない)
- database/ : データベース関連のスクリプトとデータ
   - update/ : データベースの更新に使用するスクリプトとデータ, 毎週のデータ更新で使用
   - event/ : イベント関連のデータとスクリプト
- src/gamedata/ : データ処理とグラフ化のためのPythonコード
- tests/ : テストコード
- notebook/ : marimo, jupyter notebook などの分析過程を格納する場所
   - report/ : 公開用の分析レポートの作成､編集を行う場所
   - example/ : データ分析関数群の使用例を示すnotebookを格納する場所
   - dashboard/ : データ分析関数群を使ったダッシュボードnotebookを格納する場所
   - draft/ : 開発用のnotebookを格納する場所
- docs/ : src/gamedataのデータ処理関数のドキュメントを格納する場所
- public/ : 公開用の分析結果を格納する場所､この配下がWebサイトにアップロードされる



## テストの実行

このプロジェクトでは [pytest](https://docs.pytest.org/) を使用してテストを実施します。

### 必要なパッケージのインストール

テスト実行には `pytest` と `pytest-cov` が必要です。プロジェクトの依存関係は `pyproject.toml` に定義されています。

```bash
uv sync --extra test
```

または `pip` を使用する場合:

```bash
pip install pytest pytest-cov
```

### テストの実行

#### 全テストを実行する

```bash
uv run pytest
```

または:

```bash
pytest
```

#### カバレッジレポートを表示する

```bash
uv run pytest --cov=gamedata --cov-report=term-missing
```

#### 特定のテストファイルを実行する

```bash
uv run pytest tests/test_util.py
```

#### 詳細出力で実行する

```bash
uv run pytest -v
```


## ドキュメントの生成

ドキュメントはpdocで作成します｡

```bash
uv run pdoc src/gamedata/ -o docs/
```

## トラブルシュート: uv で gamedata が import できない

macOS では、まれに .venv 配下へ hidden 属性が付与され、Python が .pth を読み飛ばすことがあります。
この状態になると、uv pip install -e . 済みでも gamedata が見えなくなります。

### 症状確認

uv run python -c "import gamedata"

失敗する場合、次で hidden 属性を確認できます。

ls -ldO .venv .venv/lib .venv/lib/python*/site-packages
ls -lO .venv/lib/python*/site-packages/*.pth

出力に hidden が含まれていればこの問題です。

### 復旧（.venv を消さない）

chflags -R nohidden .venv
uv pip install -e .

最後に確認:

uv run python -c "import gamedata; print(gamedata.__file__)"

### 補足

この問題は editable 自体の破損ではなく、.pth 読み込みが hidden 属性で抑止されることが原因です。

