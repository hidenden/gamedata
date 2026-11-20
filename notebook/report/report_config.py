from datetime import datetime


def get_config() -> dict:
    the_date = datetime(2026, 11, 15)
    date_str = the_date.strftime("%Y.%m.%d")

    return {
        "date": the_date,
        "year": the_date.year,
        "large": True,
        "description": f"Switch2 時オカ2週目も4万台維持:{date_str}ハード週販レポート",
    }
