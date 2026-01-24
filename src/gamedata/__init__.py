"""
Gamedata analysis library

This package provides utilities for analyzing game hardware sales data.
"""

# Version information
__version__ = "0.1.0"
__author__ = "Hidenari Miwa"

# Import main functions from modules
from .hard_sales import (
    load_hard_sales,
    get_hw,
    get_active_hw,
    current_report_date,
)

from .hard_sales_extract import (
    extract_week_reached_units,
    extract_by_date,
    extract_latest,
)

from .hard_sales_filter import (
    weekly_sales,
    monthly_sales,
    quarterly_sales,
    yearly_sales,
    yearly_maker_sales,
    delta_yearly_sales,
)

from .hard_sales_pivot import (
    pivot_sales,
    pivot_monthly_sales,
    pivot_quarterly_sales,
    pivot_yearly_sales,
    pivot_cumulative_sales,
    pivot_sales_by_delta,    
    pivot_cumulative_sales_by_delta,
    pivot_maker,
    cumsum_diffs,    
)

from .plot_util import (
    AxisLabels,
    TickParams,
    get_figsize,
    set_figsize,
    get_transparent_mode,
    set_transparent_mode,
    set_dispfunc,
    get_dispfunc,
)

from .plot_line import (
    plot_cumulative_sales_by_delta,
    plot_sales,
    plot_sales_by_delta,
    plot_cumulative_sales,
    plot_cumsum_diffs,
    plot_sales_pase_diff,
)

from .plot_bar import (
    plot_monthly_bar_by_year,
    plot_quarterly_bar_by_year,
    plot_monthly_bar_by_hard,
    plot_quarterly_bar_by_hard,
    plot_monthly_bar_by_hard_year,
    plot_quarterly_bar_by_hard_year,
    plot_yearly_bar_by_hard,    
    plot_yearly_bar_by_month,
    plot_delta_yearly_bar,
    plot_maker_share_bar,
)

from .plot_pie import (
    plot_maker_share_pie,
)

from .hard_info import (
    load_hard_info,
    get_hard_colors,
    get_hard_color,
    get_maker_colors,
    get_hard_names,
    get_hard_dict,
)

from .hard_event import (
    load_hard_event,
    mask_event,
    delta_event,
    filter_event,
    add_event_positions,
    add_event_positions_delta,
    EventMasks,
    EVENT_MASK_LONG,
    EVENT_MASK_MIDDLE,
    EVENT_MASK_SHORT,
)

from .chart_hard import (
    rename_columns,
    rename_index,
    rename_index_title,
    chart_units_by_date_hw,
    chart_weekly_ranking,
    chart_monthly_ranking,
    chart_yearly_ranking,
    chart_delta_week_ranking,
    style_sales,
)

from .util import (
    # Utility functions can be added here
    report_begin,
    years_ago,
    weeks_before
)


# Make commonly used functions available at package level
__all__ = []

