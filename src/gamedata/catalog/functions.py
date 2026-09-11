"""Explicit function contracts supplemented by live Python signatures."""

import inspect
from importlib import import_module

from .models import record

DATE_RULES = [
    "begin/endはreport_dateに対する両端を含む条件",
    "月途中で抽出するとその月は抽出範囲分だけの集計になる",
]

FUNCTIONS = {
    "load_hard_sales": (
        "hard_sales",
        "販売データをロード（キャッシュあり）",
        None,
        "hard_sales",
        [],
        ["DBを読み込む。no_cache=Trueでキャッシュを破棄して再読込"],
    ),
    "load_hard_info": (
        "hard_info",
        "ハード情報をロード",
        None,
        "hard_info",
        [],
        ["DBを読み込む"],
    ),
    "load_hard_annotation": (
        "hard_annotation",
        "出来事・注釈をロード（キャッシュあり）",
        None,
        "hard_annotation",
        [],
        ["DBを読み込む。no_cache=Trueで再読込"],
    ),
    "date_filter": (
        "hard_sales_filter",
        "集計日で期間抽出",
        "hard_sales",
        "hard_sales",
        ["report_date"],
        DATE_RULES,
    ),
    "sales_long": (
        "hard_sales_long",
        "機種と期間を抽出して日付順に並べる",
        "hard_sales",
        "hard_sales",
        ["report_date", "hw"],
        DATE_RULES + ["hw=[]は全機種。入力の全列を保持"],
    ),
    "weekly_sales": (
        "hard_sales_filter",
        "週次販売台数と期間内累計を集計",
        "hard_sales",
        "weekly_sales",
        ["report_date", "hw", "units"],
        DATE_RULES + ["sum_unitsは抽出後に再計算"],
    ),
    "monthly_sales": (
        "hard_sales_filter",
        "月次販売台数と期間内累計を集計",
        "hard_sales",
        "monthly_sales",
        ["report_date", "year", "month", "hw", "units"],
        DATE_RULES + ["sum_unitsは抽出後に再計算"],
    ),
    "monthly_sales_long": (
        "hard_sales_long",
        "月次販売台数をlong形式で取得",
        "hard_sales",
        "monthly_sales_long",
        ["report_date", "year", "month", "hw", "units"],
        DATE_RULES,
    ),
    "cumulative_sales_by_delta_long": (
        "hard_sales_long",
        "発売からの経過週・月・年を揃えて累計を比較",
        "hard_sales",
        "cumulative_sales_by_delta_long_week",
        ["delta_week", "index_week", "hw", "sum_units"],
        [
            "入力はハードごとにreport_date昇順が必要。グループ内のlastを採用",
            "begin/endは経過期間に対する条件。現実装では0は条件に適用されない",
            "modeはweek/month/year（w/m/yも可）。hw=[]は全機種",
        ],
    ),
    "forecast_year_end_all": (
        "forecast",
        "3つの年末予測モデルと中央値アンサンブルを実行",
        "hard_sales",
        "year_end_forecast",
        ["report_date", "year", "hw", "maker_name", "units", "ma52w", "q_num", "sum_units"],
        [
            "7日集計済みのma52w、メーカー別四半期構成比、前年季節ナイーブを併用",
            "as_ofを省略すると入力の最新report_dateを基準にする",
            "予測精度は保証されない。過去年のバックテストと併用する",
        ],
    ),
    "forecast_52w": (
        "forecast",
        "52週移動平均で任意期間と将来累計の販売台数を予測",
        "hard_sales",
        "forecast_52w",
        ["report_date", "year", "hw", "maker_name", "units", "ma52w", "sum_units"],
        [
            "period_start_dateを省略するとas_of年の1月1日、target_dateを省略すると同年12月31日",
            "target_dateは年をまたいで指定できる。period_start_date <= as_of <= target_dateが必要",
            "forecast_cumulative_unitsはハードごとのsum_unitsを起点にするため、発売日を個別指定する必要がない",
        ],
    ),
}


def describe_function(name, params=None):
    module, summary, input_ds, output_ds, required, semantics = FUNCTIONS[name]
    fn = getattr(import_module(f"gamedata.{module}"), name)
    signature = inspect.signature(fn)
    params = {} if params is None else dict(params)
    unknown = set(params) - set(signature.parameters)
    if unknown:
        raise ValueError(f"Unknown parameters: {sorted(unknown)}")
    required = list(required)
    variants = {}
    if name in ("weekly_sales", "monthly_sales"):
        maker = params.get("maker_mode", False)
        if not isinstance(maker, bool):
            raise ValueError("maker_mode must be bool")
        variants = {
            "maker_mode=False": f"dataset:{name}",
            "maker_mode=True": f"dataset:{name}_maker",
        }
        if maker:
            output_ds += "_maker"
            required[required.index("hw")] = "maker_name"
    if name == "cumulative_sales_by_delta_long":
        from ..mode import parse_mode

        mode = parse_mode(params.get("mode", "week")).value
        if mode not in ("week", "month", "year"):
            raise ValueError("mode must be week, month or year")
        output_ds = f"cumulative_sales_by_delta_long_{mode}"
        required = [f"delta_{mode}", f"index_{mode}", "hw", "sum_units"]
        variants = {
            f"mode={m}": f"dataset:cumulative_sales_by_delta_long_{m}"
            for m in ("week", "month", "year")
        }
    parameters = {}
    for key, p in signature.parameters.items():
        parameters[key] = {
            "annotation": str(p.annotation)
            if p.annotation is not inspect.Parameter.empty
            else None,
            "required": p.default is inspect.Parameter.empty,
        }
        if p.default is not inspect.Parameter.empty:
            parameters[key]["default"] = p.default
    return record(
        f"function:{name}",
        summary,
        signature=f"{name}{signature}",
        parameters=parameters,
        input_dataset=f"dataset:{input_ds}" if input_ds else None,
        output_dataset=f"dataset:{output_ds}",
        output_variants=variants,
        required_columns=required,
        semantics=semantics,
        source=f"src/gamedata/{module}.py",
        related=[f"dataset:{output_ds}"],
        docstring=inspect.getdoc(fn),
    )
