from datetime import datetime


def get_config() -> dict:
    the_date = datetime(2026, 5, 17)
    date_str = the_date.strftime("%Y.%m.%d")

    return {
        "date": the_date,
        "year": the_date.year,
        "large": True,
        "description": f"Switch2に年末商戦級駆け込み需要:{date_str}ハード週販レポート",
    }
