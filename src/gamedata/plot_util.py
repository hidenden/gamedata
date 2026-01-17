# 標準ライブラリ
from datetime import datetime, timedelta, date
from typing import List, Optional

# サードパーティライブラリ
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.ticker import ScalarFormatter, MultipleLocator
import matplotlib.dates as mdates
import mplcursors


_FigSize = (10, 5)

class AxisLabels:
    def __init__(self, title=None, xlabel=None, ylabel=None, legend=None):
        self.title = title
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.legend = legend

class TickParams:
    def __init__(self, axis='x', which='major', labelsize=10, rotation=None):
        self.axis = axis
        self.which = which
        self.labelsize = labelsize
        self.rotation = rotation

def get_figsize() -> tuple[int, int]:
    return _FigSize

def set_figsize(width: int, height: int) -> None:
    global _FigSize
    _FigSize = (width, height)


