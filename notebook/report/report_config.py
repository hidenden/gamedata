from datetime import datetime


def get_config() -> dict:
    the_date = datetime(2026, 8, 2)
    date_str = the_date.strftime("%Y.%m.%d")

    return {
        "date": the_date,
        "year": the_date.year,
        "large": True,
        "description": f"Switch2は再び3万台に低下:{date_str}ハード週販レポート",
    }
