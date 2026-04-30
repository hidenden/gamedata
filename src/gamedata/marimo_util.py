## Marimo utility functions
## Marimoノートブック向けのUIウィジェットユーティリティクラス群

import marimo as mo
import polars as pl
from datetime import datetime, timedelta, date
from typing import List
from . import hard_sales as hs
from . import hard_event as he


class HwSelect:
    """ゲームハードウェアをチェックボックスで選択するUIウィジェット。

    Args:
        default_list: 初期状態でチェックを入れるhw識別子のリスト。
                      Noneの場合は全ハードをデフォルト選択とする。
        force_any: Trueの場合、何も選択されていないときに全ハードを返す。
        hw_list: 表示するhw識別子のリスト。Noneの場合はget_hw_all()で取得する。
    """

    def __init__(self, default_list: List[str] | None = None, force_any: bool = False, hw_list: List[str] | None = None):
        # 表示対象のhwリストを決定（未指定なら全ハードを取得）
        self.hw_list = hw_list if hw_list is not None else hs.get_hw_all()

        # default_listが未指定の場合は全ハードを選択状態にする
        if default_list is None:
            default_list = self.hw_list

        # hwリストをチェックボックスの配列として生成し、default_listに含まれるものを初期チェック
        self.checklist = mo.ui.array(
            [mo.ui.checkbox(label=hw, value=(hw in default_list)) for hw in self.hw_list],
        )
        self.widget = self.checklist
        # 未選択時に全ハードを返すかどうかのフラグ
        self.force_any = force_any

    def _display_(self):
        """Marimoセル上での表示レイアウト。要素数が多い場合は2行に分けて表示する。"""
        if len(self.checklist) > 11:
            # 11件を超える場合は2行に分割して表示
            return mo.vstack(
                [mo.hstack(self.checklist[:11], justify="start"),   # 前半11件
                 mo.hstack(self.checklist[11:], justify="start")    # 後半残り
                ]
            )
        # 11件以下の場合は1行で表示
        return mo.hstack(self.checklist, justify="start")

    @property
    def value(self) -> List[str]:
        """チェック済みのhw識別子リストを返す。

        Returns:
            チェックされているhwの識別子リスト。
            force_any=Trueかつ何も選択されていない場合は全ハードを返す。
        """
        hw_data = [hw for hw, flg in zip(self.hw_list, self.widget.value) if flg]
        # 何も選択されていない場合にforce_anyが有効なら全ハードを返す
        if self.force_any and len(hw_data) == 0:
            return self.hw_list
        return hw_data


class EventSelect:
    """イベントマスクの適用範囲をドロップダウンで選択するUIウィジェット。

    Args:
        default_value: 初期選択値。"short" / "middle" / "long" のいずれか。
                       デフォルトは "middle"。
    """

    def __init__(self, default_value: str = "middle"):
        self.options = ["short", "middle", "long"]
        # ドロップダウンUIを生成
        self.dropdown = mo.ui.dropdown(options=self.options, value=default_value, label="イベントマスク")
        self.widget = self.dropdown
        # 選択肢文字列と実際のイベントマスク定数を対応付ける辞書
        self.event_dict = {
            "short": he.EVENT_MASK_SHORT,
            "middle": he.EVENT_MASK_MIDDLE,
            "long": he.EVENT_MASK_LONG,
        }

    def _display_(self):
        """Marimoセル上での表示レイアウト。"""
        return self.widget

    @property
    def value(self) -> he.EventMasks:
        """選択中のイベントマスク定数を返す。

        Returns:
            選択された範囲に対応するEventMasks定数。
        """
        return self.event_dict[self.widget.value]


class MakerSelect:
    """ゲームメーカーをチェックボックスで選択するUIウィジェット。

    Args:
        default_list: 初期状態でチェックを入れるメーカー名のリスト。
                      Noneの場合は全メーカーをデフォルト選択とする。
        force_any: Trueの場合、何も選択されていないときに全メーカーを返す。
        maker_list: 表示するメーカー名のリスト。Noneの場合はget_maker_all()で取得する。
    """

    def __init__(self, default_list: List[str] | None = None, force_any: bool = False, maker_list: List[str] | None = None):
        # 表示対象のメーカーリストを決定（未指定なら全メーカーを取得）
        self.maker_list = maker_list if maker_list is not None else hs.get_maker_all()

        # default_listが未指定の場合は全メーカーを選択状態にする
        if default_list is None:
            default_list = self.maker_list

        # メーカーリストをチェックボックスの配列として生成し、default_listに含まれるものを初期チェック
        self.checklist = mo.ui.array(
            [mo.ui.checkbox(label=maker, value=(maker in default_list)) for maker in self.maker_list],
        )
        self.widget = self.checklist
        # 未選択時に全メーカーを返すかどうかのフラグ
        self.force_any = force_any

    def _display_(self):
        """Marimoセル上での表示レイアウト。メーカー数は少ないため1行で表示する。"""
        return mo.hstack(self.checklist, justify="start")

    @property
    def value(self) -> List[str]:
        """チェック済みのメーカー名リストを返す。

        Returns:
            チェックされているメーカー名のリスト。
            force_any=Trueかつ何も選択されていない場合は全メーカーを返す。
        """
        maker_data = [maker for maker, flg in zip(self.maker_list, self.widget.value) if flg]
        # 何も選択されていない場合にforce_anyが有効なら全メーカーを返す
        if self.force_any and len(maker_data) == 0:
            return self.maker_list
        return maker_data



