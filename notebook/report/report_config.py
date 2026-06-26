from datetime import datetime


def get_config() -> dict:
    the_date = datetime(2026, 6, 21)
    date_str = the_date.strftime("%Y.%m.%d")

    return {
        "date": the_date,
        "year": the_date.year,
        "large": True,
        "description": f"Switchも下げ止まり:{date_str}ハード週販レポート",
    }
