"""
Gamedata analysis library

This package provides utilities for analyzing game hardware sales data.
"""

# Version information
__version__ = "0.1.0"
__author__ = "Hidenari Miwa"

from . import chart_config  # テーマ登録の副作用を有効化
from .chart_bar import (
    chart_bar_hwsales_by_year,
    chart_bar_sales,
    chart_hbar_yearly_share_by_maker,
    chart_bar_sales_by_hard_year,
    chart_bar_yearly_delta,
    chart_bar_month_year,
    chart_pie_yearly_share_by_maker,
)
from .chart_line import (
    chart_line_cumulative,
    chart_line_cumulative_delta,
    chart_line_sales,
    chart_line_weekly_by_hw_date,
    chart_line_cumsum_diffs,
    chart_line_pase_diffs,
)
from .chart_rule import (
    chart_line_guide,
    chart_rule_xy,
)
from .hard_event import (
    EVENT_MASK_LONG,
    EVENT_MASK_MIDDLE,
    EVENT_MASK_SHORT,
    EventMasks,
    add_event_positions,
    add_event_positions_delta,
    add_event_positions_delta_long,
    add_event_positions_long,
    delta_event,
    filter_event,
    load_hard_event,
    mask_event,
)
from .hard_info import (
    get_hard_color,
    get_hard_colors,
    get_hard_dict,
    get_hard_names,
    get_hard_order,
    get_maker_colors,
    get_maker_order,
    load_hard_info,
    sort_hard,
    sort_maker,
)

# Import main functions from modules
from .hard_sales import (
    current_report_date,
    get_active_hw,
    get_active_maker,
    get_hw,
    get_hw_all,
    get_maker,
    get_maker_all,
    load_hard_sales,
)
from .hard_sales_extract import (
    extract_by_date,
    extract_latest,
    extract_total,
    extract_week_reached_units,
    hard_sales_summary,
    maker_sales_summary,
    sales_value,
)
from .hard_sales_filter import (
    date_filter,
    delta_yearly_sales,
    monthly_sales,
    quarterly_sales,
    weekly_sales,
    yearly_maker_sales,
    yearly_sales,
)
from .hard_sales_long import (
    cumulative_sales_by_delta_long,
    cumulative_sales_long,
    maker_long,
    monthly_sales_long,
    quarterly_sales_long,
    sales_by_delta_long,
    sales_long,
    sales_with_offset_long,
    yearly_sales_long,
    cumsum_diffs_long,
    sales_pase_diffs_long,
)
from .hard_sales_pivot import (
    cumsum_diffs,
    pivot_cumulative_sales,
    pivot_cumulative_sales_by_delta,
    pivot_maker,
    pivot_monthly_sales,
    pivot_quarterly_sales,
    pivot_sales,
    pivot_sales_by_delta,
    pivot_sales_with_offset,
    pivot_yearly_sales,
)
from .hard_sales_report import (
    delta_week_ranking,
    disable_styler,
    monthly_sales_ranking,
    reached_unit_summary,
    rename_columns,
    rename_hw,
    style_df,
    style_sales,
    units_by_date_hw_table,
    weekly_sales_ranking,
    yearly_sales_ranking,
)
from .marimo_util import (
    EventSelect,
    HwSelect,
    MakerSelect,
)
from .plot_bar import (
    plot_delta_yearly_bar,
    plot_maker_share_bar,
    plot_monthly_bar_by_hard,
    plot_monthly_bar_by_hard_year,
    plot_monthly_bar_by_year,
    plot_quarterly_bar_by_hard,
    plot_quarterly_bar_by_hard_year,
    plot_quarterly_bar_by_year,
    plot_yearly_bar_by_hard,
    plot_yearly_bar_by_month,
)
from .plot_line import (
    plot_cumsum_diffs,
    plot_cumulative_sales,
    plot_cumulative_sales_by_delta,
    plot_sales,
    plot_sales_by_delta,
    plot_sales_pase_diff,
    plot_sales_with_offset,
)
from .plot_pie import (
    plot_maker_share_pie,
)
from .plot_util import (
    AxisLabels,
    TickParams,
    get_dispfunc,
    get_figsize,
    get_transparent_mode,
    set_dispfunc,
    set_figsize,
    set_transparent_mode,
)
from .util import (
    # Utility functions can be added here
    report_begin,
    weeks_before,
    years_ago,
)

# Make commonly used functions available at package level
# __all__ = []
