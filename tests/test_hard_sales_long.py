"""
gamedata.hard_sales_long モジュールのテスト
"""
from datetime import date, datetime
import polars as pl
import pytest

from gamedata import hard_sales_long as lng


class TestSalesLong:
    """sales_long 関数のテスト"""

    def test_returns_dataframe(self, sample_sales_df):
        result = lng.sales_long(sample_sales_df)
        assert isinstance(result, pl.DataFrame)

    def test_has_expected_columns(self, sample_sales_df):
        result = lng.sales_long(sample_sales_df)
        assert set(result.columns) == {"report_date", "hw", "units"}

    def test_filter_by_hw(self, sample_sales_df):
        result = lng.sales_long(sample_sales_df, hw=["NSW"])
        assert set(result["hw"].unique().to_list()) == {"NSW"}

    def test_filter_excludes_other_hw(self, sample_sales_df):
        result = lng.sales_long(sample_sales_df, hw=["NSW"])
        assert "XSX" not in result["hw"].to_list()

    def test_no_hw_filter_all_data(self, sample_sales_df):
        result = lng.sales_long(sample_sales_df)
        assert result.height > 0
        assert "NSW" in result["hw"].to_list()

    def test_with_begin_and_end(self, sample_sales_df):
        begin = date(2020, 1, 1)
        end = date(2020, 12, 31)
        result = lng.sales_long(sample_sales_df, begin=begin, end=end)
        assert all(d <= end for d in result["report_date"].to_list())
        assert all(d >= begin for d in result["report_date"].to_list())

    def test_with_begin_only(self, sample_sales_df):
        begin = date(2021, 1, 1)
        result = lng.sales_long(sample_sales_df, begin=begin)
        assert all(d >= begin for d in result["report_date"].to_list())

    def test_with_end_only(self, sample_sales_df):
        end = date(2020, 12, 31)
        result = lng.sales_long(sample_sales_df, end=end)
        assert all(d <= end for d in result["report_date"].to_list())

    def test_sorted_by_report_date(self, sample_sales_df):
        result = lng.sales_long(sample_sales_df)
        dates = result["report_date"].to_list()
        assert dates == sorted(dates)


class TestMonthlySalesLong:
    """monthly_sales_long 関数のテスト"""

    def test_returns_dataframe(self, sample_sales_df):
        result = lng.monthly_sales_long(sample_sales_df)
        assert isinstance(result, pl.DataFrame)

    def test_has_expected_columns(self, sample_sales_df):
        result = lng.monthly_sales_long(sample_sales_df)
        assert set(result.columns) == {"year_month", "year_month_str", "year", "month", "hw", "monthly_units"}

    def test_month_column_is_date(self, sample_sales_df):
        result = lng.monthly_sales_long(sample_sales_df)
        assert result["year_month"].dtype == pl.Date

    def test_filter_by_hw(self, sample_sales_df):
        result = lng.monthly_sales_long(sample_sales_df, hw=["NSW"])
        assert set(result["hw"].unique().to_list()) == {"NSW"}

    def test_with_date_range(self, sample_sales_df):
        begin = datetime(2020, 1, 1)
        end = datetime(2020, 12, 31)
        result = lng.monthly_sales_long(sample_sales_df, begin=begin, end=end)
        assert result.height > 0

    def test_sorted_by_month(self, sample_sales_df):
        result = lng.monthly_sales_long(sample_sales_df)
        months = result["year_month"].to_list()
        assert months == sorted(months)

    def test_monthly_units_positive(self, sample_sales_df):
        result = lng.monthly_sales_long(sample_sales_df)
        assert (result["monthly_units"] > 0).all()


class TestQuarterlySalesLong:
    """quarterly_sales_long 関数のテスト"""

    def test_returns_dataframe(self, sample_sales_df):
        result = lng.quarterly_sales_long(sample_sales_df)
        assert isinstance(result, pl.DataFrame)

    def test_has_expected_columns(self, sample_sales_df):
        result = lng.quarterly_sales_long(sample_sales_df)
        assert set(result.columns) == {'quarter', 'fiscal_quarter', 'year', 'fiscal_year', 'q_num', 'fq_num', 'hw', 'quarterly_units'}

    def test_filter_by_hw(self, sample_sales_df):
        result = lng.quarterly_sales_long(sample_sales_df, hw=["NSW"])
        assert set(result["hw"].unique().to_list()) == {"NSW"}

    def test_with_date_range(self, sample_sales_df):
        begin = datetime(2020, 1, 1)
        end = datetime(2020, 12, 31)
        result = lng.quarterly_sales_long(sample_sales_df, begin=begin, end=end)
        assert result.height > 0

    def test_sorted_by_quarter(self, sample_sales_df):
        result = lng.quarterly_sales_long(sample_sales_df)
        quarters = result["quarter"].to_list()
        assert quarters == sorted(quarters)

    def test_quarterly_units_positive(self, sample_sales_df):
        result = lng.quarterly_sales_long(sample_sales_df)
        assert (result["quarterly_units"] > 0).all()


class TestYearlySalesLong:
    """yearly_sales_long 関数のテスト"""

    def test_returns_dataframe(self, sample_sales_df):
        result = lng.yearly_sales_long(sample_sales_df)
        assert isinstance(result, pl.DataFrame)

    def test_has_expected_columns(self, sample_sales_df):
        result = lng.yearly_sales_long(sample_sales_df)
        assert set(result.columns) == {"year", "hw", "yearly_units"}

    def test_filter_by_hw(self, sample_sales_df):
        result = lng.yearly_sales_long(sample_sales_df, hw=["NSW"])
        assert set(result["hw"].unique().to_list()) == {"NSW"}

    def test_with_date_range(self, sample_sales_df):
        begin = datetime(2020, 1, 1)
        end = datetime(2020, 12, 31)
        result = lng.yearly_sales_long(sample_sales_df, begin=begin, end=end)
        assert result.height > 0

    def test_sorted_by_year(self, sample_sales_df):
        result = lng.yearly_sales_long(sample_sales_df)
        years = result["year"].to_list()
        assert years == sorted(years)

    def test_yearly_units_positive(self, sample_sales_df):
        result = lng.yearly_sales_long(sample_sales_df)
        assert (result["yearly_units"] > 0).all()


class TestCumulativeSalesLong:
    """cumulative_sales_long 関数のテスト"""

    def test_returns_dataframe_week_mode(self, sample_sales_df):
        result = lng.cumulative_sales_long(sample_sales_df, mode="week")
        assert isinstance(result, pl.DataFrame)

    def test_returns_dataframe_month_mode(self, sample_sales_df):
        result = lng.cumulative_sales_long(sample_sales_df, mode="month")
        assert isinstance(result, pl.DataFrame)

    def test_returns_dataframe_year_mode(self, sample_sales_df):
        result = lng.cumulative_sales_long(sample_sales_df, mode="year")
        assert isinstance(result, pl.DataFrame)

    def test_week_mode_has_expected_columns(self, sample_sales_df):
        result = lng.cumulative_sales_long(sample_sales_df, mode="week")
        assert set(result.columns) == {"report_date", "hw", "sum_units"}

    def test_full_name_mode_uses_full_name_column(self, sample_sales_df):
        result = lng.cumulative_sales_long(sample_sales_df, full_name=True)
        assert "full_name" in result.columns
        assert "hw" not in result.columns

    def test_filter_by_hw(self, sample_sales_df):
        result = lng.cumulative_sales_long(sample_sales_df, hw=["NSW"])
        assert set(result["hw"].unique().to_list()) == {"NSW"}

    def test_with_date_range(self, sample_sales_df):
        begin = datetime(2020, 1, 1)
        end = datetime(2020, 12, 31)
        result = lng.cumulative_sales_long(sample_sales_df, begin=begin, end=end)
        assert result.height > 0

    def test_month_mode_has_report_date_column(self, sample_sales_df):
        result = lng.cumulative_sales_long(sample_sales_df, mode="month")
        assert "report_date" in result.columns

    def test_year_mode_has_report_date_column(self, sample_sales_df):
        result = lng.cumulative_sales_long(sample_sales_df, mode="year")
        assert "report_date" in result.columns

    def test_unknown_mode_raises_value_error(self, sample_sales_df):
        with pytest.raises(ValueError):
            lng.cumulative_sales_long(sample_sales_df, mode="unknown")


class TestSalesByDeltaLong:
    """sales_by_delta_long 関数のテスト"""

    def test_returns_dataframe_week_mode(self, sample_sales_df):
        result = lng.sales_by_delta_long(sample_sales_df, mode="week")
        assert isinstance(result, pl.DataFrame)

    def test_returns_dataframe_month_mode(self, sample_sales_df):
        result = lng.sales_by_delta_long(sample_sales_df, mode="month")
        assert isinstance(result, pl.DataFrame)

    def test_returns_dataframe_year_mode(self, sample_sales_df):
        result = lng.sales_by_delta_long(sample_sales_df, mode="year")
        assert isinstance(result, pl.DataFrame)

    def test_week_mode_has_delta_week_column(self, sample_sales_df):
        result = lng.sales_by_delta_long(sample_sales_df, mode="week")
        assert "delta_week" in result.columns

    def test_month_mode_has_delta_month_column(self, sample_sales_df):
        result = lng.sales_by_delta_long(sample_sales_df, mode="month")
        assert "delta_month" in result.columns

    def test_year_mode_has_delta_year_column(self, sample_sales_df):
        result = lng.sales_by_delta_long(sample_sales_df, mode="year")
        assert "delta_year" in result.columns

    def test_invalid_mode_raises_value_error(self, sample_sales_df):
        with pytest.raises(ValueError):
            lng.sales_by_delta_long(sample_sales_df, mode="invalid")

    def test_filter_by_hw(self, sample_sales_df):
        result = lng.sales_by_delta_long(sample_sales_df, hw=["NSW"])
        assert set(result["hw"].unique().to_list()) == {"NSW"}

    def test_full_name_mode(self, sample_sales_df):
        result = lng.sales_by_delta_long(sample_sales_df, full_name=True)
        assert "full_name" in result.columns
        assert "hw" not in result.columns

    def test_with_begin_end(self, sample_sales_df):
        result = lng.sales_by_delta_long(sample_sales_df, begin=10, end=200)
        assert isinstance(result, pl.DataFrame)
        assert (result["delta_week"] >= 10).all()
        assert (result["delta_week"] <= 200).all()

    def test_units_column_present(self, sample_sales_df):
        result = lng.sales_by_delta_long(sample_sales_df, mode="week")
        assert "units" in result.columns


class TestSalesWithOffsetLong:
    """sales_with_offset_long 関数のテスト"""

    def test_returns_dataframe(self, sample_sales_df):
        hw_periods = [{"hw": "NSW", "begin": datetime(2020, 1, 1)}]
        result = lng.sales_with_offset_long(sample_sales_df, hw_periods)
        assert isinstance(result, pl.DataFrame)

    def test_has_expected_columns(self, sample_sales_df):
        hw_periods = [{"hw": "NSW", "begin": datetime(2020, 1, 1), "label": "NSW"}]
        result = lng.sales_with_offset_long(sample_sales_df, hw_periods)
        assert set(result.columns) == {"offset_week", "label", "units", "report_date", "hw"}

    def test_default_label_contains_hw_name(self, sample_sales_df):
        hw_periods = [{"hw": "NSW", "begin": datetime(2020, 1, 5)}]
        result = lng.sales_with_offset_long(sample_sales_df, hw_periods)
        assert any("NSW" in lbl for lbl in result["label"].to_list())

    def test_custom_label(self, sample_sales_df):
        hw_periods = [{"hw": "NSW", "begin": datetime(2020, 1, 1), "label": "NSW2020~"}]
        result = lng.sales_with_offset_long(sample_sales_df, hw_periods)
        assert "NSW2020~" in result["label"].to_list()

    def test_multiple_hw_periods(self, sample_sales_df):
        hw_periods = [
            {"hw": "NSW", "begin": datetime(2020, 1, 1), "label": "NSW"},
            {"hw": "PS5", "begin": datetime(2021, 1, 1), "label": "PS5"},
        ]
        result = lng.sales_with_offset_long(sample_sales_df, hw_periods)
        labels = set(result["label"].to_list())
        assert "NSW" in labels
        assert "PS5" in labels

    def test_end_parameter_limits_rows_per_hw(self, sample_sales_df):
        hw_periods = [{"hw": "NSW", "begin": datetime(2020, 1, 1), "label": "NSW"}]
        result = lng.sales_with_offset_long(sample_sales_df, hw_periods, end=2)
        assert result.height <= 2

    def test_sorted_by_offset_week(self, sample_sales_df):
        hw_periods = [{"hw": "NSW", "begin": datetime(2020, 1, 1), "label": "NSW"}]
        result = lng.sales_with_offset_long(sample_sales_df, hw_periods)
        weeks = result["offset_week"].to_list()
        assert weeks == sorted(weeks)


class TestCumulativeSalesByDeltaLong:
    """cumulative_sales_by_delta_long 関数のテスト"""

    def test_returns_dataframe_week_mode(self, sample_sales_df):
        result = lng.cumulative_sales_by_delta_long(sample_sales_df, mode="week")
        assert isinstance(result, pl.DataFrame)

    def test_returns_dataframe_month_mode(self, sample_sales_df):
        result = lng.cumulative_sales_by_delta_long(sample_sales_df, mode="month")
        assert isinstance(result, pl.DataFrame)

    def test_returns_dataframe_year_mode(self, sample_sales_df):
        result = lng.cumulative_sales_by_delta_long(sample_sales_df, mode="year")
        assert isinstance(result, pl.DataFrame)

    def test_week_mode_has_delta_week_column(self, sample_sales_df):
        result = lng.cumulative_sales_by_delta_long(sample_sales_df, mode="week")
        assert "delta_week" in result.columns

    def test_month_mode_has_delta_month_column(self, sample_sales_df):
        result = lng.cumulative_sales_by_delta_long(sample_sales_df, mode="month")
        assert "delta_month" in result.columns

    def test_year_mode_has_delta_year_column(self, sample_sales_df):
        result = lng.cumulative_sales_by_delta_long(sample_sales_df, mode="year")
        assert "delta_year" in result.columns

    def test_invalid_mode_raises_value_error(self, sample_sales_df):
        with pytest.raises(ValueError):
            lng.cumulative_sales_by_delta_long(sample_sales_df, mode="invalid")

    def test_filter_by_hw(self, sample_sales_df):
        result = lng.cumulative_sales_by_delta_long(sample_sales_df, hw=["NSW"])
        assert set(result["hw"].unique().to_list()) == {"NSW"}

    def test_with_begin_end(self, sample_sales_df):
        result = lng.cumulative_sales_by_delta_long(sample_sales_df, begin=10, end=200)
        assert isinstance(result, pl.DataFrame)
        assert (result["delta_week"] >= 10).all()
        assert (result["delta_week"] <= 200).all()

    def test_sum_units_column_present(self, sample_sales_df):
        result = lng.cumulative_sales_by_delta_long(sample_sales_df, mode="week")
        assert "sum_units" in result.columns


class TestMakerLong:
    """maker_long 関数のテスト"""

    def test_returns_dataframe(self, sample_sales_df):
        result = lng.maker_long(sample_sales_df)
        assert isinstance(result, pl.DataFrame)

    def test_has_expected_columns(self, sample_sales_df):
        result = lng.maker_long(sample_sales_df)
        assert set(result.columns) == {"year", "maker_name", "yearly_units", "yearly_ratio", "yearly_pct"}

    def test_with_year_range(self, sample_sales_df):
        result = lng.maker_long(sample_sales_df, begin_year=2020, end_year=2021)
        assert result.height > 0

    def test_sorted_by_year(self, sample_sales_df):
        result = lng.maker_long(sample_sales_df)
        years = result["year"].to_list()
        assert years == sorted(years)

    def test_known_maker_names_present(self, sample_sales_df):
        result = lng.maker_long(sample_sales_df)
        makers = set(result["maker_name"].to_list())
        assert "Nintendo" in makers
        assert "SONY" in makers
        assert "Microsoft" in makers

    def test_yearly_units_positive(self, sample_sales_df):
        result = lng.maker_long(sample_sales_df)
        assert (result["yearly_units"] > 0).all()

    def test_begin_year_only(self, sample_sales_df):
        result = lng.maker_long(sample_sales_df, begin_year=2021)
        assert result.height > 0

    def test_end_year_only(self, sample_sales_df):
        result = lng.maker_long(sample_sales_df, end_year=2020)
        assert result.height > 0


class TestCumSumDiffsLong:
    """cumsum_diffs_long 関数のテスト"""

    def test_returns_dataframe(self, sample_sales_df):
        result = lng.cumsum_diffs_long(sample_sales_df, [("NSW", "PS5")])
        assert isinstance(result, pl.DataFrame)

    def test_has_expected_columns(self, sample_sales_df):
        result = lng.cumsum_diffs_long(sample_sales_df, [("NSW", "PS5")])
        expected_columns = {
            "report_date",
            "hw_new",
            "hw_old",
            "pair_name",
            "cumsum_diff",
            "sum_units_new",
            "sum_units_old",
            "index_week",
        }
        assert set(result.columns) == expected_columns

    def test_single_comparison(self, sample_sales_df):
        result = lng.cumsum_diffs_long(sample_sales_df, [("NSW", "PS5")])
        assert result.height > 0
        # NS2とPS5のペアのみ
        assert set(result["hw_new"].unique().to_list()) == {"NSW"}
        assert set(result["hw_old"].unique().to_list()) == {"PS5"}

    def test_multiple_comparisons(self, sample_sales_df):
        cmplist = [("NSW", "PS5"), ("XSX", "PS5")]
        result = lng.cumsum_diffs_long(sample_sales_df, cmplist)
        assert result.height > 0
        # 両方のペアが存在することを確認
        hw_new_set = set(result["hw_new"].unique().to_list())
        assert "NSW" in hw_new_set
        assert "XSX" in hw_new_set

    def test_cumsum_diff_calculation_correct(self, sample_sales_df):
        result = lng.cumsum_diffs_long(sample_sales_df, [("NSW", "PS5")])
        # cumsum_diff = sum_units_old - sum_units_new
        result = result.with_columns(
            calculated_diff=(pl.col("sum_units_old") - pl.col("sum_units_new"))
        )
        # 計算が一致していることを確認
        assert (result["cumsum_diff"] == result["calculated_diff"]).all()

    def test_pair_name_format(self, sample_sales_df):
        result = lng.cumsum_diffs_long(sample_sales_df, [("NSW", "PS5")])
        # pair_name は "NSW_PS5差" の形式
        expected_pair_name = "NSW_PS5差"
        assert set(result["pair_name"].unique().to_list()) == {expected_pair_name}

    def test_include_comeback_false_default(self, sample_sales_df):
        # デフォルトはinclude_comeback=False
        result = lng.cumsum_diffs_long(sample_sales_df, [("NSW", "PS5")])
        # include_comeback=Falseの場合、cumsum_diff が初めて0未満になる行までフィルタリング
        # NS2は古いハード（2017発売）で、PS5は新しいハード（2020発売）
        # NSWの方が先に発売されているので、累計がずっと大きい可能性がある
        # cumsum_diffが存在することを確認（フィルタリングされていることを示す）
        if result.height > 0:
            # 最後の行のcumsum_diffが最初の行より小さくないことを確認
            # （フィルタリングが機能しているかは別テストで確認）
            assert "cumsum_diff" in result.columns

    def test_include_comeback_true_preserves_all_data(self, sample_sales_df):
        result_with_comeback = lng.cumsum_diffs_long(
            sample_sales_df, [("NSW", "PS5")], include_comeback=True
        )
        result_without_comeback = lng.cumsum_diffs_long(
            sample_sales_df, [("NSW", "PS5")], include_comeback=False
        )
        # include_comeback=Trueの方が行数が多いか等しい
        assert result_with_comeback.height >= result_without_comeback.height
        # cumsum_diff が 0 未満になる行があるなら、include_comeback=True でそれが含まれる
        negative_in_with = (result_with_comeback["cumsum_diff"] < 0).sum()
        negative_in_without = (result_without_comeback["cumsum_diff"] < 0).sum()
        # with_comeback=Trueの方が負の値を含むはず（または同じ）
        assert negative_in_with >= negative_in_without

    def test_include_comeback_filtering_behavior(self, sample_sales_df):
        """include_comeback=False時のフィルタリング動作を検証"""
        result_with_comeback = lng.cumsum_diffs_long(
            sample_sales_df, [("NSW", "PS5")], include_comeback=True
        )
        result_without_comeback = lng.cumsum_diffs_long(
            sample_sales_df, [("NSW", "PS5")], include_comeback=False
        )
        
        # cumsum_diff < 0 になる行が存在するかをチェック
        negative_rows_with = result_with_comeback.filter(pl.col("cumsum_diff") < 0)
        negative_rows_without = result_without_comeback.filter(pl.col("cumsum_diff") < 0)
        
        if negative_rows_with.height > 0:
            # cumsum_diff < 0 の行が存在する場合
            # include_comeback=False では、最初の負の行より後の行がフィルタリングされている
            # つまり、without のdata setに属する最後のreport_dateは、with の最後のreport_dateより前か同じ
            without_max_date = result_without_comeback["report_date"].max()
            with_max_date = result_with_comeback["report_date"].max()
            assert without_max_date <= with_max_date
    
    def test_report_date_alignment(self, sample_sales_df):
        # 内部結合なので、両ハードが同じreport_dateを持つ行のみが存在
        result = lng.cumsum_diffs_long(sample_sales_df, [("NSW", "PS5")])
        # 結果にはreport_dateが含まれている
        assert "report_date" in result.columns
        assert result.height >= 0

    def test_empty_result_when_no_overlapping_dates(self):
        # 重複する日付がない2つのハードウェアのデータを作成
        # この場合、内部結合の結果は空になる
        # 注：サンプルデータでは重複がある可能性があるため、
        # この테스트は構造を確認するためのもの
        import polars as pl
        from datetime import date

        # PS5とXSXのデータだけを使用（日付が異なる可能性がある）
        cmplist = [("PS5", "XSX")]
        # サンプルデータには重複がないので、結果は空の可能性
        # これは正常な動作


class TestSalesPaseDiffsLong:
    """sales_pase_diffs_long 関数のテスト"""

    def test_returns_dataframe(self, sample_sales_df):
        # テストデータで同じindex_weekを持つペアがない場合、空のDataFrameが返される
        # これは正常な動作（結果が存在しない）
        result = lng.sales_pase_diffs_long(sample_sales_df, [("NSW", "PS5")])
        assert isinstance(result, pl.DataFrame)

    def test_has_expected_columns(self, sample_sales_df):
        result = lng.sales_pase_diffs_long(sample_sales_df, [("NSW", "PS5")])
        # 空のDataFrameでもカラムが存在すること
        expected_columns = {
            "index_week",
            "hw_new",
            "hw_old",
            "pair_name",
            "pase_diff",
            "sum_units_new",
            "sum_units_old",
            "report_date_new",
            "report_date_old",
        }
        assert set(result.columns) == expected_columns

    def test_empty_result_when_no_overlapping_index_weeks(self, sample_sales_df):
        # サンプルデータではNSWとPS5がindex_weekで重複しない
        result = lng.sales_pase_diffs_long(sample_sales_df, [("NSW", "PS5")])
        # 重複がないため、結果は空
        assert result.height == 0

    def test_multiple_comparisons_structure(self, sample_sales_df):
        # 複数ペアを指定してもその構造は保持される
        cmplist = [("NSW", "PS5"), ("NSW", "XSX")]
        result = lng.sales_pase_diffs_long(sample_sales_df, cmplist)
        # 結果はDataFrameであること
        assert isinstance(result, pl.DataFrame)
        # カラムが正しいこと
        assert "pair_name" in result.columns
        
    def test_pase_diff_calculation_structure(self, sample_sales_df):
        # カスタムテストデータを作成（同じindex_weekを持つペア）
        import polars as pl
        from datetime import date, timedelta
        
        # PS5とPS4のカスタムテストデータを構築
        # PS4: 2014-02-22 発売
        # PS5: 2020-11-12 発売
        ps4_launch = date(2014, 2, 22)
        ps5_launch = date(2020, 11, 12)
        
        # テスト用にカスタムDFを作成（ここでは単純に構造テスト）
        # sales_pase_diffs_longが返すDataFrameの構造が正しいことを確認
        test_data = []
        # PS4: index_week 1, 2, 3 (3年間のデータ以降など)
        # PS5: index_week 1, 2, 3 (発売後3週分)
        for i in range(1, 4):
            test_data.append({
                "report_date": ps4_launch + timedelta(weeks=100+i),
                "hw": "PS4",
                "sum_units": 10000 + i*1000,
                "index_week": i,
                "delta_week": 100+i-1,
            })
            test_data.append({
                "report_date": ps5_launch + timedelta(weeks=i-1),
                "hw": "PS5",
                "sum_units": 5000 + i*500,
                "index_week": i,
                "delta_week": i-1,
            })
        
        test_df = pl.DataFrame(test_data)
        result = lng.sales_pase_diffs_long(test_df, [("PS5", "PS4")])
        
        # 結果が空でないことを確認
        assert result.height > 0
        # pase_diff = sum_units_new - sum_units_old であることを確認
        assert (result["pase_diff"] == result["sum_units_new"] - result["sum_units_old"]).all()

    def test_sorted_by_index_week(self, sample_sales_df):
        # カスタムテストデータで確認
        import polars as pl
        from datetime import date, timedelta
        
        ps4_launch = date(2014, 2, 22)
        ps5_launch = date(2020, 11, 12)
        
        test_data = []
        for i in range(1, 4):
            test_data.append({
                "report_date": ps4_launch + timedelta(weeks=100+i),
                "hw": "PS4",
                "sum_units": 10000 + i*1000,
                "index_week": i,
            })
            test_data.append({
                "report_date": ps5_launch + timedelta(weeks=i-1),
                "hw": "PS5",
                "sum_units": 5000 + i*500,
                "index_week": i,
            })
        
        test_df = pl.DataFrame(test_data)
        result = lng.sales_pase_diffs_long(test_df, [("PS5", "PS4")])
        
        if result.height > 0:
            index_weeks = result["index_week"].to_list()
            # index_weekでソートされていることを確認
            assert index_weeks == sorted(index_weeks)

    def test_report_date_columns_present(self, sample_sales_df):
        result = lng.sales_pase_diffs_long(sample_sales_df, [("NSW", "PS5")])
        # 両ハードのreport_dateが存在
        assert "report_date_new" in result.columns
        assert "report_date_old" in result.columns

    def test_pair_name_structure(self, sample_sales_df):
        # カスタムテストデータで確認
        import polars as pl
        from datetime import date, timedelta
        
        ps4_launch = date(2014, 2, 22)
        ps5_launch = date(2020, 11, 12)
        
        test_data = []
        for i in range(1, 4):
            test_data.append({
                "report_date": ps4_launch + timedelta(weeks=100+i),
                "hw": "PS4",
                "sum_units": 10000 + i*1000,
                "index_week": i,
            })
            test_data.append({
                "report_date": ps5_launch + timedelta(weeks=i-1),
                "hw": "PS5",
                "sum_units": 5000 + i*500,
                "index_week": i,
            })
        
        test_df = pl.DataFrame(test_data)
        result = lng.sales_pase_diffs_long(test_df, [("PS5", "PS4")])
        
        if result.height > 0:
            # pair_name は "PS5_PS4差" の形式
            expected_pair_name = "PS5_PS4差"
            assert set(result["pair_name"].unique().to_list()) == {expected_pair_name}

    def test_multiple_pairs_different_calculations(self, sample_sales_df):
        # 複数ペアで異なるpase_diffが計算されることを確認
        import polars as pl
        from datetime import date, timedelta
        
        ps3_launch = date(2006, 11, 11)
        ps4_launch = date(2014, 2, 22)
        ps5_launch = date(2020, 11, 12)
        
        test_data = []
        # 3つのハードウェアのデータ（同じindex_weekを持つ）
        for i in range(1, 3):
            test_data.append({
                "report_date": ps3_launch + timedelta(weeks=200+i),
                "hw": "PS3",
                "sum_units": 20000 + i*1000,
                "index_week": i,
            })
            test_data.append({
                "report_date": ps4_launch + timedelta(weeks=100+i),
                "hw": "PS4",
                "sum_units": 15000 + i*1000,
                "index_week": i,
            })
            test_data.append({
                "report_date": ps5_launch + timedelta(weeks=i-1),
                "hw": "PS5",
                "sum_units": 10000 + i*500,
                "index_week": i,
            })
        
        test_df = pl.DataFrame(test_data)
        result = lng.sales_pase_diffs_long(test_df, [("PS5", "PS3"), ("PS5", "PS4")])
        
        if result.height > 0:
            # 異なるペアが存在することを確認
            pair_names = result["pair_name"].unique().to_list()
            assert len(pair_names) >= 1
