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
    aggregate_monthly_sales,
    pivot_sales,
    pivot_cumulative_sales,
    pivot_sales_by_delta,
)

from .plot_hard import (
    plot_cumulative_sales_by_delta,
    plot_cumulative_sales,
)

# Make commonly used functions available at package level
__all__ = [
    'load_hard_sales',
    'get_hw_names',
    'extract_week_reached_units',
    'extract_by_date',
    'extract_latest',
    'aggregate_monthly_sales',
    'pivot_sales',
    'pivot_cumulative_sales',
    'pivot_sales_by_delta',
    'plot_cumulative_sales_by_delta',
    'plot_cumulative_sales',
]

