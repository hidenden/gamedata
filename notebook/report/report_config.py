from datetime import datetime


def get_config() -> dict:
    the_date = datetime(2026, 11, 1)
    date_str = the_date.strftime("%Y.%m.%d")

    return {
        "date": the_date,
        "year": the_date.year,
        "large": True,
        "description": f"ゼルダ40周年記念モデルでSwitch2爆増:{date_str}ハード週販レポート",
    }
