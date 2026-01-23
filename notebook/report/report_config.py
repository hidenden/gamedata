from datetime import datetime

def get_config() -> dict:
    the_date = datetime(2026, 1, 18)
    date_str = the_date.strftime("%Y.%m.%d")
    
    return {
        "date": the_date,
        "year": the_date.year,
        "large": True,
        "description": f"年末年始商戦終了｡PS5四桁に落ち込み:{date_str}ハード週販レポート",
    }
