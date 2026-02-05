from datetime import datetime

def get_config() -> dict:
    the_date = datetime(2026, 2, 1)
    date_str = the_date.strftime("%Y.%m.%d")
    
    return {
        "date": the_date,
        "year": the_date.year,
        "large": True,
        "description": f"Switch歴代最低週販:{date_str}ハード週販レポート",
    }
