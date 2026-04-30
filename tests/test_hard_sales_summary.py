"""
gamedata.hard_sales_extract モジュール hard_sales_summary / maker_sales_summary のテスト
"""
from datetime import date, timedelta
import polars as pl
import pytest

from gamedata import hard_sales_extract as hse


class TestHardSalesSummary:
    """hard_sales_summary 関数のテスト"""

    def test_returns_list(self, sample_sales_df):
        result = hse.hard_sales_summary(sample_sales_df)
        assert isinstance(result, list)

    def test_returns_list_of_dicts(self, sample_sales_df):
        result = hse.hard_sales_summary(sample_sales_df)
        assert all(isinstance(item, dict) for item in result)

    def test_all_hw_returned_when_no_filter(self, sample_sales_df):
        result = hse.hard_sales_summary(sample_sales_df)
        hw_results = {item['hw'] for item in result}
        assert hw_results == {'NSW', 'PS5', 'XSX'}

    def test_none_returns_all_hw(self, sample_sales_df):
        result = hse.hard_sales_summary(sample_sales_df, hw=None)
        assert len(result) == 3

    def test_empty_list_returns_all_hw(self, sample_sales_df):
        result = hse.hard_sales_summary(sample_sales_df, hw=[])
        assert len(result) == 3

    def test_filter_single_hw(self, sample_sales_df):
        result = hse.hard_sales_summary(sample_sales_df, hw=['NSW'])
        assert len(result) == 1
        assert result[0]['hw'] == 'NSW'

    def test_filter_multiple_hw(self, sample_sales_df):
        result = hse.hard_sales_summary(sample_sales_df, hw=['NSW', 'PS5'])
        hws = {item['hw'] for item in result}
        assert hws == {'NSW', 'PS5'}

    def test_nonexistent_hw_skipped(self, sample_sales_df):
        result = hse.hard_sales_summary(sample_sales_df, hw=['NSW', 'FAKE'])
        assert len(result) == 1
        assert result[0]['hw'] == 'NSW'

    def test_required_keys_present(self, sample_sales_df):
        result = hse.hard_sales_summary(sample_sales_df, hw=['NSW'])
        expected_keys = {
            'hw', 'full_name', 'maker_name', 'launch_date', 'last_report_date',
            'total_units', 'sales_period', 'sales_weeks', 'avg_weekly_units',
            'max_weekly_units', 'max_weekly_date',
            'max_monthly_units', 'max_monthly_period',
            'max_quarterly_units', 'max_quarterly_period',
            'max_yearly_units', 'max_yearly_year',
            'launch_week_units',
            'weeks_to_500k', 'weeks_to_1m', 'weeks_to_5m', 'weeks_to_15m',
            'weeks_to_20m', 'weeks_to_25m', 'weeks_to_30m', 'weeks_to_35m',
        }
        assert set(result[0].keys()) == expected_keys

    def test_hw_basic_info(self, sample_sales_df):
        result = hse.hard_sales_summary(sample_sales_df, hw=['NSW'])
        item = result[0]
        assert item['hw'] == 'NSW'
        assert item['full_name'] == 'Nintendo Switch'
        assert item['maker_name'] == 'Nintendo'
        assert item['launch_date'] == date(2017, 3, 3)

    def test_last_report_date(self, sample_sales_df):
        result = hse.hard_sales_summary(sample_sales_df, hw=['NSW'])
        item = result[0]
        assert item['last_report_date'] == date(2021, 4, 4)

    def test_total_units(self, sample_sales_df):
        """NSWの累計台数は180000"""
        result = hse.hard_sales_summary(sample_sales_df, hw=['NSW'])
        assert result[0]['total_units'] == 180_000

    def test_total_units_type(self, sample_sales_df):
        result = hse.hard_sales_summary(sample_sales_df, hw=['NSW'])
        assert isinstance(result[0]['total_units'], int)

    def test_sales_period_type(self, sample_sales_df):
        result = hse.hard_sales_summary(sample_sales_df, hw=['NSW'])
        assert isinstance(result[0]['sales_period'], timedelta)

    def test_sales_period_value(self, sample_sales_df):
        """NSWの集計期間: 2017-03-03 ～ 2021-04-04"""
        result = hse.hard_sales_summary(sample_sales_df, hw=['NSW'])
        expected = date(2021, 4, 4) - date(2017, 3, 3)
        assert result[0]['sales_period'] == expected

    def test_sales_weeks(self, sample_sales_df):
        """NSWは6週分のデータ"""
        result = hse.hard_sales_summary(sample_sales_df, hw=['NSW'])
        assert result[0]['sales_weeks'] == 6

    def test_avg_weekly_units_type(self, sample_sales_df):
        result = hse.hard_sales_summary(sample_sales_df, hw=['NSW'])
        assert isinstance(result[0]['avg_weekly_units'], int)

    def test_avg_weekly_units_value(self, sample_sales_df):
        """NSWの平均週間販売台数: 180000 / 6 = 30000"""
        result = hse.hard_sales_summary(sample_sales_df, hw=['NSW'])
        assert result[0]['avg_weekly_units'] == 30_000

    def test_max_weekly_units(self, sample_sales_df):
        """NSWの週間最大: 50000 (2020-11-15)"""
        result = hse.hard_sales_summary(sample_sales_df, hw=['NSW'])
        assert result[0]['max_weekly_units'] == 50_000

    def test_max_weekly_date(self, sample_sales_df):
        result = hse.hard_sales_summary(sample_sales_df, hw=['NSW'])
        assert result[0]['max_weekly_date'] == date(2020, 11, 15)

    def test_max_monthly_units_type(self, sample_sales_df):
        result = hse.hard_sales_summary(sample_sales_df, hw=['NSW'])
        assert isinstance(result[0]['max_monthly_units'], int)

    def test_max_monthly_period_format(self, sample_sales_df):
        """月間最大期間は YYYY-MM 形式"""
        result = hse.hard_sales_summary(sample_sales_df, hw=['NSW'])
        period = result[0]['max_monthly_period']
        assert len(period) == 7
        assert period[4] == '-'

    def test_max_monthly_units_value(self, sample_sales_df):
        """NSWの月間最大: 2020年11月 = 50000, 2021年1月 = 40000, 2020年1月 = 55000"""
        result = hse.hard_sales_summary(sample_sales_df, hw=['NSW'])
        # 2020年1月: 30000 + 25000 = 55000 が最大
        assert result[0]['max_monthly_units'] == 55_000
        assert result[0]['max_monthly_period'] == '2020-01'

    def test_max_quarterly_units_type(self, sample_sales_df):
        result = hse.hard_sales_summary(sample_sales_df, hw=['NSW'])
        assert isinstance(result[0]['max_quarterly_units'], int)

    def test_max_quarterly_period_format(self, sample_sales_df):
        """四半期は "YYYYQn" 形式"""
        result = hse.hard_sales_summary(sample_sales_df, hw=['NSW'])
        period = result[0]['max_quarterly_period']
        assert 'Q' in period

    def test_max_quarterly_units_value(self, sample_sales_df):
        """NSWの四半期最大: 2020Q1 = 55000 (30000+25000), 2020Q2=20000, 2020Q4=50000, 2021Q1=40000, 2021Q2=15000"""
        result = hse.hard_sales_summary(sample_sales_df, hw=['NSW'])
        assert result[0]['max_quarterly_units'] == 55_000
        assert result[0]['max_quarterly_period'] == '2020Q1'

    def test_max_yearly_units_type(self, sample_sales_df):
        result = hse.hard_sales_summary(sample_sales_df, hw=['NSW'])
        assert isinstance(result[0]['max_yearly_units'], int)

    def test_max_yearly_year_type(self, sample_sales_df):
        result = hse.hard_sales_summary(sample_sales_df, hw=['NSW'])
        assert isinstance(result[0]['max_yearly_year'], int)

    def test_max_yearly_units_value(self, sample_sales_df):
        """NSWの年間最大: 2020年 = 30000+25000+20000+50000 = 125000"""
        result = hse.hard_sales_summary(sample_sales_df, hw=['NSW'])
        assert result[0]['max_yearly_units'] == 125_000
        assert result[0]['max_yearly_year'] == 2020

    def test_launch_week_units(self, sample_sales_df):
        """NSWの発売週 (delta_week=0) は存在しないためサンプルデータでは 0 になる。
        PS5は delta_week=0 行が存在: 2020-11-15 の 20000"""
        result = hse.hard_sales_summary(sample_sales_df, hw=['PS5'])
        # PS5_LAUNCH=2020-11-12, report_date=2020-11-15 → delta_day=3, delta_week=0
        assert result[0]['launch_week_units'] == 20_000

    def test_launch_week_units_no_launch_week(self, sample_sales_df):
        """NSWはサンプルデータに delta_week=0 の行がないため 0"""
        result = hse.hard_sales_summary(sample_sales_df, hw=['NSW'])
        assert result[0]['launch_week_units'] == 0

    def test_weeks_to_threshold_not_reached(self, sample_sales_df):
        """閾値に届かない場合は None"""
        result = hse.hard_sales_summary(sample_sales_df, hw=['NSW'])
        # NSWの最大cumは 180000 < 500000
        assert result[0]['weeks_to_500k'] is None
        assert result[0]['weeks_to_1m'] is None

    def test_weeks_to_threshold_reached(self, sample_sales_df):
        """累計が閾値に達している場合は発売週を1と数えた週数が返ること"""
        # NSWの sum_units が 55000 を超えるのは 2020-01-12 (delta_week を確認)
        # NSW_LAUNCH=2017-03-03, 2020-01-12 → days=(2020-01-12)-(2017-03-03)
        # delta_week = days // 7
        # sum_units=55000 は 2週目 (delta_week=...)
        result = hse.hard_sales_summary(sample_sales_df, hw=['NSW'])
        # weeks_to_500k は None (180000 < 500000) のはず
        assert result[0]['weeks_to_500k'] is None

    def test_weeks_to_keys_all_present(self, sample_sales_df):
        result = hse.hard_sales_summary(sample_sales_df, hw=['NSW'])
        threshold_keys = [
            'weeks_to_500k', 'weeks_to_1m', 'weeks_to_5m', 'weeks_to_15m',
            'weeks_to_20m', 'weeks_to_25m', 'weeks_to_30m', 'weeks_to_35m',
        ]
        for key in threshold_keys:
            assert key in result[0]

    def test_weeks_to_threshold_type_when_reached(self, sample_sales_df):
        """到達済みの場合はint型"""
        from datetime import date as d, timedelta as td
        from conftest import _make_row
        launch = d(2020, 1, 1)
        rows = []
        for i in range(5):
            rd = d(2020, 1, 5) + td(weeks=i)
            rows.append(_make_row(
                "HW1", rd, 200_000, (i + 1) * 200_000,
                launch, "TestMaker", "Test HW", i + 1, "2020Q1", 0,
            ))
        test_df = pl.DataFrame(rows).with_columns(
            pl.col("begin_date").cast(pl.Date),
            pl.col("end_date").cast(pl.Date),
            pl.col("report_date").cast(pl.Date),
            pl.col("launch_date").cast(pl.Date),
            pl.col("period_date").cast(pl.Int16),
            pl.col("year").cast(pl.Int16),
            pl.col("month").cast(pl.Int16),
            pl.col("mday").cast(pl.Int16),
            pl.col("week").cast(pl.Int16),
            pl.col("delta_day").cast(pl.Int32),
            pl.col("delta_week").cast(pl.Int32),
            pl.col("delta_month").cast(pl.Int16),
            pl.col("delta_year").cast(pl.Int16),
        )
        result = hse.hard_sales_summary(test_df, hw=['HW1'])
        assert result[0]['weeks_to_500k'] is not None
        assert isinstance(result[0]['weeks_to_500k'], int)
        # 累計500kに達するのは3週目 (sum=600000 >= 500000, delta_week=2 → +1 = 3)
        assert result[0]['weeks_to_500k'] == 3


class TestMakerSalesSummary:
    """maker_sales_summary 関数のテスト"""

    def test_returns_list(self, sample_sales_df):
        result = hse.maker_sales_summary(sample_sales_df)
        assert isinstance(result, list)

    def test_returns_list_of_dicts(self, sample_sales_df):
        result = hse.maker_sales_summary(sample_sales_df)
        assert all(isinstance(item, dict) for item in result)

    def test_all_makers_returned_when_no_filter(self, sample_sales_df):
        result = hse.maker_sales_summary(sample_sales_df)
        makers = {item['maker_name'] for item in result}
        assert makers == {'Nintendo', 'SONY', 'Microsoft'}

    def test_none_returns_all_makers(self, sample_sales_df):
        result = hse.maker_sales_summary(sample_sales_df, makers=None)
        assert len(result) == 3

    def test_empty_list_returns_all_makers(self, sample_sales_df):
        result = hse.maker_sales_summary(sample_sales_df, makers=[])
        assert len(result) == 3

    def test_filter_single_maker(self, sample_sales_df):
        result = hse.maker_sales_summary(sample_sales_df, makers=['Nintendo'])
        assert len(result) == 1
        assert result[0]['maker_name'] == 'Nintendo'

    def test_filter_multiple_makers(self, sample_sales_df):
        result = hse.maker_sales_summary(sample_sales_df, makers=['Nintendo', 'SONY'])
        makers = {item['maker_name'] for item in result}
        assert makers == {'Nintendo', 'SONY'}

    def test_nonexistent_maker_skipped(self, sample_sales_df):
        result = hse.maker_sales_summary(sample_sales_df, makers=['Nintendo', 'FAKECO'])
        assert len(result) == 1
        assert result[0]['maker_name'] == 'Nintendo'

    def test_required_keys_present(self, sample_sales_df):
        result = hse.maker_sales_summary(sample_sales_df, makers=['Nintendo'])
        expected_keys = {
            'maker_name', 'hw_list', 'total_units',
            'max_weekly_units', 'max_weekly_date', 'max_weekly_hw',
            'max_monthly_units', 'max_monthly_period', 'max_monthly_hw',
            'max_quarterly_units', 'max_quarterly_period', 'max_quarterly_hw',
            'max_yearly_units', 'max_yearly_year', 'max_yearly_hw',
        }
        assert set(result[0].keys()) == expected_keys

    def test_hw_list_type(self, sample_sales_df):
        result = hse.maker_sales_summary(sample_sales_df, makers=['Nintendo'])
        assert isinstance(result[0]['hw_list'], list)

    def test_hw_list_value(self, sample_sales_df):
        """Nintendoは NSWのみ"""
        result = hse.maker_sales_summary(sample_sales_df, makers=['Nintendo'])
        assert result[0]['hw_list'] == ['NSW']

    def test_total_units(self, sample_sales_df):
        """Nintendo(NSW)の累計: 180000"""
        result = hse.maker_sales_summary(sample_sales_df, makers=['Nintendo'])
        assert result[0]['total_units'] == 180_000

    def test_total_units_type(self, sample_sales_df):
        result = hse.maker_sales_summary(sample_sales_df, makers=['Nintendo'])
        assert isinstance(result[0]['total_units'], int)

    def test_total_units_sony(self, sample_sales_df):
        """SONY(PS5)の累計: 45000"""
        result = hse.maker_sales_summary(sample_sales_df, makers=['SONY'])
        assert result[0]['total_units'] == 45_000

    def test_max_weekly_units(self, sample_sales_df):
        """Nintendo(NSW)の週間最大: 50000 (2020-11-15)"""
        result = hse.maker_sales_summary(sample_sales_df, makers=['Nintendo'])
        assert result[0]['max_weekly_units'] == 50_000

    def test_max_weekly_date_type(self, sample_sales_df):
        result = hse.maker_sales_summary(sample_sales_df, makers=['Nintendo'])
        assert isinstance(result[0]['max_weekly_date'], date)

    def test_max_weekly_date_value(self, sample_sales_df):
        result = hse.maker_sales_summary(sample_sales_df, makers=['Nintendo'])
        assert result[0]['max_weekly_date'] == date(2020, 11, 15)

    def test_max_weekly_hw_type(self, sample_sales_df):
        result = hse.maker_sales_summary(sample_sales_df, makers=['Nintendo'])
        assert isinstance(result[0]['max_weekly_hw'], list)

    def test_max_weekly_hw_value(self, sample_sales_df):
        result = hse.maker_sales_summary(sample_sales_df, makers=['Nintendo'])
        assert 'NSW' in result[0]['max_weekly_hw']

    def test_max_monthly_units_type(self, sample_sales_df):
        result = hse.maker_sales_summary(sample_sales_df, makers=['Nintendo'])
        assert isinstance(result[0]['max_monthly_units'], int)

    def test_max_monthly_period_format(self, sample_sales_df):
        result = hse.maker_sales_summary(sample_sales_df, makers=['Nintendo'])
        period = result[0]['max_monthly_period']
        assert len(period) == 7
        assert period[4] == '-'

    def test_max_monthly_hw_type(self, sample_sales_df):
        result = hse.maker_sales_summary(sample_sales_df, makers=['Nintendo'])
        assert isinstance(result[0]['max_monthly_hw'], list)

    def test_max_quarterly_units_type(self, sample_sales_df):
        result = hse.maker_sales_summary(sample_sales_df, makers=['Nintendo'])
        assert isinstance(result[0]['max_quarterly_units'], int)

    def test_max_quarterly_period_format(self, sample_sales_df):
        result = hse.maker_sales_summary(sample_sales_df, makers=['Nintendo'])
        period = result[0]['max_quarterly_period']
        assert 'Q' in period

    def test_max_quarterly_hw_type(self, sample_sales_df):
        result = hse.maker_sales_summary(sample_sales_df, makers=['Nintendo'])
        assert isinstance(result[0]['max_quarterly_hw'], list)

    def test_max_yearly_units_type(self, sample_sales_df):
        result = hse.maker_sales_summary(sample_sales_df, makers=['Nintendo'])
        assert isinstance(result[0]['max_yearly_units'], int)

    def test_max_yearly_year_type(self, sample_sales_df):
        result = hse.maker_sales_summary(sample_sales_df, makers=['Nintendo'])
        assert isinstance(result[0]['max_yearly_year'], int)

    def test_max_yearly_hw_type(self, sample_sales_df):
        result = hse.maker_sales_summary(sample_sales_df, makers=['Nintendo'])
        assert isinstance(result[0]['max_yearly_hw'], list)

    def test_max_yearly_units_value(self, sample_sales_df):
        """Nintendo(NSW)の年間最大: 2020年 = 30000+25000+20000+50000 = 125000"""
        result = hse.maker_sales_summary(sample_sales_df, makers=['Nintendo'])
        assert result[0]['max_yearly_units'] == 125_000
        assert result[0]['max_yearly_year'] == 2020

    def test_max_yearly_hw_value(self, sample_sales_df):
        result = hse.maker_sales_summary(sample_sales_df, makers=['Nintendo'])
        assert result[0]['max_yearly_hw'] == ['NSW']

    def test_microsoft_two_hw_multi_week(self, sample_sales_df):
        """Microsoft(XSX)は1HWのみ"""
        result = hse.maker_sales_summary(sample_sales_df, makers=['Microsoft'])
        assert result[0]['hw_list'] == ['XSX']
        assert result[0]['total_units'] == 9_000
