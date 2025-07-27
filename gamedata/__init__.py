"""
Gamedata analysis library

This package provides utilities for analyzing game hardware sales data.
"""

# Version information
__version__ = "1.0.0"
__author__ = "Hidenari Miwa"

# Import main functions from modules
from .hard_sales import (
    load_hard_sales,
    get_hw_names,
    extract_week_reached_units,
    extract_by_date,
    extract_latest,
    extract_by_hw,
    extract_by_maker,
    extract_by_year,
    aggregate_monthly_sales,
    pivot_cumulative_sales_by_hw,
    pivot_cumulative_sales_by_delta_week,
    pivot_monthly_cumulative_sales_by_hw,
)

# Make commonly used functions available at package level
__all__ = [
    'load_hard_sales',
    'pivot_cumulative_sales_by_hw', 
    'pivot_cumulative_sales_by_delta_week',
    'pivot_monthly_cumulative_sales_by_hw',
    'get_hw_names',
    'extract_week_reached_units',
    'extract_by_date',
    'extract_latest',
    'extract_by_hw',
    'extract_by_maker',
    'extract_by_year',
    'aggregate_monthly_sales', 
]

