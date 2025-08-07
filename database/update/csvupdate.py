#! /usr/bin/env python3
# コマンドライン引数で指定されたCSVファイルを読み込み、データベースにアップサートするスクリプト
# データベースのパスは環境変数 DATABASE_PATH から取得する
# データベースへの投入はは　update_util.py の upsert_to_database 関数を使用する

import os
import sys
import csv
from typing import List, Tuple
from database.update.update_util import upsert_to_database

def read_csv_file(file_path: str) -> List[Tuple]:
    """
    Read a CSV file and return its content as a list of tuples.

    Args:
        file_path (str): Path to the CSV file.

    Returns:
        List[Tuple]: List of rows, where each row is a tuple.
    """
    with open(file_path, mode='r', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        data = [tuple(row) for row in reader]
    return data

def main():
    # -c, -f オプションの有無を判定
    dryrun = True
    precheck = True
    args = sys.argv[1:]
    if '-c' in args:
        dryrun = False
        args.remove('-c')
    if '-f' in args:
        precheck = False
        args.remove('-f')
    if len(args) != 1:
        print("Usage: python csvupdate.py [-c] [-f] <csv_file_path>")
        sys.exit(1)

    csv_file_path = args[0]

    if not os.path.isfile(csv_file_path):
        print(f"Error: The file {csv_file_path} does not exist.")
        sys.exit(1)

    # 環境変数からデータベースのパスを取得
    db_path = os.getenv('DATABASE_PATH')
    if not db_path:
        print("Error: DATABASE_PATH environment variable is not set.")
        sys.exit(1)

    # CSVファイルを読み込み
    newdata = read_csv_file(csv_file_path)

    # データベースにアップサート
    upsert_to_database(db_path, newdata, precheck=precheck, dryrun=dryrun)
    if dryrun:
        print("Dryrun: CSV data checked but not upserted to the database.")
    else:
        print("CSV data has been successfully upserted to the database.")

if __name__ == "__main__":
    main()
    
    exit(0)


