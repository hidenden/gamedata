#!/usr/bin/env sh

pushd teitenkansoku/raw
./teiten_scraper.py
popd

pushd teitenkansoku/processed
./teiten_filter.py
popd

./union_datasources.py ../data_source/ hard_weekly_init.csv

git diff hard_weekly_init.csv


