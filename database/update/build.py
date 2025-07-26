#!/usr/bin/env python3

import sys
from union_datasources import union_datasource
from seven_days import fix_7days
import util

def build_main(srcdir:str, outdir:str):
    outfile = f"{outdir}/hard_weekly.csv"

    unioned = union_datasource(srcdir)
    # shared_data = fix_7days(unioned)
    shared_data = unioned  # Assuming unioned data is already in the desired format
    util.save_csv(outfile, util.insert_header(shared_data))

if __name__ == "__main__":
    srcdir = "../../data_source"
    outdir = ".."
    build_main(srcdir, outdir)
    sys.exit(0)

