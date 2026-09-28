from datetime import datetime


def get_config() -> dict:
    the_date = datetime(2026, 9, 20)
    date_str = the_date.strftime("%Y.%m.%d")

    return {
        "date": the_date,
        "year": the_date.year,
        "large": True,
        "description": f"Switch2 普及速度一位をDSに譲る:{date_str}ハード週販レポート",
    }
