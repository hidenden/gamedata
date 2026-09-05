from datetime import datetime


def get_config() -> dict:
    the_date = datetime(2026, 8, 30)
    date_str = the_date.strftime("%Y.%m.%d")

    return {
        "date": the_date,
        "year": the_date.year,
        "large": True,
        "description": f"14週間ぶりにPS5がSwitchを下回りました:{date_str}ハード週販レポート",
    }
