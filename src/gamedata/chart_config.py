# chart configuration for gamedata project
import altair as alt


@alt.theme.register(name="publish", enable=False)
def publish_theme():
    return {
        "config": {
            "axis": {
                "ticks": True,
                "grid": True,
                "labelFontSize": 14,
                "labelAngle": 0,
                "titleFontSize": 14,
                "gridOpacity": 0.7,
            },
            "axisX": {
                "labelAngle": 90,
            },
            # 色分けした際の項目
            "legend": {
                "labelFontSize": 14,
                "labelAngle": 0,
                "titleFontSize": 12,
                "titleAngle": 0,
            },
            # グラフ上部の文字
            "header": {
                "labelFontSize": 20,
                "labelAngle": 0,
                "titleFontSize": 20,
                "titleAngle": 0,
            },
            "text": {
                "fontSize": 12,
                "fontWeight": "bold",
                "opacity": 0.85,
                "limit": 120,
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
                "labelAngle": 0,
                "labelColor": "black",
                "titleFontSize": 14,
                "titleAngle": 0,
                "titleColor": "black",
            },
            # グラフ上部の文字
            "header": {
                "labelFontSize": 20,
                "labelAngle": 0,
                "labelColor": "black",
                "titleFontSize": 25,
                "titleAngle": 0,
                "titleColor": "black",
            },
            "text": {
                "fontSize": 12,
                "fontWeight": "bold",
                "opacity": 0.85,
                "limit": 120,
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
