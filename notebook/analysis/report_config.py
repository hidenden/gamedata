from datetime import datetime

def get_config() -> dict:
    the_date = datetime(2025, 8, 31)
    date_str = the_date.strftime("%Y.%m.%d")
    
    return {
        "date": the_date,
        "large": True,
        "description": f"PS5の障壁は無い、ハード台数的には:{date_str}ハード週販レポート",
    }
