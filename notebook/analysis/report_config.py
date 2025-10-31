from datetime import datetime

def get_config() -> dict:
    the_date = datetime(2025, 10, 26)
    date_str = the_date.strftime("%Y.%m.%d")
    
    return {
        "date": the_date,
        "large": True,
        "description": f"Switch2はスパイク的出荷作戦？:{date_str}ハード週販レポート",
    }
