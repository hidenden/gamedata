from datetime import datetime

def get_config() -> dict:
    the_date = datetime(2025, 10, 19)
    date_str = the_date.strftime("%Y.%m.%d")
    
    return {
        "date": the_date,
        "large": True,
        "description": f"ZAでSwitch2が大躍進:{date_str}ハード週販レポート",
    }
