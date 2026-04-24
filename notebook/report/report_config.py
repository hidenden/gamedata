from datetime import datetime

def get_config() -> dict:
    the_date = datetime(2026, 4, 19)
    date_str = the_date.strftime("%Y.%m.%d")
    
    return {
        "date": the_date,
        "year": the_date.year,
        "large": True,
        "description": f"トモコレがSwitch Liteを牽引:{date_str}ハード週販レポート",
    }
