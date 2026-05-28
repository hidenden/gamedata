from enum import Enum


class Mode(Enum):
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"
    FISCAL_QUARTER = "fiscal_quarter"
    FISCAL_YEAR = "fiscal_year"


def parse_mode(mode: str) -> Mode:
    if not isinstance(mode, str):
        raise ValueError("mode must be a string.")

    normalized = mode.strip().lower()
    if normalized in {"week", "w"}:
        return Mode.WEEK
    if normalized in {"month", "m"}:
        return Mode.MONTH
    if normalized in {"quarter", "q", "cq"}:
        return Mode.QUARTER
    if normalized in {"year", "y", "cy"}:
        return Mode.YEAR
    if normalized in {"fiscalquarter", "fiscalquater", "fq"}:
        return Mode.FISCAL_QUARTER
    if normalized in {"fiscalyear", "fy"}:
        return Mode.FISCAL_YEAR

    raise ValueError(f"Unsupported mode: {mode}")
