# ローカル環境メモ

手元Mac環境でpysparkを実行する方法のメモ書きです(忘れるので)

## VSCodeで利用する方法

pysparkを PYSPARK_DRIVER_PYTHONをpython3で実行する

```shell
$ ./run_spark.sh
```

スクリプトの中身はこれ｡

    export PYSPARK_PYTHON=/opt/homebrew/bin/python3 
    export PYSPARK_DRIVER_PYTHON=/opt/homebrew/bin/python3 
    export PYSPARK_DRIVER_PYTHON_OPTS=""

    /opt/homebrew/bin/pyspark

次にVSCodeを実行し `~/Development/gamedata` を開きます｡

gamedata配下の ipynbファイルを開くとjupyter notebook環境になります｡


### 初めての実行時

一度jupyter notebookを実行すると環境ができあがってしまうのですが､
初めての場合や環境の再構築の場合は以下の手順になります｡

1. コマンドパレットで "Create New jupyter notebook" を実行
2. Pythonインタプリタの選択になるので `/opt/homebrew/bin/python3` を選びます
3. 初めての場合は pysparkのライブラリなどが無いので､ノート内で `%pip install pyspark` などを実行し不足するライブラリをインストールします

注意事項: カレントディレクトリはnotebookの保存ディレクトリになります｡
なので新規ファイルを先に所定のディレクトリに保存してカレントディレクトリを
希望の位置に固定したほうがいいです｡



## ブラウザで利用する方法

以下のように pysparkコマンドを実行する

```shell
$ pyspark
```

環境変数はこうなっているので､jupyter labが動き始めます

    PYSPARK_PYTHON=/opt/homebrew/bin/python3
    PYSPARK_DRIVER_PYTHON=/opt/homebrew/bin/jupyter
    PYSPARK_DRIVER_PYTHON_OPTS=lab

ブラウザも自動で立ち上がるので､ブラウザ内でjupyter labを使用します｡

## データのアップデート方法

1. gamedataディレクトリ直下で `udpate.sh`を実行します｡
2. ***database/parquet/build.ipynb*** を開いて､全体を再実行します｡

