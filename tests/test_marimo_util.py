"""
gamedata.marimo_util モジュールのテスト
"""
from unittest.mock import patch, MagicMock, PropertyMock
import polars as pl
import pytest

import gamedata.hard_sales as hs
import gamedata.hard_event as he
from gamedata import marimo_util as mu


def _make_mo_mock():
    """marimo のモックオブジェクトを作成する"""
    mo = MagicMock()
    # チェックボックスの value は bool
    checkbox_mock = MagicMock()
    checkbox_mock.value = True
    mo.ui.checkbox.return_value = checkbox_mock

    # array の value はチェックボックスの value のリスト
    array_mock = MagicMock()
    array_mock.value = [True, False]
    mo.ui.array.return_value = array_mock

    # dropdown
    dropdown_mock = MagicMock()
    dropdown_mock.value = "middle"
    mo.ui.dropdown.return_value = dropdown_mock

    # vstack/hstack
    mo.vstack.return_value = MagicMock()
    mo.hstack.return_value = MagicMock()

    return mo


class TestHwSelect:
    """HwSelect クラスのテスト"""

    def test_init_with_hw_list(self, sample_sales_df):
        """hw_list を指定して初期化できること"""
        with patch("gamedata.marimo_util.mo") as mock_mo:
            mock_mo.ui.array.return_value = MagicMock(value=[True, False])
            mock_mo.ui.checkbox.return_value = MagicMock(value=True)
            obj = mu.HwSelect(hw_list=["NSW", "PS5"])
        assert obj.hw_list == ["NSW", "PS5"]

    def test_init_without_hw_list_uses_get_hw_all(self, sample_sales_df):
        """hw_list が None の場合、get_hw_all() が呼ばれること"""
        with patch("gamedata.marimo_util.mo") as mock_mo, \
             patch.object(hs, "get_hw_all", return_value=["NSW", "PS5"]) as mock_get:
            mock_mo.ui.array.return_value = MagicMock(value=[True, False])
            mock_mo.ui.checkbox.return_value = MagicMock(value=True)
            obj = mu.HwSelect()
        mock_get.assert_called_once()

    def test_default_list_none_selects_all(self):
        """default_list=None の場合、全ハードが選択状態になること"""
        with patch("gamedata.marimo_util.mo") as mock_mo:
            mock_mo.ui.array.return_value = MagicMock(value=[True, True])
            mock_mo.ui.checkbox.return_value = MagicMock(value=True)
            obj = mu.HwSelect(hw_list=["NSW", "PS5"], default_list=None)
        # default_list が None なら hw_list と同じになる
        assert obj.hw_list == ["NSW", "PS5"]

    def test_value_returns_checked_hw(self):
        """value プロパティがチェック済み hw を返すこと"""
        with patch("gamedata.marimo_util.mo") as mock_mo:
            array_mock = MagicMock()
            array_mock.value = [True, False]
            mock_mo.ui.array.return_value = array_mock
            mock_mo.ui.checkbox.return_value = MagicMock(value=True)
            obj = mu.HwSelect(hw_list=["NSW", "PS5"])
        assert "NSW" in obj.value
        assert "PS5" not in obj.value

    def test_force_any_returns_all_when_none_selected(self):
        """force_any=True かつ何も選択されていない場合は全ハードを返すこと"""
        with patch("gamedata.marimo_util.mo") as mock_mo:
            array_mock = MagicMock()
            array_mock.value = [False, False]
            mock_mo.ui.array.return_value = array_mock
            mock_mo.ui.checkbox.return_value = MagicMock(value=False)
            obj = mu.HwSelect(hw_list=["NSW", "PS5"], force_any=True)
        assert obj.value == ["NSW", "PS5"]

    def test_force_any_false_returns_empty_when_none_selected(self):
        """force_any=False かつ何も選択されていない場合は空リストを返すこと"""
        with patch("gamedata.marimo_util.mo") as mock_mo:
            array_mock = MagicMock()
            array_mock.value = [False, False]
            mock_mo.ui.array.return_value = array_mock
            mock_mo.ui.checkbox.return_value = MagicMock(value=False)
            obj = mu.HwSelect(hw_list=["NSW", "PS5"], force_any=False)
        assert obj.value == []

    def test_display_more_than_11_items_uses_vstack(self):
        """11件超の場合 vstack で2行表示になること"""
        hw_list = [f"HW{i:02d}" for i in range(12)]
        with patch("gamedata.marimo_util.mo") as mock_mo:
            array_mock = MagicMock()
            array_mock.value = [True] * 12
            array_mock.__len__ = MagicMock(return_value=12)
            mock_mo.ui.array.return_value = array_mock
            mock_mo.ui.checkbox.return_value = MagicMock(value=True)
            mock_mo.vstack.return_value = MagicMock()
            obj = mu.HwSelect(hw_list=hw_list)
            obj._display_()
        mock_mo.vstack.assert_called_once()

    def test_display_11_or_fewer_items_uses_hstack(self):
        """11件以下の場合 hstack で1行表示になること"""
        hw_list = [f"HW{i:02d}" for i in range(5)]
        with patch("gamedata.marimo_util.mo") as mock_mo:
            array_mock = MagicMock()
            array_mock.value = [True] * 5
            array_mock.__len__ = MagicMock(return_value=5)
            mock_mo.ui.array.return_value = array_mock
            mock_mo.ui.checkbox.return_value = MagicMock(value=True)
            mock_mo.hstack.return_value = MagicMock()
            obj = mu.HwSelect(hw_list=hw_list)
            obj._display_()
        mock_mo.hstack.assert_called()


class TestEventSelect:
    """EventSelect クラスのテスト"""

    def test_init_default_value(self):
        with patch("gamedata.marimo_util.mo") as mock_mo:
            dropdown_mock = MagicMock()
            dropdown_mock.value = "middle"
            mock_mo.ui.dropdown.return_value = dropdown_mock
            obj = mu.EventSelect()
        assert obj.options == ["short", "middle", "long"]

    def test_value_returns_event_mask_constant(self):
        """value プロパティが EventMasks 定数を返すこと"""
        with patch("gamedata.marimo_util.mo") as mock_mo:
            dropdown_mock = MagicMock()
            dropdown_mock.value = "middle"
            mock_mo.ui.dropdown.return_value = dropdown_mock
            obj = mu.EventSelect()
        assert obj.value == he.EVENT_MASK_MIDDLE

    def test_value_short(self):
        with patch("gamedata.marimo_util.mo") as mock_mo:
            dropdown_mock = MagicMock()
            dropdown_mock.value = "short"
            mock_mo.ui.dropdown.return_value = dropdown_mock
            obj = mu.EventSelect(default_value="short")
        assert obj.value == he.EVENT_MASK_SHORT

    def test_value_long(self):
        with patch("gamedata.marimo_util.mo") as mock_mo:
            dropdown_mock = MagicMock()
            dropdown_mock.value = "long"
            mock_mo.ui.dropdown.return_value = dropdown_mock
            obj = mu.EventSelect(default_value="long")
        assert obj.value == he.EVENT_MASK_LONG

    def test_display_returns_widget(self):
        """_display_ がウィジェットを返すこと"""
        with patch("gamedata.marimo_util.mo") as mock_mo:
            dropdown_mock = MagicMock()
            dropdown_mock.value = "middle"
            mock_mo.ui.dropdown.return_value = dropdown_mock
            obj = mu.EventSelect()
        result = obj._display_()
        assert result is obj.widget


class TestMakerSelect:
    """MakerSelect クラスのテスト"""

    def test_init_with_maker_list(self):
        """maker_list を指定して初期化できること"""
        with patch("gamedata.marimo_util.mo") as mock_mo:
            mock_mo.ui.array.return_value = MagicMock(value=[True, False])
            mock_mo.ui.checkbox.return_value = MagicMock(value=True)
            obj = mu.MakerSelect(maker_list=["Nintendo", "SONY"])
        assert obj.maker_list == ["Nintendo", "SONY"]

    def test_init_without_maker_list_uses_get_maker_all(self):
        """maker_list が None の場合、get_maker_all() が呼ばれること"""
        with patch("gamedata.marimo_util.mo") as mock_mo, \
             patch.object(hs, "get_maker_all", return_value=["Nintendo", "SONY"]) as mock_get:
            mock_mo.ui.array.return_value = MagicMock(value=[True, False])
            mock_mo.ui.checkbox.return_value = MagicMock(value=True)
            obj = mu.MakerSelect()
        mock_get.assert_called_once()

    def test_value_returns_checked_makers(self):
        """value プロパティがチェック済みメーカーを返すこと"""
        with patch("gamedata.marimo_util.mo") as mock_mo:
            array_mock = MagicMock()
            array_mock.value = [True, False]
            mock_mo.ui.array.return_value = array_mock
            mock_mo.ui.checkbox.return_value = MagicMock(value=True)
            obj = mu.MakerSelect(maker_list=["Nintendo", "SONY"])
        assert "Nintendo" in obj.value
        assert "SONY" not in obj.value

    def test_force_any_returns_all_when_none_selected(self):
        """force_any=True かつ何も選択されていない場合は全メーカーを返すこと"""
        with patch("gamedata.marimo_util.mo") as mock_mo:
            array_mock = MagicMock()
            array_mock.value = [False, False]
            mock_mo.ui.array.return_value = array_mock
            mock_mo.ui.checkbox.return_value = MagicMock(value=False)
            obj = mu.MakerSelect(maker_list=["Nintendo", "SONY"], force_any=True)
        assert obj.value == ["Nintendo", "SONY"]

    def test_force_any_false_returns_empty_when_none_selected(self):
        with patch("gamedata.marimo_util.mo") as mock_mo:
            array_mock = MagicMock()
            array_mock.value = [False, False]
            mock_mo.ui.array.return_value = array_mock
            mock_mo.ui.checkbox.return_value = MagicMock(value=False)
            obj = mu.MakerSelect(maker_list=["Nintendo", "SONY"], force_any=False)
        assert obj.value == []

    def test_display_returns_hstack(self):
        """_display_ が hstack を返すこと"""
        with patch("gamedata.marimo_util.mo") as mock_mo:
            array_mock = MagicMock()
            array_mock.value = [True]
            mock_mo.ui.array.return_value = array_mock
            mock_mo.ui.checkbox.return_value = MagicMock(value=True)
            mock_mo.hstack.return_value = MagicMock()
            obj = mu.MakerSelect(maker_list=["Nintendo"])
            obj._display_()
        mock_mo.hstack.assert_called()
