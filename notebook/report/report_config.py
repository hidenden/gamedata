from datetime import datetime

def get_config() -> dict:
    the_date = datetime(2025, 12, 28)
    date_str = the_date.strftime("%Y.%m.%d")
    
    return {
        "date": the_date,
        "year": the_date.year,
        "large": True,
        "description": f"Switch2 2025年は378万台:{date_str}ハード週販レポート",
    }
