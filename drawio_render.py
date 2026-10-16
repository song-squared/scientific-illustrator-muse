#!/usr/bin/env python3
"""极简 .drawio -> PNG 渲染器（PIL），用于无 draw.io 时的几何验证/交叉检查。
支持：直边（含虚线）、矩形、椭圆、文本。不支持：曲线箭头等。"""
import xml.etree.ElementTree as ET
import sys, re
from PIL import Image, ImageDraw, ImageFont

def parse_style(s):
    d = {}
    for part in (s or "").split(";"):
        if "=" in part:
            k, v = part.split("=", 1)
            d[k] = v
    return d

def main(inp, outp, scale=2):
    t = ET.parse(inp)
    model = t.getroot().find(".//mxGraphModel")
    pw, ph = int(model.get("pageWidth", 1340)), int(model.get("pageHeight", 950))
    img = Image.new("RGB", (pw * scale, ph * scale), "black")
    dr = ImageDraw.Draw(img)
    try:
        font_path = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
        fonts = {}
        def font(sz):
            if sz not in fonts:
                fonts[sz] = ImageFont.truetype(font_path, sz * scale)
            return fonts[sz]
    except Exception as e:
        print("font load fail:", e); sys.exit(1)

    for c in t.getroot().findall(".//mxCell"):
        style = parse_style(c.get("style"))
        g = c.find("mxGeometry")
        if g is None:
            continue
        if c.get("edge") == "1":
            sp, tp = g.find("mxPoint[@as='sourcePoint']"), g.find("mxPoint[@as='targetPoint']")
            if sp is None or tp is None:
                continue
            x1, y1 = float(sp.get("x")) * scale, float(sp.get("y")) * scale
            x2, y2 = float(tp.get("x")) * scale, float(tp.get("y")) * scale
            col = style.get("strokeColor", "#FFFFFF")
            w = max(1, int(style.get("strokeWidth", 3)) * scale)
            if style.get("dashed") == "1":
                # 简单虚线
                import math
                L = math.hypot(x2 - x1, y2 - y1)
                n = max(1, int(L / (14 * scale)))
                for i in range(n):
                    if i % 2 == 0:
                        continue
                    ax = x1 + (x2 - x1) * i / n; ay = y1 + (y2 - y1) * i / n
                    bx = x1 + (x2 - x1) * (i + 1) / n; by = y1 + (y2 - y1) * (i + 1) / n
                    dr.line([ax, ay, bx, by], fill=col, width=w)
            else:
                dr.line([x1, y1, x2, y2], fill=col, width=w)
        elif c.get("vertex") == "1":
            x, y = float(g.get("x", 0)) * scale, float(g.get("y", 0)) * scale
            w_, h_ = float(g.get("width", 0)) * scale, float(g.get("height", 0)) * scale
            val = c.get("value")
            if val is not None and ("text;" in (c.get("style") or "")):
                sz = int(style.get("fontSize", 22))
                f = font(sz)
                bbox = dr.textbbox((0, 0), val, font=f)
                tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
                dr.text((x + w_ / 2 - tw / 2 - bbox[0], y + h_ / 2 - th / 2 - bbox[1]),
                        val, font=f, fill=style.get("fontColor", "#FF0000"))
            else:
                sc = style.get("strokeColor", "#FFFFFF")
                fc = style.get("fillColor", "none")
                sw = max(1, int(style.get("strokeWidth", 3)) * scale)
                box = [x, y, x + w_, y + h_]
                if "ellipse" in (c.get("style") or ""):
                    if fc != "none":
                        dr.ellipse(box, fill=fc)
                    if sc != "none":
                        dr.ellipse(box, outline=sc, width=sw)
                else:
                    if fc != "none" and fc != "#000000":
                        dr.rectangle(box, fill=fc)
                    elif fc == "#000000":
                        dr.rectangle(box, fill="black")
                    if sc != "none":
                        dr.rectangle(box, outline=sc, width=sw)
    img.save(outp)
    print("saved", outp, img.size)

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 2)
