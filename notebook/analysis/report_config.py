from datetime import datetime

def get_config() -> dict:
    the_date = datetime(2025, 9, 28)
    date_str = the_date.strftime("%Y.%m.%d")
    
    return {
        "date": the_date,
        "large": False,
        "description": f"サイレントヒルf効果でPS5が9月前年比超え:{date_str}ハード週販レポート",
    }
