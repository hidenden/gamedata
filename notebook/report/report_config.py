from datetime import datetime

def get_config() -> dict:
    the_date = datetime(2026, 2, 8)
    date_str = the_date.strftime("%Y.%m.%d")
    
    return {
        "date": the_date,
        "year": the_date.year,
        "large": True,
        "description": f"Switch 4桁の落ち込む:{date_str}ハード週販レポート",
    }
