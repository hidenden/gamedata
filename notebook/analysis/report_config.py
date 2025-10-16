from datetime import datetime

def get_config() -> dict:
    the_date = datetime(2025, 10, 12)
    date_str = the_date.strftime("%Y.%m.%d")
    
    return {
        "date": the_date,
        "large": True,
        "description": f"嵐の前の静けさ:{date_str}ハード週販レポート",
    }
