from datetime import datetime

def get_config() -> dict:
    the_date = datetime(2026, 3, 22)
    date_str = the_date.strftime("%Y.%m.%d")
    
    return {
        "date": the_date,
        "year": the_date.year,
        "large": True,
        "description": f"3週連続ぽこあポケモン首位でSwitch2好調:{date_str}ハード週販レポート",
    }
