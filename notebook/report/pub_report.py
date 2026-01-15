#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from datetime import datetime
from nbconvert import HTMLExporter
from nbconvert.preprocessors import Preprocessor
from urllib.parse import urljoin

BASEDIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASEDIR)
NOTEBOOK = 'weekly_report.ipynb'
OUTDIR = '../../public'
SITEURL = 'https://gamehardrecord.netlify.app'

class OGPUrlPreprocessor(Preprocessor):
    def preprocess(self, nb, resources):
        rsc_ogp = resources.get('ogp', {})
        report_date = rsc_ogp.get('report_date')
        large_flag = rsc_ogp.get('large', False)
        base_url = rsc_ogp.get('base_url')

        ogp = nb.metadata.get('ogp', {})
        ogp['description'] = rsc_ogp.get('description', '')
        ogp['title'] = f"ゲームハード週販レポート ({report_date.strftime('%Y.%m.%d')})"
        ogp['type'] = 'website'
        ogp['url'] = urljoin(base_url, f"{report_date.year}/weekly_report_{report_date.strftime('%Y%m%d')}.html")

        if large_flag:
            ogp['image'] = f"{base_url}/{report_date.year}/weekly_report_{report_date.strftime('%Y%m%d')}.png"
            ogp['twitter_card'] = "summary_large_image"
        else:
            ogp['image'] = f"{base_url}/small_card.png"
            ogp['twitter_card'] = "summary"

        nb.metadata['ogp'] = ogp
        return nb, resources


from report_config import get_config
config = get_config()
report_date = config["date"]
report_file_name = f"weekly_report_{report_date.strftime('%Y%m%d')}.html"
report_path = f"{OUTDIR}/{report_date.year}/{report_file_name}"

# nbconvertでHTMLに変換（標準テンプレートを使用）
exporter = HTMLExporter(
    template_name = 'ogp',
    extra_template_basedirs = ['../templates'],
    exclude_input = True
)
exporter.exclude_output_prompt = True
exporter.exclude_input_prompt = True
exporter.register_preprocessor(OGPUrlPreprocessor, enabled=True)
rsc = {
    'base_url': SITEURL,
    'report_date': report_date,
    'large': config['large'],
    'description': config['description'],
}

try:
    print("Converting notebook to HTML...")
    body, resources = exporter.from_filename(NOTEBOOK, resources={"ogp": rsc})
    
    # report_pathにファイルが存在したら削除
    if os.path.exists(report_path):
        os.remove(report_path)

    # ファイルに保存  
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(body)
    print(f"Report published successfully to {report_path}. ")
        
except Exception as e:
    print(f"Error during export: {e}")
    import traceback
    traceback.print_exc()