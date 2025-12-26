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
    get_hw_names,
    extract_week_reached_units,
    extract_by_date,
    extract_latest,
    weekly_sales,
    monthly_sales,
    yearly_sales,
    yearly_maker_sales,
    delta_yearly_sales,
    pivot_sales,
    pivot_cumulative_sales,
    pivot_sales_by_delta,    
    current_report_date,
    cumsum_diffs,
)

from .plot_hard import (
    get_figsize,
    set_figsize,
    plot_cumulative_sales_by_delta,
    plot_sales_by_delta,
    plot_cumulative_sales,
    plot_monthly_bar_by_year,
    plot_yearly_bar_by_hard,
    plot_yearly_bar_by_month,
    plot_delta_yearly_bar,
    plot_maker_share_pie,
    plot_cumsum_diffs,
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
)

from .chart_hard import (
    rename_columns,
    rename_index,
    rename_index_title,
    chart_units_by_date_hw,
    chart_weekly_ranking,
    chart_monthly_ranking,
    chart_yearly_ranking,
    chart_delta_week
)

from .util import (
    # Utility functions can be added here
    report_begin,
    years_ago,
    weeks_before
)


# Make commonly used functions available at package level
__all__ = [
    'load_hard_sales',
    'get_hw_names',
    'extract_week_reached_units',
    'extract_by_date',
    'extract_latest',
    'weekly_sales',
    'monthly_sales',
    'yearly_sales',
    'yearly_maker_sales',
    'delta_yearly_sales',
    'pivot_sales',
    'pivot_cumulative_sales',
    'pivot_sales_by_delta',
    'cumsum_diffs',
    'plot_cumulative_sales_by_delta',
    'plot_sales_by_delta',
    'plot_cumulative_sales',
    'plot_monthly_bar_by_year',
    'plot_yearly_bar_by_hard',
    'plot_yearly_bar_by_month',
    'plot_delta_yearly_bar',
    'plot_cumsum_diffs',
    'load_hard_info',
    'get_hard_colors',
    'get_hard_color',
    'get_maker_colors',
    'get_hard_names',
    'get_hard_dict',
    'current_report_date',
    'get_figsize',
    'plot_maker_share_pie',
    'set_figsize',
    'load_hard_event',
    'mask_event',
    'delta_event',
    'filter_event',
    'add_event_positions',
    'add_event_positions_delta',
    'rename_columns',
    'rename_index',
    'rename_index_title',
    'chart_units_by_date_hw',
    'chart_weekly_ranking',
    'chart_monthly_ranking',
    'chart_yearly_ranking',
    'chart_delta_week',
    'report_begin',
    'years_ago',
    'weeks_before',
]

