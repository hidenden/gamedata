from datetime import datetime


def get_config() -> dict:
    the_date = datetime(2026, 5, 24)
    date_str = the_date.strftime("%Y.%m.%d")

    return {
        "date": the_date,
        "year": the_date.year,
        "large": True,
        "description": f"Switch2値上げ直前駆け込み週:{date_str}ハード週販レポート",
    }
