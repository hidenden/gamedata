"""
gamedata.util モジュールのテスト
"""
from datetime import datetime
import pytest
from gamedata.util import report_begin, years_ago, weeks_before


class TestReportBegin:
    """report_begin 関数のテスト"""

    def test_january(self):
        """1月 → 前年 4/1"""
        result = report_begin(datetime(2024, 1, 15))
        assert result == datetime(2023, 4, 1)

    def test_february(self):
        """2月 → 前年 4/1"""
        result = report_begin(datetime(2024, 2, 1))
        assert result == datetime(2023, 4, 1)

    def test_march(self):
        """3月 → 前年 4/1"""
        result = report_begin(datetime(2024, 3, 31))
        assert result == datetime(2023, 4, 1)

    def test_april(self):
        """4月 → 前年 7/1"""
        result = report_begin(datetime(2024, 4, 1))
        assert result == datetime(2023, 7, 1)

    def test_may(self):
        """5月 → 前年 7/1"""
        result = report_begin(datetime(2024, 5, 20))
        assert result == datetime(2023, 7, 1)

    def test_june(self):
        """6月 → 前年 7/1"""
        result = report_begin(datetime(2024, 6, 30))
        assert result == datetime(2023, 7, 1)

    def test_july(self):
        """7月 → 前年 10/1"""
        result = report_begin(datetime(2024, 7, 1))
        assert result == datetime(2023, 10, 1)

    def test_august(self):
        """8月 → 前年 10/1"""
        result = report_begin(datetime(2024, 8, 15))
        assert result == datetime(2023, 10, 1)

    def test_september(self):
        """9月 → 前年 10/1"""
        result = report_begin(datetime(2024, 9, 30))
        assert result == datetime(2023, 10, 1)

    def test_october(self):
        """10月 → 当年 1/1"""
        result = report_begin(datetime(2024, 10, 1))
        assert result == datetime(2024, 1, 1)

    def test_november(self):
        """11月 → 当年 1/1"""
        result = report_begin(datetime(2024, 11, 15))
        assert result == datetime(2024, 1, 1)

    def test_december(self):
        """12月 → 当年 1/1"""
        result = report_begin(datetime(2024, 12, 31))
        assert result == datetime(2024, 1, 1)

    def test_returns_datetime(self):
        """戻り値が datetime 型であること"""
        result = report_begin(datetime(2024, 6, 1))
        assert isinstance(result, datetime)

    def test_time_is_midnight(self):
        """戻り値の時刻が 00:00:00 であること"""
        result = report_begin(datetime(2024, 6, 1, 12, 30, 45))
        assert result.hour == 0
        assert result.minute == 0
        assert result.second == 0


class TestYearsAgo:
    """years_ago 関数のテスト"""

    def test_default_two_years(self):
        """デフォルト（2年前）の動作"""
        result = years_ago(datetime(2024, 6, 15))
        assert result == datetime(2022, 1, 1)

    def test_one_year_ago(self):
        """1年前の動作"""
        result = years_ago(datetime(2024, 6, 15), diff_year=1)
        assert result == datetime(2023, 1, 1)

    def test_five_years_ago(self):
        """5年前の動作"""
        result = years_ago(datetime(2024, 3, 10), diff_year=5)
        assert result == datetime(2019, 1, 1)

    def test_returns_january_first(self):
        """結果が1月1日であること"""
        result = years_ago(datetime(2024, 12, 31), diff_year=3)
        assert result.month == 1
        assert result.day == 1

    def test_returns_datetime(self):
        """戻り値が datetime 型であること"""
        result = years_ago(datetime(2024, 1, 1))
        assert isinstance(result, datetime)

    def test_year_calculation(self):
        """年の計算が正しいこと"""
        result = years_ago(datetime(2024, 1, 1), diff_year=10)
        assert result.year == 2014


class TestWeeksBefore:
    """weeks_before 関数のテスト"""

    def test_default_four_weeks(self):
        """デフォルト（4週間前）の動作"""
        base = datetime(2024, 2, 1)
        result = weeks_before(base)
        assert result == datetime(2024, 1, 4)

    def test_one_week_before(self):
        """1週間前の動作"""
        base = datetime(2024, 2, 1)
        result = weeks_before(base, diff_week=1)
        assert result == datetime(2024, 1, 25)

    def test_zero_weeks(self):
        """0週前（同じ日付）"""
        base = datetime(2024, 2, 1)
        result = weeks_before(base, diff_week=0)
        assert result == base

    def test_returns_datetime(self):
        """戻り値が datetime 型であること"""
        result = weeks_before(datetime(2024, 6, 1))
        assert isinstance(result, datetime)

    def test_crosses_month_boundary(self):
        """月をまたぐ計算が正しいこと"""
        base = datetime(2024, 3, 1)
        result = weeks_before(base, diff_week=2)
        assert result == datetime(2024, 2, 16)

    def test_crosses_year_boundary(self):
        """年をまたぐ計算が正しいこと"""
        base = datetime(2024, 1, 7)
        result = weeks_before(base, diff_week=2)
        assert result == datetime(2023, 12, 24)
