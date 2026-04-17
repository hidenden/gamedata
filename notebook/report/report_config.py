from datetime import datetime

def get_config() -> dict:
    the_date = datetime(2026, 4, 12)
    date_str = the_date.strftime("%Y.%m.%d")
    
    return {
        "date": the_date,
        "year": the_date.year,
        "large": True,
        "description": f"Q2はハード販売台数控えめ:{date_str}ハード週販レポート",
    }
