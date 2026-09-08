"""暦年末のゲームハード販売台数を予測する関数群。"""

from __future__ import annotations

from collections.abc import Sequence
from datetime import date

import polars as pl


_CONTEXT_COLUMNS = {
    "report_date",
    "year",
    "hw",
    "maker_name",
    "units",
}
_FORECAST_COLUMNS = [
    "model",
    "as_of",
    "hw",
    "maker_name",
    "actual_ytd_units",
    "forecast_remaining_units",
    "forecast_year_units",
]


def _validate_sales_frame(sales_df: pl.DataFrame, required: set[str]) -> None:
    if not isinstance(sales_df, pl.DataFrame):
        raise TypeError("sales_df must be a polars.DataFrame")
    missing = sorted(required - set(sales_df.columns))
    if missing:
        raise ValueError(f"sales_dfに必要な列がありません: {', '.join(missing)}")
    if sales_df.is_empty():
        raise ValueError("sales_dfに販売実績がありません")


def _positive_int(value: int, name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(f"{name}は1以上の整数を指定してください")


def _forecast_context(
    sales_df: pl.DataFrame,
    as_of: date | None = None,
    hw: Sequence[str] | None = None,
    *,
    required: set[str] | None = None,
) -> tuple[date, int, pl.DataFrame, pl.DataFrame]:
    """予測の基準日と対象年の実績を準備する内部ヘルパー。"""
    _validate_sales_frame(sales_df, _CONTEXT_COLUMNS | (required or set()))
    max_date = sales_df.select(pl.col("report_date").max()).item()
    if not isinstance(max_date, date):
        raise ValueError("report_dateは日付型である必要があります")
    if as_of is not None and not isinstance(as_of, date):
        raise TypeError("as_ofはdatetime.dateまたはNoneを指定してください")
    resolved_as_of = max_date if as_of is None else min(as_of, max_date)
    year = resolved_as_of.year
    current = sales_df.filter(
        (pl.col("report_date") <= resolved_as_of) & (pl.col("year") == year)
    )
    if hw is not None:
        current = current.filter(pl.col("hw").is_in(list(hw)))
    if current.is_empty():
        raise ValueError(f"{year}年の販売実績がありません")
    actual = current.group_by(["hw", "maker_name"]).agg(
        pl.col("units").sum().alias("actual_ytd_units")
    )
    return resolved_as_of, year, current, actual


def forecast_year_end_52w(
    sales_df: pl.DataFrame,
    as_of: date | None = None,
    hw: Sequence[str] | None = None,
) -> pl.DataFrame:
    """保存済みの52週移動平均から年末販売台数を予測する。

    入力がすべて7日集計済みであることを前提に、基準日時点の ``ma52w``
    （過去52週の週平均販売台数）が年末まで続くと仮定する。返却値はハード
    ごとの当年実績・残期間予測・年間予測で、``model`` は
    ``trailing_52w`` となる。52週分の履歴がないハードでは予測列がnullに
    なる。
    """
    resolved_as_of, year, _, actual = _forecast_context(
        sales_df, as_of, hw, required={"ma52w"}
    )
    weekly_average = (
        sales_df.filter(
            (pl.col("report_date") <= resolved_as_of)
            & pl.col("hw").is_in(actual.get_column("hw").to_list())
        )
        .sort("report_date")
        .group_by("hw")
        .agg(pl.col("ma52w").last().alias("weekly_run_rate"))
    )
    remaining_days = (date(year, 12, 31) - resolved_as_of).days
    return (
        actual.join(weekly_average, on="hw", how="left")
        .with_columns(
            (pl.col("actual_ytd_units") + pl.col("weekly_run_rate") * remaining_days / 7)
            .round(0)
            .cast(pl.Int64)
            .alias("forecast_year_units"),
            pl.lit("trailing_52w").alias("model"),
            pl.lit(resolved_as_of).alias("as_of"),
        )
        .with_columns(
            (pl.col("forecast_year_units") - pl.col("actual_ytd_units")).alias(
                "forecast_remaining_units"
            )
        )
        .select(_FORECAST_COLUMNS)
        .sort("forecast_year_units", descending=True)
    )


def forecast_year_end_quarter_share(
    sales_df: pl.DataFrame,
    as_of: date | None = None,
    history_years: int = 5,
    hw: Sequence[str] | None = None,
) -> pl.DataFrame:
    """メーカー別の過去年四半期構成比から年末販売台数を予測する。

    完全な過去年についてメーカー別四半期シェアの中央値を使う。メーカーの
    履歴が4四半期分そろわない場合は、全メーカーの四半期シェアへフォール
    バックする。``model`` は ``maker_quarter_share`` となる。
    """
    _positive_int(history_years, "history_years")
    resolved_as_of, year, _, actual = _forecast_context(
        sales_df, as_of, hw, required={"q_num"}
    )
    history = sales_df.filter(
        (pl.col("year") >= year - history_years) & (pl.col("year") < year)
    )
    quarterly = history.group_by(["maker_name", "year", "q_num"]).agg(
        pl.col("units").sum().alias("quarter_units")
    )
    annual = quarterly.group_by(["maker_name", "year"]).agg(
        pl.col("quarter_units").sum().alias("annual_units"),
        pl.col("q_num").n_unique().alias("quarter_count"),
    )
    shares = (
        quarterly.join(annual, on=["maker_name", "year"])
        .filter((pl.col("quarter_count") == 4) & (pl.col("annual_units") > 0))
        .with_columns((pl.col("quarter_units") / pl.col("annual_units")).alias("share"))
        .group_by(["maker_name", "q_num"])
        .agg(pl.col("share").median().alias("quarter_share"))
    )
    global_shares = (
        quarterly.group_by(["year", "q_num"]).agg(pl.col("quarter_units").sum())
        .join(
            quarterly.group_by("year").agg(
                pl.col("quarter_units").sum().alias("annual_units")
            ),
            on="year",
        )
        .with_columns((pl.col("quarter_units") / pl.col("annual_units")).alias("share"))
        .group_by("q_num")
        .agg(pl.col("share").median().alias("quarter_share"))
    )
    quarter = (resolved_as_of.month - 1) // 3 + 1
    quarter_start_month = (quarter - 1) * 3 + 1
    quarter_start = date(year, quarter_start_month, 1)
    quarter_end = date(year, 12, 31) if quarter == 4 else date(year, quarter_start_month + 3, 1)
    quarter_days = (quarter_end - quarter_start).days + (1 if quarter == 4 else 0)
    elapsed_fraction = min(1.0, ((resolved_as_of - quarter_start).days + 1) / quarter_days)
    fallback = {
        int(row["q_num"]): float(row["quarter_share"])
        for row in global_shares.iter_rows(named=True)
    }
    rows = []
    for row in actual.iter_rows(named=True):
        maker_shares = {
            int(item["q_num"]): float(item["quarter_share"])
            for item in shares.filter(pl.col("maker_name") == row["maker_name"]).iter_rows(named=True)
        }
        profile = maker_shares if len(maker_shares) == 4 else fallback
        elapsed_share = sum(profile.get(q, 0.0) for q in range(1, quarter))
        elapsed_share += profile.get(quarter, 0.0) * elapsed_fraction
        estimate = round(row["actual_ytd_units"] / elapsed_share) if elapsed_share > 0 else None
        rows.append(
            {
                "model": "maker_quarter_share",
                "as_of": resolved_as_of,
                "hw": row["hw"],
                "maker_name": row["maker_name"],
                "actual_ytd_units": row["actual_ytd_units"],
                "forecast_remaining_units": None
                if estimate is None
                else max(0, estimate - row["actual_ytd_units"]),
                "forecast_year_units": estimate,
            }
        )
    return pl.DataFrame(rows).select(_FORECAST_COLUMNS).sort("forecast_year_units", descending=True)


def forecast_year_end_yoy_seasonal(
    sales_df: pl.DataFrame,
    as_of: date | None = None,
    scale_bounds: tuple[float, float] = (0.25, 4.0),
    hw: Sequence[str] | None = None,
) -> pl.DataFrame:
    """前年の残期間販売を当年YTD比で補正して年末販売台数を予測する。

    前年の同日までの累計比を ``scale_bounds`` に収め、その倍率で前年残期間の
    販売を補正する。前年実績がないハードの予測値はnullとなる。``model`` は
    ``yoy_seasonal`` となる。
    """
    try:
        lower_bound, upper_bound = scale_bounds
    except (TypeError, ValueError) as exc:
        raise ValueError("scale_boundsは0より大きい昇順の2要素タプルを指定してください") from exc
    if (
        not isinstance(lower_bound, (int, float))
        or not isinstance(upper_bound, (int, float))
        or lower_bound <= 0
        or lower_bound > upper_bound
    ):
        raise ValueError("scale_boundsは0より大きい昇順の2要素タプルを指定してください")
    resolved_as_of, year, _, actual = _forecast_context(sales_df, as_of, hw)
    try:
        prior_cutoff = date(year - 1, resolved_as_of.month, resolved_as_of.day)
    except ValueError:
        prior_cutoff = date(year - 1, 2, 28)
    prior = sales_df.filter(pl.col("year") == year - 1)
    prior_ytd = prior.filter(pl.col("report_date") <= prior_cutoff).group_by("hw").agg(
        pl.col("units").sum().alias("prior_ytd_units")
    )
    prior_remaining = prior.filter(pl.col("report_date") > prior_cutoff).group_by("hw").agg(
        pl.col("units").sum().alias("prior_remaining_units")
    )
    return (
        actual.join(prior_ytd, on="hw", how="left")
        .join(prior_remaining, on="hw", how="left")
        .with_columns(
            (pl.col("actual_ytd_units") / pl.col("prior_ytd_units"))
            .clip(lower_bound, upper_bound)
            .alias("yoy_scale")
        )
        .with_columns(
            (pl.col("prior_remaining_units") * pl.col("yoy_scale"))
            .round(0)
            .cast(pl.Int64)
            .alias("forecast_remaining_units")
        )
        .with_columns(
            (pl.col("actual_ytd_units") + pl.col("forecast_remaining_units")).alias(
                "forecast_year_units"
            ),
            pl.lit("yoy_seasonal").alias("model"),
            pl.lit(resolved_as_of).alias("as_of"),
        )
        .select(_FORECAST_COLUMNS)
        .sort("forecast_year_units", descending=True)
    )


def forecast_year_end_all(
    sales_df: pl.DataFrame,
    as_of: date | None = None,
    hw: Sequence[str] | None = None,
) -> pl.DataFrame:
    """3モデルと中央値アンサンブルで年末販売台数・累計台数を予測する。

    個別モデルと ``median_ensemble`` を縦に連結する。後者は利用可能な年間
    予測の中央値であり、単一モデルの極端な値を抑えるためのものだが、精度を
    保証しない。返却値には基準日時点の累計に残期間予測を加えた
    ``forecast_cumulative_units`` も含む。
    """
    _validate_sales_frame(sales_df, _CONTEXT_COLUMNS | {"ma52w", "q_num", "sum_units"})
    forecasts = pl.concat(
        [
            forecast_year_end_52w(sales_df, as_of, hw=hw),
            forecast_year_end_quarter_share(sales_df, as_of, hw=hw),
            forecast_year_end_yoy_seasonal(sales_df, as_of, hw=hw),
        ],
        how="vertical_relaxed",
    )
    ensemble = (
        forecasts.filter(pl.col("forecast_year_units").is_not_null())
        .group_by(["as_of", "hw", "maker_name", "actual_ytd_units"])
        .agg(
            pl.col("forecast_year_units")
            .median()
            .round(0)
            .cast(pl.Int64)
            .alias("forecast_year_units")
        )
        .with_columns(
            (pl.col("forecast_year_units") - pl.col("actual_ytd_units")).alias(
                "forecast_remaining_units"
            ),
            pl.lit("median_ensemble").alias("model"),
        )
        .select(_FORECAST_COLUMNS)
    )
    combined = pl.concat([forecasts, ensemble], how="vertical_relaxed")
    latest_cumulative = (
        sales_df.filter(pl.col("report_date") <= combined.get_column("as_of")[0])
        .sort("report_date")
        .group_by("hw")
        .agg(pl.col("sum_units").last().alias("actual_cumulative_units"))
    )
    return (
        combined.join(latest_cumulative, on="hw", how="left")
        .with_columns(
            (pl.col("actual_cumulative_units") + pl.col("forecast_remaining_units")).alias(
                "forecast_cumulative_units"
            )
        )
        .drop("actual_cumulative_units")
        .sort(["hw", "model"])
    )
