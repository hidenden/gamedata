#!/usr/bin/env sh

pushd data_source/teitenkansoku/raw
./build.py
popd

pushd data_source/teitenkansoku/processed
./teiten_filter.py
popd

pushd database/csv_base
./build.py
popd

# pushd database/pkl
# ./build.py
# popd

git diff database/hard_weekly.csv

echo "----------------------------------------------------------------"
echo "NOTE: Please invoke database/parquet/build.ipynb (from pyspark) "
echo "----------------------------------------------------------------"


