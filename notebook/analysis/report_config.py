from datetime import datetime

def get_config() -> dict:
    the_date = datetime(2025, 11, 23)
    date_str = the_date.strftime("%Y.%m.%d")
    
    return {
        "date": the_date,
        "large": True,
        "description": f"Switch2 12万台 年末商戦独走:{date_str}ハード週販レポート",
    }
