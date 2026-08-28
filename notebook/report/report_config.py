from datetime import datetime


def get_config() -> dict:
    the_date = datetime(2026, 8, 23)
    date_str = the_date.strftime("%Y.%m.%d")

    return {
        "date": the_date,
        "year": the_date.year,
        "large": True,
        "description": f"Switch2最低記録､季節要因で全機種低迷:{date_str}ハード週販レポート",
    }
