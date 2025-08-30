from datetime import datetime

def get_config() -> dict:
    the_date = datetime(year=2025, month=8, day=31)
    date_str = the_date.strftime("%Y.%m.%d")
    
    return {
        "date": the_date,
        "large": False,
        "description": f"{date_str}時点の国内ゲームハードの週販データを分析したレポートです。"
    }
