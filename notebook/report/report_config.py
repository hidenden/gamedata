from datetime import datetime


def get_config() -> dict:
    the_date = datetime(2026, 7, 19)
    date_str = the_date.strftime("%Y.%m.%d")

    return {
        "date": the_date,
        "year": the_date.year,
        "large": True,
        "description": f"PS5､8週連続でSwitchを上回る新記録:{date_str}ハード週販レポート",
    }
