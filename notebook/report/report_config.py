from datetime import datetime


def get_config() -> dict:
    the_date = datetime(2026, 10, 18)
    date_str = the_date.strftime("%Y.%m.%d")

    return {
        "date": the_date,
        "year": the_date.year,
        "large": True,
        "description": f"Switch 過去最低週販を更新:{date_str}ハード週販レポート",
    }
