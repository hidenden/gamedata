"""
共有テストフィクスチャ
"""
from datetime import date, timedelta
import pytest
import polars as pl


# ---------------------------------------------------------------------------
# ハード販売データのサンプル DataFrame
# ---------------------------------------------------------------------------

def _make_row(
    hw: str,
    report_date: date,
    units: int,
    sum_units: int,
    launch_date: date,
    maker_name: str,
    full_name: str,
    week_idx: int,
    quarter: str,
    delta_year: int,
) -> dict:
    begin_date = report_date - timedelta(days=6)
    delta_d = (report_date - launch_date).days
    delta_w = delta_d // 7
    delta_m = (report_date.year - launch_date.year) * 12 + (report_date.month - launch_date.month)
    return {
        "weekly_id": f"{hw}-{week_idx:04d}",
        "begin_date": begin_date,
        "end_date": report_date,
        "report_date": report_date,
        "quarter": quarter,
        "period_date": 7,
        "hw": hw,
        "units": units,
        "adjust_units": units,
        "year": report_date.year,
        "month": report_date.month,
        "mday": report_date.day,
        "week": 1,
        "delta_day": delta_d,
        "delta_week": delta_w,
        "delta_month": delta_m,
        "delta_year": delta_year,
        "avg_units": units // 7,
        "sum_units": sum_units,
        "launch_date": launch_date,
        "maker_name": maker_name,
        "full_name": full_name,
    }


NSW_LAUNCH = date(2017, 3, 3)
PS5_LAUNCH = date(2020, 11, 12)
XSX_LAUNCH = date(2020, 11, 10)

# Sundays
SUNDAY_2020_01_05 = date(2020, 1, 5)
SUNDAY_2020_01_12 = date(2020, 1, 12)
SUNDAY_2020_04_05 = date(2020, 4, 5)
SUNDAY_2020_11_15 = date(2020, 11, 15)
SUNDAY_2021_01_03 = date(2021, 1, 3)
SUNDAY_2021_04_04 = date(2021, 4, 4)


def _build_sales_rows():
    rows = []
    # NSW データ (6 週分)
    nsw_data = [
        (SUNDAY_2020_01_05, 30000, 30000, "2020Q1", 2),
        (SUNDAY_2020_01_12, 25000, 55000, "2020Q1", 2),
        (SUNDAY_2020_04_05, 20000, 75000, "2020Q2", 3),
        (SUNDAY_2020_11_15, 50000, 125000, "2020Q4", 3),
        (SUNDAY_2021_01_03, 40000, 165000, "2021Q1", 3),
        (SUNDAY_2021_04_04, 15000, 180000, "2021Q2", 4),
    ]
    for i, (rd, units, sum_units, quarter, delta_year) in enumerate(nsw_data):
        rows.append(_make_row(
            "NSW", rd, units, sum_units, NSW_LAUNCH,
            "Nintendo", "Nintendo Switch", i + 1, quarter, delta_year,
        ))

    # PS5 データ (3 週分)
    ps5_data = [
        (SUNDAY_2020_11_15, 20000, 20000, "2020Q4", 0),
        (SUNDAY_2021_01_03, 15000, 35000, "2021Q1", 0),
        (SUNDAY_2021_04_04, 10000, 45000, "2021Q2", 0),
    ]
    for i, (rd, units, sum_units, quarter, delta_year) in enumerate(ps5_data):
        rows.append(_make_row(
            "PS5", rd, units, sum_units, PS5_LAUNCH,
            "SONY", "PlayStation5", i + 1, quarter, delta_year,
        ))

    # XSX データ (2 週分)
    xsx_data = [
        (SUNDAY_2021_01_03, 5000, 5000, "2021Q1", 0),
        (SUNDAY_2021_04_04, 4000, 9000, "2021Q2", 0),
    ]
    for i, (rd, units, sum_units, quarter, delta_year) in enumerate(xsx_data):
        rows.append(_make_row(
            "XSX", rd, units, sum_units, XSX_LAUNCH,
            "Microsoft", "Xbox Series X|S", i + 1, quarter, delta_year,
        ))

    return rows


@pytest.fixture
def sample_sales_df() -> pl.DataFrame:
    """ハード販売データのサンプル DataFrame"""
    rows = _build_sales_rows()
    df = pl.DataFrame(rows)
    df = df.with_columns(
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
    return df.sort("weekly_id")


# ---------------------------------------------------------------------------
# ハードイベントデータのサンプル DataFrame
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_event_df() -> pl.DataFrame:
    """ハードイベントデータのサンプル DataFrame (load_hard_event() の戻り値形式)"""
    rows = [
        {
            "event_date": date(2020, 1, 5),
            "hw": "NSW",
            "event_name": "NSW 新作ソフト発売",
            "event_type": "soft",
            "priority": 1.0,
            "report_date": date(2020, 1, 5),
        },
        {
            "event_date": date(2020, 11, 12),
            "hw": "NSW",
            "event_name": "NSW 本体値下げ",
            "event_type": "price",
            "priority": 2.0,
            "report_date": date(2020, 11, 15),
        },
        {
            "event_date": date(2021, 1, 3),
            "hw": "PS5",
            "event_name": "PS5 新作ソフト発売",
            "event_type": "soft",
            "priority": 1.0,
            "report_date": date(2021, 1, 3),
        },
        {
            "event_date": date(2021, 4, 1),
            "hw": "XSX",
            "event_name": "Xbox セール",
            "event_type": "sale",
            "priority": 3.0,
            "report_date": date(2021, 4, 4),
        },
    ]
    return pl.DataFrame(rows).with_columns(
        pl.col("event_date").cast(pl.Date),
        pl.col("report_date").cast(pl.Date),
    )


@pytest.fixture
def sample_event_df_with_delta(sample_event_df) -> pl.DataFrame:
    """delta_week カラムを持つイベント DataFrame"""
    launch_dict = {
        "NSW": NSW_LAUNCH,
        "PS5": PS5_LAUNCH,
        "XSX": XSX_LAUNCH,
    }
    rows = sample_event_df.to_dicts()
    for row in rows:
        hw = row["hw"]
        rd = row["report_date"]
        launch = launch_dict.get(hw)
        if launch:
            row["delta_week"] = (rd - launch).days // 7
        else:
            row["delta_week"] = 0
    df = pl.DataFrame(rows).with_columns(
        pl.col("event_date").cast(pl.Date),
        pl.col("report_date").cast(pl.Date),
        pl.col("delta_week").cast(pl.Int32),
    )
    return df


# ---------------------------------------------------------------------------
# ハード情報のサンプル DataFrame
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_info_df() -> pl.DataFrame:
    """ハード情報のサンプル DataFrame"""
    rows = [
        {"id": "NSW", "launch_date": NSW_LAUNCH, "maker_name": "Nintendo", "full_name": "Nintendo Switch"},
        {"id": "PS5", "launch_date": PS5_LAUNCH, "maker_name": "SONY", "full_name": "PlayStation5"},
        {"id": "XSX", "launch_date": XSX_LAUNCH, "maker_name": "Microsoft", "full_name": "Xbox Series X|S"},
    ]
    return pl.DataFrame(rows).with_columns(
        pl.col("launch_date").cast(pl.Date),
    )
