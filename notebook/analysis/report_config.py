from datetime import datetime

def get_config() -> dict:
    the_date = datetime(2025, 9, 14)
    date_str = the_date.strftime("%Y.%m.%d")
    
    return {
        "date": the_date,
        "large": True,
        "description": f"Switch2 200万台到達:{date_str}ハード週販レポート",
    }
