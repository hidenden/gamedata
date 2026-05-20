from datetime import datetime


def get_config() -> dict:
    the_date = datetime(2026, 5, 17)
    date_str = the_date.strftime("%Y.%m.%d")

    return {
        "date": the_date,
        "year": the_date.year,
        "large": True,
        "description": f"Switch2駆け込み需要で好調が続く:{date_str}ハード週販レポート",
    }
