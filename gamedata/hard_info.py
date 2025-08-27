# ゲームハードおよびゲームメーカーの情報を返すライブラリ

HARD_COLORS = {
    'PS5': "#0070d1",
    'XSX': "#029422",
    'NSW': "#E60012",
    'NS2': "#87010C",
    'XBOne': "#59B06A",
    'PS4': "#003087",
    'WiiU': "#0094D8",
    'Vita': "#1564D3",
    '3DS': "#EC3E2E",
    'Wii': "#00c0e0",
    'PS3': "#2E3139",
    'XB360': '#1FAE2E',
    'DS': "#7a7a7a",
    'PSP': '#2734D0',
    'Xbox': '#0F7C10',
    'GC': "#601F8B",
    'GBA': "#6c3fa4",
    'PS2': "#0143D2",
    'WS': '#FF8F1F',
    'PKS': '#5D6BFF',
    'DC': "#F06400",
    'NeoGeoP': '#FFCF33',
    'GB': "#A43070",
    'N64': "#320E50",
    'PS': "#9998A5",
    'SATURN': "#58636A"
}

MAKER_COLORS = {
    'SONY': "#0311B0",
    'Microsoft': '#107C10',
    'Nintendo': '#E60012',
    'BANDAI': "#F5804D",
    'SEGA': '#008CD2',
    'SNK': '#FFC400',
    'PC': '#000000'
}

def get_hard_colors(hw:list[str]) -> list[str]:
    """
    ハードウェア名のリストから対応する色のリストを取得する。
    
    Args:
        hw: ハードウェア名のリスト
    
    Returns:
        list[str]: ハードウェア名に対応する色のリスト
    """
    return [HARD_COLORS.get(h, 'black') for h in hw]


def get_maker_colors(maker:list[str]) -> list[str]:
    """
    メーカー名のリストから対応する色のリストを取得する。

    Args:
        maker: メーカー名のリスト

    Returns:
        list[str]: メーカー名に対応する色のリスト
    """
    return [MAKER_COLORS.get(m, 'black') for m in maker]

HARD_NAMES = {
    "PS5": "PlayStation5",
    "XSX": "Xbox Series X|S",
    "NSW": "Nintendo Switch",
    "NS2": "Nintendo Switch2",
    "XBOne": "Xbox One",
    "PS4": "PlayStation4",
    "WiiU": "Wii U",
    "Vita": "PlayStation Vita",
    "3DS": "Nintendo 3DS",
    "Wii": "Wii",
    "PS3": "PlayStation3",
    "XB360": "Xbox 360",
    "DS": "Nintendo DS",
    "PSP": "PlayStation Portable",
    "Xbox": "Xbox",
    "GC": "Nintendo GAMECUBE",
    "GBA": "GAME BOY ADVANCE",
    "PS2": "PlayStation2",
    "WS": "WonderSwan",
    "PKS": "PocketStation",
    "DC": "DreamCast",
    "NeoGeoP": "NeoGeo Pocket",
    "GB": "GAME BOY",
    "N64": "NINTENDO64",
    "PS": "PlayStation",
    "SATURN": "SEGA SATURN"
}

def get_hard_names(hw:list[str]) -> list[str]:
    """
    Returns a list of hardware names corresponding to the given hardware identifiers.

    Args:
        hw (list[str]): A list of hardware identifier strings.

    Returns:
        list[str]: A list of hardware names. If an identifier is not found, 'unknown' is used.
    """
    return [HARD_NAMES.get(h, 'unknown') for h in hw]
