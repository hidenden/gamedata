"""Static annotation-level policy for AI-facing editorial decisions.

The values intentionally mirror ``database/annotation/level.md``. Runtime
code never reads that document, so the catalog works from any notebook cwd.
"""

from copy import deepcopy

from .models import record


_BANDS = (
    {
        "min_level": 0,
        "max_level": 9,
        "label": "数年に一度のイベント",
        "logical_meaning": "累計グラフに大きな影響を及ぼした出来事",
        "chart_visibility": "10年以上の長期グラフでも表示する",
        "editorial_priority": "mention_when_relevant",
        "examples": [
            "新ハードウェアの発売",
            "任天堂ハードウェアの価格改定",
            "業界の数年に一度の変化・イベント",
            "100万本以上級ゲームの発売日",
        ],
    },
    {
        "min_level": 10,
        "max_level": 19,
        "label": "年一のイベント",
        "logical_meaning": "累計グラフに中程度、週販グラフに大きな影響を及ぼした出来事",
        "chart_visibility": "2〜9年程度の累計グラフで表示する",
        "editorial_priority": "mention_when_relevant",
        "examples": [
            "任天堂以外のハードウェア価格改定",
            "ハードウェア新モデル・重要な周辺機器の発売",
            "50〜100万本級ゲームの発売日",
            "Nintendo Direct、Pokemon Presents、State of Play、Xbox Showcase",
            "E3、Gamescomなどの年次イベント",
        ],
    },
    {
        "min_level": 20,
        "max_level": 29,
        "label": "四半期に一度のイベント",
        "logical_meaning": "週販グラフに中程度の影響を及ぼし、累計グラフへの影響はほぼない出来事",
        "chart_visibility": "1〜2年（100週間）程度のグラフで表示する",
        "editorial_priority": "mention_if_explanatory",
        "examples": [
            "20〜50万本級ゲームの発売日",
            "100万本級ゲームのアップデート・新機能リリース",
            "ブラックフライデー、サマーセールなどの大型セール",
            "マイナーな周辺機器の発売・刷新",
        ],
    },
    {
        "min_level": 30,
        "max_level": 39,
        "label": "月一イベント",
        "logical_meaning": "週販グラフには影響しないが、著名な出来事",
        "chart_visibility": "半年〜1年程度の週販グラフで表示する",
        "editorial_priority": "usually_omit",
        "examples": [
            "10〜20万本級ゲームの発売日",
            "50万本級ゲームのアップデート・新機能リリース",
            "定期的なアップデート・新機能リリース、月次・年次セール",
        ],
    },
    {
        "min_level": 40,
        "max_level": None,
        "label": "週イベント・軽微な出来事",
        "logical_meaning": "週販グラフに影響がないマイナーな出来事",
        "chart_visibility": "週販の拡大グラフで表示する",
        "editorial_priority": "omit_unless_article_topic",
        "examples": ["10万本未満のソフト発売日", "ゲーム機に紐づく業界の話題"],
    },
)

_EDITORIAL_RULES = [
    "レベルは表示・記事化の優先度であり、販売変化との因果関係を保証しない。",
    "対象ハードと記事対象期間に関係しない注釈は、レベルにかかわらず記事に書かない。",
    "発売前のイベントは、販売データに反映される集計週を確認してから言及する。",
]


def _band_for(level: int) -> dict:
    for band in _BANDS:
        maximum = band["max_level"]
        if level >= band["min_level"] and (maximum is None or level <= maximum):
            return band
    raise AssertionError("annotation level bands must cover every non-negative integer")


def _validate_level(level: int) -> None:
    if isinstance(level, bool) or not isinstance(level, int):
        raise TypeError("level must be a non-negative integer")
    if level < 0:
        raise ValueError("level must be a non-negative integer")


def _validate_flag(name: str, value: bool) -> None:
    if not isinstance(value, bool):
        raise TypeError(f"{name} must be bool")


def annotation_level_policy() -> dict:
    """Return the static annotation-level policy without reading files or a DB."""
    return record(
        "guide:annotation_levels",
        "注釈レベルの重要度、グラフ表示範囲、記事化判断の方針",
        policy_version=1,
        runtime_source="Pythonの静的定数。database/annotation/level.mdは実行時に読まない",
        bands=deepcopy(_BANDS),
        editorial_rules=list(_EDITORIAL_RULES),
    )


def annotation_level_guidance(
    level: int,
    *,
    related_hardware: bool = True,
    in_reporting_window: bool = True,
    explains_sales_change: bool = False,
    is_article_topic: bool = False,
) -> dict:
    """Return a deterministic editorial decision for one annotation level."""
    _validate_level(level)
    for name, value in (
        ("related_hardware", related_hardware),
        ("in_reporting_window", in_reporting_window),
        ("explains_sales_change", explains_sales_change),
        ("is_article_topic", is_article_topic),
    ):
        _validate_flag(name, value)

    band = _band_for(level)
    relevant = related_hardware and in_reporting_window
    priority = band["editorial_priority"]
    if not relevant:
        should_mention = False
        reason = "対象ハードまたは記事対象期間に関係しないため"
    elif priority == "mention_when_relevant":
        should_mention = True
        reason = "重要度が高く、対象ハード・期間に関係するため"
    elif priority == "mention_if_explanatory":
        should_mention = explains_sales_change or is_article_topic
        reason = (
            "販売変化の説明または記事テーマに必要なため"
            if should_mention
            else "販売変化の説明にも記事テーマにも必要ではないため"
        )
    else:
        should_mention = is_article_topic
        reason = (
            "記事テーマそのものに当たるため"
            if should_mention
            else "軽微な出来事であり記事テーマではないため"
        )

    result = deepcopy(band)
    result.update(
        {
            "level": level,
            "related_hardware": related_hardware,
            "in_reporting_window": in_reporting_window,
            "explains_sales_change": explains_sales_change,
            "is_article_topic": is_article_topic,
            "should_consider": relevant and priority != "omit_unless_article_topic",
            "should_mention": should_mention,
            "reason": reason,
        }
    )
    return result
