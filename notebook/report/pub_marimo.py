#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import subprocess

BASEDIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASEDIR)
NOTEBOOK = 'weekly_report.py'
OUTDIR = '../../public'
SITEURL = 'https://gamehardrecord.netlify.app'

from report_config import get_config
config = get_config()
report_date = config["date"]
report_file_name = f"weekly_report_{report_date.strftime('%Y%m%d')}.html"
# report_dir = f"{OUTDIR}/{report_date.year}"
report_dir = f"{OUTDIR}/marimo"  # marimo用の作業用ディレクトリ(将来は削除)
report_path = f"{report_dir}/{report_file_name}"

def export_marimo_to_html(notebook_path: str, output_path: str):
    cmd = ["marimo", "export", "html", "--no-include-code", notebook_path,
           "-o", output_path, 
           "--", "--publish", "1"]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("Error:", result.stderr)
    else:
        print(f"Exported to {output_path}")

try:
    print("Converting marimo to HTML...")
    
    # report_pathにファイルが存在したら削除
    if os.path.exists(report_path):
        os.remove(report_path)

    export_marimo_to_html(NOTEBOOK, report_path)
        
except Exception as e:
    print(f"Error during export: {e}")
    import traceback
    traceback.print_exc()