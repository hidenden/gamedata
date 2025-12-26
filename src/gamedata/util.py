from datetime import datetime, timedelta

# 4半期単位で約1年前の日付を計算して返す関数
# 引数にはdatetimeオブジェクトを渡す
# 入力が　1月から3月の日付なら前年の4月1日を返す
# 入力が4月から6月の日付なら前年の7月1日を返す
# 入力が7月から9月の日付なら前年の10月1日を返す
# 入力が10月から12月の日付ならその年の1月1日を返す
def report_begin(date: datetime) -> datetime:
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


# 引数で与えられた日付のn年前の1月1日のdatetimeオブジェクトを返す関数
def years_ago(date: datetime, diff_year:int = 2) -> datetime:
    year = date.year
    return datetime(year - diff_year, 1, 1)

def weeks_before(date: datetime, diff_week:int = 4) -> datetime:
    return date - timedelta(weeks=diff_week)