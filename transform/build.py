#!/usr/bin/env python3

import sys
import shutil
import geimin_filter
import teiten_filter
import nayose
import seven_days

def build_main():
    print("Build by geimin_filter")
    geimin_filter.geimin_filter_main()
    print("Build by teiten_filter")
    teiten_filter.teiten_filter_main()
    copy_gamesdata()
    
    nayose.nayose_main()
    seven_days.seven_days_main()



def copy_gamesdata():
    print("Copy from raw/gamesdata")
    fname = "gamesdata_2015_12.csv"
    srcdir = "../raw/gamesdata"
    shutil.copy(f"{srcdir}/{fname}", "gamesdata_weekly_hard_201512.csv")

if __name__ == "__main__":
    build_main()
    sys.exit(0)

