"""Rendering is independent of marimo and Polars display settings."""

from collections.abc import Mapping
from datetime import date, datetime, time, timedelta
from decimal import Decimal
import json
import math


def json_value(value):
    """Convert observed values to strict JSON, including nested arbitrary columns."""
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    if isinstance(value, (date, datetime, time)):
        return value.isoformat()
    if isinstance(value, timedelta):
        return value.total_seconds()
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, bytes):
        return {"encoding": "hex", "value": value.hex()}
    if isinstance(value, Mapping):
        return {str(k): json_value(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_value(v) for v in value]
    return {"unsupported_type": type(value).__name__}


def render(result, *, format="markdown"):
    """Return Markdown or strict JSON text; never display or print implicitly."""
    if format not in ("markdown", "json"):
        raise ValueError("format must be markdown or json")
    text = json.dumps(json_value(result), ensure_ascii=False, indent=2, allow_nan=False)
    if format == "json":
        return text
    # Dynamic fences safely display annotation text containing backticks.
    import re

    longest = max((len(m.group()) for m in re.finditer(r"`+", text)), default=0)
    fence = "`" * max(3, longest + 1)
    if not isinstance(result, Mapping):
        return f"{fence}json\n{text}\n{fence}"
    lines = []
    for key, value in json_value(result).items():
        # The root keys are catalog fields; quote arbitrary keys as inline code.
        inline_fence = "`" * max(1, longest + 1)
        key_text = key.replace("\n", " ").replace("\r", " ")
        lines.append(f"### {inline_fence} {key_text} {inline_fence}")
        if isinstance(value, str):
            lines.append(f"{fence}text\n{value}\n{fence}")
        else:
            body = json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False)
            lines.append(f"{fence}json\n{body}\n{fence}")
    return "\n\n".join(lines)
