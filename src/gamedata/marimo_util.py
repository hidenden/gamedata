## Marimo utility functions

import marimo as mo
import polars as pl
from datetime import datetime, timedelta, date
from typing import List
from . import hard_sales as hs
from . import hard_event as he

class HwSelect:
    def __init__(self, default_list: List[str] | None = None):
        if default_list is None:
            default_list = []
        self.hw_list = hs.get_hw_all()
        self.checklist = mo.ui.array(
            [mo.ui.checkbox(label=hw, value=(hw in default_list)) for hw in self.hw_list],
        )
        self.widget = self.checklist
        
    def _display_(self):
        return mo.vstack(
            [mo.hstack(self.checklist[:13], justify="start"),
             mo.hstack(self.checklist[13:], justify="start")
            ]
        )

    @property
    def value(self) -> List[str]:
        return [hw for hw, flg in zip(self.hw_list, self.widget.value) if flg]


class EventSelect:
    def __init__(self, default_value: str = "middle"):
        self.options = ["short", "middle", "long"]
        self.dropdown = mo.ui.dropdown(options=self.options, value=default_value, label="イベントマスク")
        self.widget = self.dropdown
        self.event_dict = {
            "short": he.EVENT_MASK_SHORT,
            "middle": he.EVENT_MASK_MIDDLE,
            "long": he.EVENT_MASK_LONG,
        }
        
    def _display_(self):
        return self.widget

    @property
    def value(self) -> he.EventMasks:
        return self.event_dict[self.widget.value]

