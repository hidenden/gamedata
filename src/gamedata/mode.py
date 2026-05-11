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
        raise NotImplementedError("Fiscal quarter mode is not supported yet.")
    if normalized in {"fiscalyear", "fy"}:
        raise NotImplementedError("Fiscal year mode is not supported yet.")

    raise ValueError(f"Unsupported mode: {mode}")
