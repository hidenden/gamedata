"""Curated semantics; column names are scoped to their output dataset."""

from copy import deepcopy

from .models import record


def column(dtype, summary, **fields):
    return {"dtype": dtype, "summary": summary, **fields}


SALES_COLUMNS = {
    "weekly_id": column("String", "週次レコードID"),
    "begin_date": column("Date", "集計開始日（report_date - (period_date - 1)日）"),
    "end_date": column("Date", "集計終了日。report_dateと同じ"),
    "report_date": column("Date", "集計期間の末日。通常日曜日。公表日時ではない"),
    "period_date": column("Int16", "集計日数。通常7日、14日の場合もある", unit="日"),
    "hw": column("String", "ハード識別子。hard_info.idに対応"),
    "units": column(
        "Int64",
        "補正済み販売台数。売上金額ではない",
        unit="台",
        calculation="gamehard_weekly.units + adjust_units",
        aggregation="重複しない機種・期間でsum可能",
        caveats=["adjust_unitsを再加算しない", "欠測は販売ゼロを意味しない"],
    ),
    "adjust_units": column("Int64", "unitsに既に含まれる補正値", unit="台"),
    "year": column("Int16", "report_dateの暦年"),
    "month": column("Int16", "report_dateの月（1〜12）"),
    "mday": column("Int16", "report_dateの日"),
    "week": column("Int16", "(report_dateの日 - 1) // 7 + 1。ISO週番号ではない"),
    "delta_day": column("Int32", "report_dateと発売日の差（日数）", unit="日"),
    "delta_week": column("Int32", "delta_day // 7。0始まりの経過週", unit="週"),
    "delta_month": column("Int16", "発売月との暦月差。0始まり"),
    "delta_year": column("Int16", "report_dateの年 - 発売年。満年数ではない"),
    "avg_units": column(
        "Int64", "補正済みunits // period_date（整数除算）", unit="台/日"
    ),
    "sum_units": column(
        "Int64",
        "DB収録履歴におけるハード別累計販売台数",
        unit="台",
        calculation="ハード別にreport_date昇順で補正済みunitsを累積",
        aggregation="時系列方向にsumしない。対象の最終日を選ぶ",
        caveats=[
            "期間抽出しても起点は変わらない",
            "収録開始前を含む生涯累計かは別途確認",
        ],
    ),
    "launch_date": column("Date", "ハードの発売日"),
    "maker_name": column("String", "メーカー名"),
    "full_name": column("String", "ハードの正式名称"),
    "q_num": column("Int8", "暦年の四半期番号（1〜4）"),
    "fiscal_year": column(
        "Int16",
        "4月始まり・期末年表記の会計年度",
        calculation="1〜3月はyear、4〜12月はyear + 1",
        examples=["2026年4月〜2027年3月は2027"],
    ),
    "fiscal_month": column("Int8", "4月を1とする会計月"),
    "index_week": column("Int32", "delta_week + 1。1始まり"),
    "index_month": column("Int16", "delta_month + 1。1始まり"),
    "index_year": column("Int16", "delta_year + 1。1始まり"),
    "fq_num": column("Int8", "会計年度内の四半期番号（1〜4）"),
    "quarter": column("String", "暦年四半期ラベル。例: 2026Q1"),
    "fiscal_quarter": column("String", "会計四半期ラベル。例: 2027FQ1"),
    "units_diff": column(
        "Int64",
        "同一ハードの前の行からのunits差分",
        null_meaning="最初の行は比較対象がない",
    ),
    "yearly_sum_units": column(
        "Int64",
        "ロード時のハード別・暦年別units累計",
        unit="台",
        aggregation="時系列方向にsumしない",
        caveats=["期間抽出後もロード時の累計値を保持"],
    ),
    "yday": column("Int16", "年内の通算日（1〜366）"),
    "yweek": column("Int16", "strftime('%U') + 1。ISO週番号ではない"),
}
for window in (4, 13, 52):
    SALES_COLUMNS[f"ma{window}w"] = column(
        "Int64",
        f"同一ハードの直近{window}行のunits平均をround(0)して整数化",
        unit="台",
        null_meaning=f"計算に必要な{window}行がない場合など",
        caveats=["欠測・集計日数によって暦上の週数と一致しない"],
    )


def dataset(name, summary, columns, key, **fields):
    return record(
        f"dataset:{name}", summary, columns=deepcopy(columns), key=key, **fields
    )


DATASETS = {
    "hard_sales": dataset(
        "hard_sales",
        "日本国内ゲームハードの期間別販売データと派生指標",
        SALES_COLUMNS,
        ["weekly_id"],
        grain="ハード × 集計期間",
        source="SQLite hard_salesビュー → load_hard_sales()",
        source_code=[
            "src/gamedata/hard_sales.py",
            "database/update_tables.sql",
            "database/update/refresh_analysis.py",
        ],
        semantics=[
            "月・年は集計末日の所属期間。日割り配分しない",
            "14日集計を7日×2へ分割する更新処理がある",
            "flagが出力されないため分割行はこのDataFrameだけでは特定できない",
        ],
        relations=[
            {
                "dataset": "hard_info",
                "left_on": ["hw"],
                "right_on": ["id"],
                "cardinality": "many-to-one",
            },
            {
                "dataset": "hard_annotation",
                "left_on": ["hw", "report_date"],
                "right_on": ["hw", "report_date"],
                "cardinality": "one-to-many",
                "caveat": "複数注釈との結合で販売行が増殖し得る。結合後のsumに注意",
            },
        ],
        related=["function:load_hard_sales"],
    ),
    "hard_info": dataset(
        "hard_info",
        "ハードの識別子・発売日・メーカー・正式名称",
        {
            "id": column("String", "ハード識別子。販売データのhwに対応"),
            **{k: SALES_COLUMNS[k] for k in ("launch_date", "maker_name", "full_name")},
        },
        ["id"],
        grain="ハード",
        source="SQLite gamehard_info → load_hard_info()",
        related=["function:load_hard_info"],
    ),
}
_annotation_columns = {
    "id": column("Int64", "注釈ID"),
    "annotation_date": column("Date", "元テーブルdateを日付変換した注釈日"),
    "note": column("String", "注釈本文。分析上の因果関係を保証しない"),
    "desc": column(
        "String",
        "注釈の補足・背景情報。空欄はNULL。記事作成では対象ハード・期間との関連を確認し、販売変化の因果として断定しない",
        null_meaning="補足情報が未登録",
    ),
    "level": column(
        "Int64",
        "表示優先度。小さいほど長期グラフでも表示する重要な出来事",
        source="guide:annotation_levels",
    ),
    **{
        k: deepcopy(SALES_COLUMNS[k])
        for k in (
            "hw",
            "report_date",
            "launch_date",
            "delta_week",
            "year",
            "month",
            "delta_year",
            "delta_month",
            "q_num",
            "fiscal_year",
            "fiscal_month",
            "index_week",
            "index_month",
            "index_year",
            "fq_num",
        )
    },
}
for _name, _dtype in {
    "year": "Int32",
    "month": "Int8",
    "delta_year": "Int32",
    "delta_month": "Int32",
}.items():
    _annotation_columns[_name]["dtype"] = _dtype
DATASETS["hard_annotation"] = dataset(
    "hard_annotation",
    "ゲームハード関連の出来事・注釈",
    _annotation_columns,
    ["id"],
    grain="注釈。hwとreport_dateの組は一意とは限らない",
    source="SQLite gamehard_annotation → load_hard_annotation()",
    related=[
        "function:load_hard_annotation",
        "dataset:hard_sales",
        "guide:annotation_levels",
    ],
)

# Output contracts are distinct even when a column shares a name with the input.
for _period, _keys in {"weekly": ["report_date"], "monthly": ["year", "month"]}.items():
    for _maker in (False, True):
        _dimension = "maker_name" if _maker else "hw"
        _name = f"{_period}_sales" + ("_maker" if _maker else "")
        DATASETS[_name] = dataset(
            _name,
            f"{_period}集計（{_dimension}別）",
            {
                **{k: SALES_COLUMNS[k] for k in [*_keys, _dimension]},
                f"{_period}_units": column(
                    "Int64", "指定期間内の補正済み販売台数の合計", unit="台"
                ),
                "sum_units": column(
                    "Int64",
                    "日付抽出後に再計算した期間内累計",
                    unit="台",
                    aggregation="時系列方向にsumしない",
                    caveats=["hard_sales.sum_unitsとは起点が異なる"],
                ),
            },
            [*_keys, _dimension],
            grain=f"{_period} × {_dimension}",
        )
DATASETS["monthly_sales_long"] = dataset(
    "monthly_sales_long",
    "ハード別月次販売台数のlong形式",
    {
        "year_month": column("Date", "集計月の末日"),
        "year_month_str": column("String", "YYYY-MM形式の年月"),
        **{
            k: DATASETS["monthly_sales"]["columns"][k]
            for k in ("year", "month", "hw", "monthly_units")
        },
    },
    ["year", "month", "hw"],
    grain="暦月 × ハード",
)
for _period in ("week", "month", "year"):
    _name = f"cumulative_sales_by_delta_long_{_period}"
    DATASETS[_name] = dataset(
        _name,
        f"発売からの経過{_period}別の累計販売台数",
        {
            k: SALES_COLUMNS[k]
            for k in (f"delta_{_period}", f"index_{_period}", "hw", "sum_units")
        },
        [f"delta_{_period}", "hw"],
        grain=f"発売からの経過{_period} × ハード",
        semantics=["グループ内の入力順で最後のsum_unitsを採用。日付昇順の入力が必要"],
    )

DATASETS["forecast_52w"] = dataset(
    "forecast_52w",
    "52週移動平均による任意期間・将来累計販売台数予測",
    {
        "model": column("String", "予測モデル名。trailing_52w"),
        "as_of": column("Date", "実績を観測済みとして扱う予測基準日"),
        "period_start_date": column("Date", "期間累計販売台数の集計開始日"),
        "target_date": column("Date", "予測対象となる期間累計の終了日"),
        **{k: SALES_COLUMNS[k] for k in ("hw", "maker_name")},
        "actual_period_units": column("Int64", "開始日から基準日までの実績販売台数", unit="台"),
        "forecast_remaining_units": column("Int64", "基準日から対象日までの予測販売台数", unit="台"),
        "forecast_period_units": column("Int64", "開始日から対象日までの予測期間累計販売台数", unit="台"),
        "forecast_cumulative_units": column("Int64", "対象日時点のハード別累計販売台数予測", unit="台"),
    },
    ["model", "as_of", "period_start_date", "target_date", "hw"],
    grain="予測基準日 × 期間 × ハード × 予測モデル",
    semantics=[
        "入力は7日集計済みで、ma52wを週平均販売台数として使う",
        "forecast_cumulative_unitsはsum_unitsに残期間予測を加えるため、開始日・発売日に依存しない",
        "期間実績はreport_dateで絞り込み、週次レコードを日割り配分しない",
    ],
)

DATASETS["year_end_forecast"] = dataset(
    "year_end_forecast",
    "暦年末のハード別販売台数予測（複数モデル）",
    {
        "model": column("String", "予測モデル名。中央値アンサンブルを含む"),
        "as_of": column("Date", "予測基準日。入力の最新収録日を超える指定は丸められる"),
        **{k: SALES_COLUMNS[k] for k in ("hw", "maker_name")},
        "actual_ytd_units": column("Int64", "基準日までの当年販売台数", unit="台"),
        "forecast_remaining_units": column("Int64", "基準日後から年末までの予測販売台数", unit="台"),
        "forecast_year_units": column("Int64", "当年の年間予測販売台数", unit="台"),
        "forecast_cumulative_units": column("Int64", "年末時点の予測累計販売台数", unit="台"),
    },
    ["model", "as_of", "hw"],
    grain="予測基準日 × ハード × 予測モデル",
    semantics=[
        "前年実績がないハードではyoy_seasonalの予測列がnullになり得る",
        "median_ensembleはnullでない個別モデルの年間予測の中央値",
        "予測は不確実性を伴い、発売・価格改定・供給制約などを明示的には扱わない",
    ],
)
