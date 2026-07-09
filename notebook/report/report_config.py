from datetime import datetime


def get_config() -> dict:
    the_date = datetime(2026, 7, 5)
    date_str = the_date.strftime("%Y.%m.%d")

    return {
        "date": the_date,
        "year": the_date.year,
        "large": True,
        "description": f"リズム天国効果でSwitch2,Switch好調:{date_str}ハード週販レポート",
    }
