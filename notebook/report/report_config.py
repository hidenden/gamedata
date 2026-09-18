from datetime import datetime


def get_config() -> dict:
    the_date = datetime(2026, 9, 13)
    date_str = the_date.strftime("%Y.%m.%d")

    return {
        "date": the_date,
        "year": the_date.year,
        "large": True,
        "description": f"次週 Switch2の累計一位の正念場:{date_str}ハード週販レポート",
    }
