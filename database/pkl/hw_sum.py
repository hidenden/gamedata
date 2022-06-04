#!/usr/bin/env python3

import sys
import pandas as pd
import datetime
from typing import List
from typing import Dict


'''
データ範囲に発売日が含まれていないものは累計データから取り除く必要がある｡
データ内の各ゲーム機の発売日状況

- DS  2004/12/2
- DC  1998/11/27 OK ここがギリギリ
- GB  1989/4/21 NG
- GBA  2001/3/21 OK
- N64  1996/6/23 NG
- NeoGeoP 1998/10/28 OK  ここが本当のギリギリ
- PS  1994/12/3 NG
- WS  1999/3/4 OK
- SATURN  1994/11/22 NG
- Xbox 2001/11/15 OK
- PKS 1999/1/23 OK
- PSP 2002/12/12 OK
'''

def hw_sum_main():
    make_sumcum()
    make_launchsum()

def make_sumcum():
    hw_weekly_df = pd.read_pickle("weekly_hard_record.pkl")
    hwsum_df = hw_weekly_df.cumsum().drop(["GB", "N64", "PS", "SATURN"], axis=1)
    hwsum_name = "weekly_hard_cumsum"
    hwsum_df.to_pickle(f"{hwsum_name}.pkl")

def make_launchsum():
    launch = {
        "Switch": datetime.datetime(2017, 3, 3),
        "PS5": datetime.datetime(2020, 11, 12),
        "PS4": datetime.datetime(2014, 2, 22),
        "WiiU": datetime.datetime(2012,11,18),
        "3DS": datetime.datetime(2011,2,26),
        'DC': datetime.datetime(1998, 11, 27),
        'DS':datetime.datetime(2004, 12, 2),
        'GBA':datetime.datetime(2001, 3, 21),
        'GC':datetime.datetime(2001, 9, 14),
        'NeoGeoP':datetime.datetime(1998, 10, 28),
        'PS2':datetime.datetime(2000, 3, 4),
        'PS3':datetime.datetime(2006, 11, 11),
        'PSP':datetime.datetime(2002, 12, 12),
        'WS':datetime.datetime(1999, 3, 4),
        'Vita':datetime.datetime(2011, 12, 17),
        'Wii':datetime.datetime(2006, 12, 2),
        'XB360':datetime.datetime(2005, 12, 10),
        'XBOne':datetime.datetime(2014, 9, 4),
        'XSX':datetime.datetime(2020, 11, 10),
        'Xbox':datetime.datetime(2001, 11, 15),
        'PKS':datetime.datetime(1999, 1, 23)
        }
    
    hw_sum = pd.read_pickle("weekly_hard_cumsum.pkl")
    hw_launch_sum = sum_to_launchsum(hw_sum, launch)
    launch_fname = "launch_hard_cumsum"
    hw_launch_sum.to_pickle(f"{launch_fname}.pkl")

def sum_to_launchsum(hw_sum:pd.DataFrame, launch_days:Dict) -> pd.DataFrame :
    new_dict = {}
    dzero = datetime.timedelta(0)
    for hw_key, epoch in launch_days.items():
        this_dict = {}
        for day,num in hw_sum[hw_key].to_dict().items():
            delta = day - epoch
            if (dzero <= delta):
                this_dict[delta.total_seconds() / (24*3600)] = num
#                this_dict[delta] = num
#        this_dict[dzero] = 0.0
        this_dict[dzero.total_seconds()] = 0.0
        new_dict[hw_key] = this_dict
        
    return pd.DataFrame(new_dict).sort_index()

if __name__ == "__main__":
    hw_sum_main()
    sys.exit(0)
