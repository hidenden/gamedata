from datetime import datetime

def get_config() -> dict:
    the_date = datetime(2025, 10, 5)
    date_str = the_date.strftime("%Y.%m.%d")
    
    return {
        "date": the_date,
        "large": False,
        "description": f"Ghost of YoteiでPS5躍進:{date_str}ハード週販レポート",
    }
