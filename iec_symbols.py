#!/usr/bin/env python3
"""IEC 60617 电气符号库（Python 版）——供 AI 直接调用的符号函数。

每个符号 = 一组基础图元（线/圆/矩形/文本），保证无头渲染零依赖。
配套 draw.io UI 库见 iec60617.xml（同一套符号，可拖拽）。

用法：
    from iec_symbols import no_contact, motor_3ph
    no_contact(ctx, x, y)   # 在 (x, y) 处画常开触点，返回底部 y
"""
import xml.etree.ElementTree as ET


class Ctx:
    """绘图上下文：持有 root 与 id 计数器，提供基础图元。"""
    def __init__(self, root, white="#FFFFFF", red="#FF0000", font="Noto Sans CJK SC"):
        self.root = root
        self._cid = [1]
        self.WHITE = white
        self.RED = red
        self.FONT = font

    def nid(self):
        self._cid[0] += 1
        return "s%d" % self._cid[0]

    def wire(self, x1, y1, x2, y2, color=None, w=3, dashed=False):
        color = color or self.WHITE
        s = "endArrow=none;html=1;strokeColor=%s;strokeWidth=%d;" % (color, w)
        if dashed:
            s += "dashed=1;dashPattern=10 7;"
        c = ET.SubElement(self.root, "mxCell", id=self.nid(), style=s, edge="1", parent="1")
        g = ET.SubElement(c, "mxGeometry", {"relative": "1", "as": "geometry"})
        ET.SubElement(g, "mxPoint", {"x": str(x1), "y": str(y1), "as": "sourcePoint"})
        ET.SubElement(g, "mxPoint", {"x": str(x2), "y": str(y2), "as": "targetPoint"})

    def dot(self, x, y, r=7, color=None):
        color = color or self.RED
        c = ET.SubElement(self.root, "mxCell", id=self.nid(),
                          style="ellipse;html=1;strokeColor=%s;fillColor=%s;" % (color, color),
                          vertex="1", parent="1")
        ET.SubElement(c, "mxGeometry", {"x": str(x - r), "y": str(y - r),
                                        "width": str(2 * r), "height": str(2 * r), "as": "geometry"})

    def rect(self, x, y, w, h, fill="none", stroke=None, sw=3):
        stroke = stroke or self.WHITE
        c = ET.SubElement(self.root, "mxCell", id=self.nid(),
                          style="rounded=0;html=1;strokeColor=%s;fillColor=%s;strokeWidth=%d;"
                                % (stroke, fill, sw),
                          vertex="1", parent="1")
        ET.SubElement(c, "mxGeometry", {"x": str(x), "y": str(y),
                                        "width": str(w), "height": str(h), "as": "geometry"})

    def ellipse(self, x, y, w, h, fill="none", stroke=None, sw=3):
        stroke = stroke or self.WHITE
        c = ET.SubElement(self.root, "mxCell", id=self.nid(),
                          style="ellipse;html=1;strokeColor=%s;fillColor=%s;strokeWidth=%d;"
                                % (stroke, fill, sw),
                          vertex="1", parent="1")
        ET.SubElement(c, "mxGeometry", {"x": str(x), "y": str(y),
                                        "width": str(w), "height": str(h), "as": "geometry"})

    def text(self, x, y, s, size=22, color=None):
        color = color or self.RED
        n_cjk = sum(1 for ch in s if ord(ch) > 127)
        n_asc = len(s) - n_cjk
        w = int(n_cjk * size * 1.0 + n_asc * size * 0.62 + 12)
        h = int(size * 1.45)
        style = ("text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;"
                 "fontColor=%s;fontSize=%d;fontFamily=%s;" % (color, size, self.FONT))
        c = ET.SubElement(self.root, "mxCell", id=self.nid(), value=s, style=style,
                          vertex="1", parent="1")
        ET.SubElement(c, "mxGeometry", {"x": str(x - w // 2), "y": str(y - h // 2),
                                        "width": str(w), "height": str(h), "as": "geometry"})

    def library_shape(self, x, y, w, h, shape, stroke=None, sw=3):
        """调 draw.io 自带库符号（style 名见 electrical-style-names.md）。"""
        stroke = stroke or self.WHITE
        c = ET.SubElement(self.root, "mxCell", id=self.nid(),
                          style="shape=%s;html=1;strokeColor=%s;strokeWidth=%d;fillColor=none;"
                                % (shape, stroke, sw),
                          vertex="1", parent="1")
        ET.SubElement(c, "mxGeometry", {"x": str(x), "y": str(y),
                                        "width": str(w), "height": str(h), "as": "geometry"})


# ================= 符号 =================
# 约定：垂直符号以顶部中心 (x, y_top) 为锚点，返回底部 y，便于串接。

def no_contact(ctx, x, y_top):
    """常开触点（垂直）"""
    ctx.wire(x, y_top, x, y_top + 16)
    ctx.wire(x, y_top + 16, x + 15, y_top + 36)
    ctx.wire(x, y_top + 36, x, y_top + 52)
    return y_top + 52

def nc_contact(ctx, x, y_top):
    """常闭触点（垂直）"""
    no_contact(ctx, x, y_top)
    ctx.wire(x - 7, y_top + 32, x + 11, y_top + 20)
    return y_top + 52

def coil(ctx, xc, y, w=64, h=28):
    """线圈（接触器/继电器）"""
    ctx.rect(xc - w // 2, y, w, h)

def thermal_relay(ctx, x, y, w=130, h=50):
    """热继电器 FR"""
    ctx.rect(x, y, w, h)
    yc = y + h // 2
    ctx.wire(x + 12, yc, x + w - 12, yc, dashed=True)
    ctx.rect(x + w // 4 - 12, yc - 9, 24, 18)
    ctx.rect(x + 3 * w // 4 - 12, yc - 9, 24, 18)

def motor_3ph(ctx, x, y, r=32):
    """三相电机 M"""
    ctx.ellipse(x - r, y - r, 2 * r, 2 * r)
    ctx.text(x, y + 2, "M", 30, ctx.WHITE)

def indicator_lamp(ctx, x, y, r=28):
    """指示灯（圆圈+叉）"""
    ctx.ellipse(x - r, y - r, 2 * r, 2 * r)
    d = int(r * 0.68)
    ctx.wire(x - d, y - d, x + d, y + d)
    ctx.wire(x - d, y + d, x + d, y - d)

def buzzer(ctx, x, y):
    """蜂鸣器"""
    ctx.ellipse(x - 18, y - 18, 36, 36)
    ctx.wire(x + 18, y - 11, x + 40, y - 20)
    ctx.wire(x + 18, y + 11, x + 40, y + 20)
    ctx.wire(x + 40, y - 20, x + 40, y + 20)

def selector_switch(ctx, x, y, r=16):
    """选择开关（旋转）"""
    ctx.ellipse(x - r, y - r, 2 * r, 2 * r)
    ctx.wire(x, y, x + 11, y - 11)
    ctx.dot(x, y, 3, ctx.WHITE)

def float_switch(ctx, x, y):
    """浮球开关触点"""
    ctx.ellipse(x - 13, y - 13, 26, 26)
    ctx.wire(x, y - 13, x + 22, y - 39)

def pushbutton(ctx, x, y):
    """按钮"""
    ctx.wire(x, y - 26, x, y - 12)
    ctx.wire(x, y + 12, x, y + 26)
    ctx.ellipse(x - 11, y - 11, 22, 22)
    ctx.wire(x - 15, y - 16, x + 15, y - 16)

def knife_switch(ctx, x, y):
    """刀开关（水平，支点在左）"""
    ctx.dot(x, y, 4, ctx.WHITE)
    ctx.wire(x, y, x + 42, y - 30)
    ctx.wire(x + 48, y, x + 48, y - 14)
    ctx.dot(x + 48, y - 7, 4, ctx.WHITE)

def fuse(ctx, x, y_top):
    """熔断器（垂直）"""
    ctx.wire(x, y_top, x, y_top + 14)
    ctx.rect(x - 8, y_top + 14, 16, 24)
    ctx.wire(x, y_top + 38, x, y_top + 52)
    return y_top + 52

def ground_pe(ctx, x, y):
    """保护接地（调库：mxgraph.electrical.signal_sources.protective_earth）"""
    ctx.library_shape(x - 20, y - 10, 40, 32,
                      "mxgraph.electrical.signal_sources.protective_earth")

def terminal_circle(ctx, x, y, r=8):
    """接线端子圆圈"""
    ctx.ellipse(x - r, y - r, 2 * r, 2 * r)
