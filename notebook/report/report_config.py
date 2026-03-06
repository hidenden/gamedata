from datetime import datetime

def get_config() -> dict:
    the_date = datetime(2026, 3, 1)
    date_str = the_date.strftime("%Y.%m.%d")
    
    return {
        "date": the_date,
        "year": the_date.year,
        "large": True,
        "description": f"バイオハザード9効果?でハード好況:{date_str}ハード週販レポート",
    }
