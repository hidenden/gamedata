"""Read-only AI catalog for gamedata.

Start with ``overview()``, find an entry with ``search()``, then ``describe()``.
Use ``inspect_frame()`` on existing notebook data; it never loads the database.
All results are JSON-compatible dictionaries. ``render()`` returns display text.
"""

from .registry import describe, overview, search
from .inspection import inspect_frame
from .rendering import render
from .annotation_levels import annotation_level_guidance, annotation_level_policy

__all__ = [
    "overview",
    "search",
    "describe",
    "inspect_frame",
    "render",
    "annotation_level_policy",
    "annotation_level_guidance",
]
