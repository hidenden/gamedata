from datetime import datetime


def get_config() -> dict:
    the_date = datetime(2026, 7, 26)
    date_str = the_date.strftime("%Y.%m.%d")

    return {
        "date": the_date,
        "year": the_date.year,
        "large": True,
        "description": f"スプラトゥーン・レイダースがSwitch2を牽引:{date_str}ハード週販レポート",
    }
