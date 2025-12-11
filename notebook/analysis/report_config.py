from datetime import datetime

def get_config() -> dict:
    the_date = datetime(2025, 12, 7)
    date_str = the_date.strftime("%Y.%m.%d")
    
    return {
        "date": the_date,
        "large": True,
        "description": f"Switch2 300万台到達!:{date_str}ハード週販レポート",
    }
