from datetime import datetime

def get_config() -> dict:
    the_date = datetime(2025, 11, 9)
    date_str = the_date.strftime("%Y.%m.%d")
    
    return {
        "date": the_date,
        "large": True,
        "description": f"Switch2年末商戦に突入:{date_str}ハード週販レポート",
    }
