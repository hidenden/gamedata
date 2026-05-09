#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import subprocess
from bs4 import BeautifulSoup
from pathlib import Path
from report_config import get_config

# Global setting
BASEDIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASEDIR)
NOTEBOOK = 'weekly_report.py'
HTMLFILE = 'marimo_out.html'
OUTDIR = '../../public'
SITEURL = 'https://gamehardrecord.netlify.app'
CONFIG = get_config()
    
def marimo_export_html(input_path: str, output_path: str):
    cmd = ["marimo", "export", "html", "--no-include-code", input_path,
           "-o", output_path, 
           "--", "--publish", "1"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"Marimo export failed: {result.stderr}")

def load_soup(input_path: str) -> BeautifulSoup:
    with open(input_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")
    # input_pathを削除する
    os.remove(input_path)
    return soup

def insert_og_tags(soup: BeautifulSoup) -> BeautifulSoup:
    head = soup.find("head")
    if not head:
        raise Exception("Error: <head> not found")
    
    # 既存の og / twitter タグを削除（重複防止）
    for tag in head.find_all("meta", attrs={"property": lambda x: x and x.startswith(("og:", "article:"))}):
        tag.decompose()
    for tag in head.find_all("meta", attrs={"name": lambda x: x and x.startswith("twitter:")}):
        tag.decompose()
    
    report_date = CONFIG["date"]
    yymmdd = report_date.strftime("%Y%m%d")
    description = CONFIG["description"]
    
    # Insert new OG and Twitter Card meta tags
    meta_tags = [
        ("property", "og:title", f"ゲームハード週販レポート({yymmdd})"),
        ("property", "og:description", description),
        ("property", "og:image", f"{SITEURL}/{report_date.year}/weekly_report_{yymmdd}.png"),
        ("property", "og:url", f"{SITEURL}/{report_date.year}/weekly_report_{yymmdd}.html"),   # 実際の公開URL
        ("property", "og:type", "website"),
        ("property", "og:site_name", "国内ゲームハード週販レポート"),
        
        # Twitter / X Card
        ("name", "twitter:card", "summary_large_image"),
        ("name", "twitter:title", f"ゲームハード週販レポート({yymmdd})"),
        ("name", "twitter:description", description),
        ("name", "twitter:image", f"{SITEURL}/{report_date.year}/weekly_report_{yymmdd}.png"),
    ]
    
    for attr_type, key, content in meta_tags:
        meta = soup.new_tag("meta")
        meta[attr_type] = key
        meta["content"] = content
        head.append(meta)
        head.append(soup.new_string("\n"))
        
    return soup


def insert_css_link(soup: BeautifulSoup) -> BeautifulSoup:
    head = soup.find("head")
    css_list = ["./custom.css"]
    
    for url in css_list:
        link = soup.new_tag("link")
        link["rel"] = "stylesheet"
        link["href"] = url
        head.append(link)
        head.append(soup.new_string("\n"))
        
    return soup


def save_soup(soup: BeautifulSoup):
    # subdir = "marimo" 
    subdir = str(CONFIG["date"].year)
    report_file_name = f"weekly_report_{CONFIG['date'].strftime('%Y%m%d')}.html"
    report_path = f"{OUTDIR}/{subdir}/{report_file_name}"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(str(soup))
    print(f"Report published successfully: {report_path}")
        

def main():
    # Phase 1
    marimo_export_html(NOTEBOOK, HTMLFILE)
    
    # Phase 2
    soup: BeautifulSoup = load_soup(HTMLFILE)
    
    # Phase 3
    og_soup: BeautifulSoup = insert_og_tags(soup)
    
    # Phase 4
    css_soup: BeautifulSoup = insert_css_link(og_soup)
    
    # Phase 5
    save_soup(css_soup)

if __name__ == "__main__":
    try:
        main()
        sys.exit(0)
    except Exception as e:
        print(f"Error during main execution: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    