from datetime import datetime

def get_config() -> dict:
    the_date = datetime(2025, 12, 21)
    date_str = the_date.strftime("%Y.%m.%d")
    
    return {
        "date": the_date,
        "large": True,
        "description": f"Switch2 20万台出荷継続中:{date_str}ハード週販レポート",
    }
