from datetime import datetime

def get_config() -> dict:
    the_date = datetime(2026, 1, 25)
    date_str = the_date.strftime("%Y.%m.%d")
    
    return {
        "date": the_date,
        "year": the_date.year,
        "large": True,
        "description": f":{date_str}ハード週販レポート",
    }
