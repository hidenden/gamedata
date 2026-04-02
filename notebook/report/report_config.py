from datetime import datetime

def get_config() -> dict:
    the_date = datetime(2026, 3, 29)
    date_str = the_date.strftime("%Y.%m.%d")
    
    return {
        "date": the_date,
        "year": the_date.year,
        "large": True,
        "description": f"PS5値上げ前の駆け込み需要は?:{date_str}ハード週販レポート",
    }
