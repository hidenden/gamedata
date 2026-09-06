"""Small deterministic search index and stable record lookup."""

from copy import deepcopy
import re

from .datasets import DATASETS
from .functions import FUNCTIONS, describe_function
from .models import SCHEMA_VERSION, record
from .recipes import RECIPES

KINDS = ("dataset", "column", "function", "recipe")


def describe(id, *, sections=None, params=None):
    """Return a fresh record. params resolves function output variants only.

    Unknown IDs raise KeyError; invalid parameters/sections raise ValueError.
    No function is executed and no database is read.
    """
    if not isinstance(id, str) or ":" not in id:
        raise KeyError(id)
    kind, name = id.split(":", 1)
    if params is not None and kind != "function":
        raise ValueError("params is only supported for function records")
    if kind == "dataset":
        result = DATASETS[name]
    elif kind == "column":
        ds, sep, col = name.partition(".")
        if not sep:
            raise KeyError(id)
        fields = DATASETS[ds]["columns"][col]
        result = record(
            id,
            fields["summary"],
            dataset=f"dataset:{ds}",
            **{k: v for k, v in fields.items() if k != "summary"},
        )
    elif kind == "function":
        result = describe_function(name, params)
    elif kind == "recipe":
        result = RECIPES[name]
    else:
        raise KeyError(id)
    if sections is not None:
        if isinstance(sections, str):
            sections = [sections]
        invalid = set(sections) - set(result)
        if invalid:
            raise ValueError(f"Unknown sections: {sorted(invalid)}")
        keep = {"schema_version", "id", "kind", "summary", *sections}
        result = {k: v for k, v in result.items() if k in keep}
    return deepcopy(result)


def _entries():
    for ds, info in DATASETS.items():
        yield info["id"], "dataset", info["summary"]
        for col, fields in info["columns"].items():
            yield f"column:{ds}.{col}", "column", fields["summary"]
    for name, info in FUNCTIONS.items():
        yield f"function:{name}", "function", info[1]
    for info in RECIPES.values():
        yield info["id"], "recipe", info["summary"]


def search(query, *, kind=None, limit=10):
    """Search Japanese descriptions or Python names; bounded and deterministic.

    Exact matches rank first, followed by token/Japanese bigram overlap.
    An empty query lists entries, optionally restricted by kind.
    """
    if kind is not None and kind not in KINDS:
        raise ValueError(f"kind must be one of {KINDS}")
    if not isinstance(query, str):
        raise TypeError("query must be str")
    if type(limit) is not int or not 1 <= limit <= 100:
        raise ValueError("limit must be between 1 and 100")
    query = query.strip().casefold()
    tokens = re.findall(r"[a-z0-9_]+|[^\W\d_a-z]+", query)
    fragments = set()
    for token in tokens:
        if token.isascii() or len(token) < 2:
            fragments.add(token)
        else:
            fragments.update(token[i : i + 2] for i in range(len(token) - 1))
    matches = []
    for identifier, entry_kind, summary in _entries():
        if kind is not None and entry_kind != kind:
            continue
        haystack = f"{identifier} {summary}".casefold()
        score = (100 if query and query in haystack else 0) + sum(
            f in haystack for f in fragments
        )
        if not query or score:
            matches.append(
                {
                    "id": identifier,
                    "kind": entry_kind,
                    "summary": summary,
                    "score": score,
                }
            )
    matches.sort(key=lambda item: (-item["score"], item["id"]))
    return {
        "schema_version": SCHEMA_VERSION,
        "query": query,
        "total": len(matches),
        "items": matches[:limit],
        "truncated": len(matches) > limit,
    }


def overview():
    """Compact entry point for an AI connected to a notebook."""
    from .. import __version__

    return {
        "schema_version": SCHEMA_VERSION,
        "library": "gamedata",
        "library_version": __version__,
        "summary": "日本国内ゲームハード販売データの加工・集計・可視化ライブラリ（Polars）",
        "datasets": [
            {"id": DATASETS[k]["id"], "summary": DATASETS[k]["summary"]}
            for k in ("hard_sales", "hard_info", "hard_annotation")
        ],
        "categories": [
            "ロード",
            "期間・機種抽出",
            "週次・月次集計",
            "発売からの累計比較",
        ],
        "coverage": {
            "functions": len(FUNCTIONS),
            "datasets": len(DATASETS),
            "note": "初期版は主要関数のみ登録。未登録はライブラリに存在しないという意味ではない",
        },
        "rules": [
            "unitsは補正済み。adjust_unitsを再加算しない",
            "累計は時系列方向にsumしない。sum_unitsの起点は出力データセットごとに確認",
            "月次・年次はreport_dateの所属期間。会計年度は4月始まりの期末年",
            "欠測は販売ゼロとは限らない。最新月・年は途中の場合がある",
            "注釈との結合で販売行が増殖する可能性がある",
        ],
        "next_calls": [
            "catalog.inspect_frame(hard_sales_all_df, dataset='hard_sales')",
            "catalog.search('発売からの累計を比較')",
            "catalog.describe('dataset:hard_sales')",
        ],
        "usage": "from gamedata import catalog; print(catalog.render(catalog.overview()))",
    }
