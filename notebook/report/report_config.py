from datetime import datetime

def get_config() -> dict:
    the_date = datetime(2026, 4, 5)
    date_str = the_date.strftime("%Y.%m.%d")
    
    return {
        "date": the_date,
        "year": the_date.year,
        "large": True,
        "description": f"Switch2国内累計500万台突破 PS4集計終了:{date_str}ハード週販レポート",
    }
