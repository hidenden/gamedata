from datetime import datetime

def get_config() -> dict:
    the_date = datetime(2025, 11, 2)
    date_str = the_date.strftime("%Y.%m.%d")
    
    return {
        "date": the_date,
        "large": True,
        "description": f"Switch2は8万台超、多めの出荷が続きます:{date_str}ハード週販レポート",
    }
