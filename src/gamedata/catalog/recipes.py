from .models import record

RECIPES = {
    "compare_launch_cumulative": record(
        "recipe:compare_launch_cumulative",
        "発売からの累計を比較。普及速度を同じ経過週で比べる",
        code="g.cumulative_sales_by_delta_long(hard_sales_all_df.sort('report_date'), mode='week', hw=['NS2', 'PS5'])",
        semantics=[
            "実際の収録機種と期間はinspect_frameで先に確認",
            "同じ暦日での累計比較とは異なる",
        ],
        related=["function:cumulative_sales_by_delta_long"],
    ),
    "monthly_sales": record(
        "recipe:monthly_sales",
        "月ごとの販売台数を比較する",
        code="g.monthly_sales_long(hard_sales_all_df, hw=['NS2', 'PS5'])",
        semantics=["report_dateの所属月で集計。最新月は途中の可能性がある"],
        related=["function:monthly_sales_long"],
    ),
    "extract_sales": record(
        "recipe:extract_sales",
        "機種と日付範囲を指定して販売データを抽出する",
        code="g.sales_long(hard_sales_all_df, hw=['PS5'], begin=date(2026, 1, 1), end=date(2026, 12, 31))",
        semantics=["gはimport gamedata as g、dateはfrom datetime import dateで用意"],
        related=["function:sales_long"],
    ),
}
