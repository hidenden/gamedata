from datetime import datetime


def get_config() -> dict:
    the_date = datetime(2026, 9, 6)
    date_str = the_date.strftime("%Y.%m.%d")

    return {
        "date": the_date,
        "year": the_date.year,
        "large": True,
        "description": f"低調ながらも上昇基調の9月第1週:{date_str}ハード週販レポート",
    }
