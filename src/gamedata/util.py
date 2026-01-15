from datetime import datetime, timedelta

def report_begin(date: datetime) -> datetime:
    """4半期単位で「約1年前」に相当するレポート開始日を返す。

    入力月に応じて、以下の日付（いずれも月初）を返す。

    - 1〜3月: 前年 4/1
    - 4〜6月: 前年 7/1
    - 7〜9月: 前年 10/1
    - 10〜12月: 当年 1/1

    Args:
        date: 基準となる日付。

    Returns:
        レポート開始日（datetime、時刻は 00:00:00）。
    """
    year = date.year
    month = date.month

    if month in [1, 2, 3]:
        return datetime(year - 1, 4, 1)
    elif month in [4, 5, 6]:
        return datetime(year - 1, 7, 1)
    elif month in [7, 8, 9]:
        return datetime(year - 1, 10, 1)
    else:  # month in [10, 11, 12]
        return datetime(year, 1, 1)


def years_ago(date: datetime, diff_year: int = 2) -> datetime:
    """指定年数だけ遡った年の1月1日を返す。

    Args:
        date: 基準となる日付。
        diff_year: 何年前にするか（年数）。

    Returns:
        (date.year - diff_year) 年の 1/1（datetime、時刻は 00:00:00）。
    """
    year = date.year
    return datetime(year - diff_year, 1, 1)


def weeks_before(date: datetime, diff_week: int = 4) -> datetime:
    """指定週数だけ前の日付を返す。

    Args:
        date: 基準となる日付。
        diff_week: 何週間前にするか（週数）。

    Returns:
        date から diff_week 週間前の datetime。
    """
    return date - timedelta(weeks=diff_week)