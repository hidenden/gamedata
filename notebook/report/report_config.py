from datetime import datetime

def get_config() -> dict:
    the_date = datetime(2026, 2, 15)
    date_str = the_date.strftime("%Y.%m.%d")
    
    return {
        "date": the_date,
        "year": the_date.year,
        "large": True,
        "description": f"Switch2とPS5の台数差が300万台を切りました:{date_str}ハード週販レポート",
    }
