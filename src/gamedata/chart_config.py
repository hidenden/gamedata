# chart configuration for gamedata project
import altair as alt

# PNG/SVG保存時の出力解像度を上げる倍率
ALT_EMBED_SCALE_FACTOR = 4
ALT_EMBED_OPTIONS = {
    "actions": {
        "export": True,
        "source": False,
        "compiled": False,
        "editor": False,
    },
    "scaleFactor": ALT_EMBED_SCALE_FACTOR,
}


@alt.theme.register(name="publish", enable=False)
def publish_theme():
    return {
        "usermeta": {"embedOptions": ALT_EMBED_OPTIONS},
        "config": {
            "axis": {
                "ticks": True,
                "grid": True,
                "labelFontSize": 14,
                "titleFontSize": 14,
                "gridOpacity": 0.7,
            },
            "axisX": {
                "labelAngle": 90,
            },
            # 色分けした際の項目
            "legend": {
                "labelFontSize": 14,
                "titleFontSize": 12,
            },
            # グラフ上部の文字
            "header": {
                "labelFontSize": 20,
                "titleFontSize": 20,
            },
            "text": {
                "fontSize": 10,
                "fontWeight": "bold",
                "opacity": 0.8,
                "limit": 130,
            },
            "line": {"strokeWidth": 2},
            "point": {"filled": True, "size": 80, "opacity": 0.7, "fillOpacity": 0.7},
            "title": {
                "fontSize": 14,
                "subtitleFontSize": 12,
            },
            # 図の大きさ
            "view": {"width": 760, "height": 380},
        }
    }


@alt.theme.register(name="edit", enable=True)
def edit_theme():
    return {
        "usermeta": {"embedOptions": ALT_EMBED_OPTIONS},
        "config": {
            "axis": {
                "ticks": True,
                "grid": True,
                "labelFontSize": 12,
                "labelAngle": 0,
                "labelColor": "black",
                "titleFontSize": 14,
                "titleColor": "#202020",
                "gridColor": "darkgray",
                "gridOpacity": 0.7,
                "tickColor": "black",
                "domainColor": "black",
                "bandColor": "lightgray",
            },
            "axisX": {
                "labelAngle": 90,
            },
            # 色分けした際の項目
            "legend": {
                "labelFontSize": 14,
                "labelColor": "black",
                "titleFontSize": 14,
                "titleColor": "black",
            },
            # グラフ上部の文字
            "header": {
                "labelFontSize": 20,
                "labelColor": "black",
                "titleFontSize": 25,
                "titleColor": "black",
            },
            "text": {
                "fontSize": 10,
                "fontWeight": "bold",
                "opacity": 0.8,
                "limit": 150,
            },
            "line": {"strokeWidth": 2},
            "point": {"filled": True, "size": 90, "opacity": 0.7, "fillOpacity": 0.7},
            "title": {
                "fontSize": 14,
                "subtitleFontSize": 14,
                "color": "#404040",
                "subtitleColor": "#202020",
            },
            # 図の大きさ
            "view": {
                "width": 900,
                "height": 480,
            },
            # 図の背景
            "background": "white",
        }
    }
