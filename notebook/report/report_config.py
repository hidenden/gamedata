from datetime import datetime


def get_config() -> dict:
    the_date = datetime(2026, 10, 11)
    date_str = the_date.strftime("%Y.%m.%d")

    return {
        "date": the_date,
        "year": the_date.year,
        "large": True,
        "description": f"Switch 3700万台到達:{date_str}ハード週販レポート",
    }
