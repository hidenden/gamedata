## Marimo utility functions

import marimo as mo
import polars as pl
from datetime import datetime, timedelta, date
from typing import List
from . import hard_sales as hs
from . import hard_event as he

class HwSelect:
    def __init__(self, default_list: List[str] | None = None, force_any: bool = False):
        self.hw_list = hs.get_hw_all()
        if default_list is None:
            default_list = self.hw_list
        self.checklist = mo.ui.array(
            [mo.ui.checkbox(label=hw, value=(hw in default_list)) for hw in self.hw_list],
        )
        self.widget = self.checklist
        self.force_any = force_any
        
    def _display_(self):
        return mo.vstack(
            [mo.hstack(self.checklist[:11], justify="start"),
             mo.hstack(self.checklist[11:], justify="start")
            ]
        )

    @property
    def value(self) -> List[str]:        
        hw_data = [hw for hw, flg in zip(self.hw_list, self.widget.value) if flg]
        if self.force_any and len(hw_data) == 0:
            return self.hw_list
        return hw_data

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


class MakerSelect:
    def __init__(self, default_list: List[str] | None = None, force_any: bool = False):
        self.maker_list = hs.get_maker_all()
        if default_list is None:
            default_list = self.maker_list
        self.checklist = mo.ui.array(
            [mo.ui.checkbox(label=maker, value=(maker in default_list)) for maker in self.maker_list],
        )
        self.widget = self.checklist
        self.force_any = force_any
        
    def _display_(self):
        return mo.hstack(self.checklist, justify="start")


    @property
    def value(self) -> List[str]:        
        maker_data = [maker for maker, flg in zip(self.maker_list, self.widget.value) if flg]
        if self.force_any and len(maker_data) == 0:
            return self.maker_list
        return maker_data



