from datetime import datetime

def get_config() -> dict:
    the_date = datetime(2025, 9, 7)
    date_str = the_date.strftime("%Y.%m.%d")
    
    return {
        "date": the_date,
        "large": True,
        "description": f"PS5 オータムセールで急伸、700万台突破!:{date_str}ハード週販レポート",
    }
