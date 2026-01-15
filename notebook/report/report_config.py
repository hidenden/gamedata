from datetime import datetime

def get_config() -> dict:
    the_date = datetime(2026, 1, 11)
    date_str = the_date.strftime("%Y.%m.%d")
    
    return {
        "date": the_date,
        "year": the_date.year,
        "large": True,
        "description": f"Switch2 400万台突破で2026年スタート:{date_str}ハード週販レポート",
    }
