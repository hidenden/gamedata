from datetime import datetime


def get_config() -> dict:
    the_date = datetime(2026, 6, 7)
    date_str = the_date.strftime("%Y.%m.%d")

    return {
        "date": the_date,
        "year": the_date.year,
        "large": True,
        "description": f"駆け込み反動でSwitch2さらに落ち込み:{date_str}ハード週販レポート",
    }
