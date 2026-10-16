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

def circuit_breaker(ctx, x, y_top):
    """断路器 QF（垂直）"""
    ctx.wire(x, y_top, x, y_top + 16)
    ctx.wire(x - 9, y_top + 22, x + 9, y_top + 40)
    ctx.wire(x - 9, y_top + 40, x + 9, y_top + 22)
    ctx.wire(x, y_top + 46, x, y_top + 62)
    return y_top + 62

def disconnector(ctx, x, y_top):
    """隔离开关 QS（垂直，带圆点铰链）"""
    ctx.wire(x, y_top, x, y_top + 14)
    ctx.dot(x, y_top + 18, 4, ctx.WHITE)
    ctx.wire(x, y_top + 18, x + 16, y_top + 40)
    ctx.wire(x, y_top + 44, x, y_top + 60)
    return y_top + 60

def emergency_stop(ctx, x, y):
    """急停按钮（蘑菇头），y 为中心"""
    ctx.wire(x, y - 30, x, y - 8)
    ctx.ellipse(x - 15, y - 8, 30, 14)
    ctx.wire(x, y + 6, x, y + 30)

def limit_switch(ctx, x, y_top):
    """限位开关 SQ（垂直，滚轮）"""
    ctx.wire(x, y_top, x, y_top + 16)
    ctx.wire(x, y_top + 16, x + 15, y_top + 36)
    ctx.ellipse(x + 11, y_top + 30, 12, 12)
    ctx.wire(x, y_top + 40, x, y_top + 56)
    return y_top + 56

def current_transformer(ctx, x, y):
    """电流互感器 TA（两交叠圆），(x,y) 为中心"""
    ctx.ellipse(x - 24, y - 16, 32, 32)
    ctx.ellipse(x - 8, y - 16, 32, 32)

def ammeter(ctx, x, y, r=28):
    """电流表 A"""
    ctx.ellipse(x - r, y - r, 2 * r, 2 * r)
    ctx.text(x, y + 2, "A", 30, ctx.WHITE)

def voltmeter(ctx, x, y, r=28):
    """电压表 V"""
    ctx.ellipse(x - r, y - r, 2 * r, 2 * r)
    ctx.text(x, y + 2, "V", 30, ctx.WHITE)

def surge_arrester(ctx, x, y_top):
    """避雷器（垂直）"""
    ctx.wire(x, y_top, x, y_top + 12)
    ctx.rect(x - 10, y_top + 12, 20, 28)
    ctx.wire(x - 10, y_top + 40, x + 10, y_top + 12)
    ctx.wire(x + 6, y_top + 16, x + 10, y_top + 12)
    ctx.wire(x + 2, y_top + 20, x + 10, y_top + 12)
    ctx.wire(x, y_top + 40, x, y_top + 56)
    return y_top + 56

def time_delay_no(ctx, x, y_top):
    """通电延时常开触点 KT（垂直）"""
    no_contact(ctx, x, y_top)
    ctx.wire(x - 12, y_top + 8, x - 12, y_top + 24)
    ctx.wire(x - 12, y_top + 8, x + 12, y_top + 8)
    return y_top + 52

def solenoid(ctx, x, y):
    """电磁铁/电磁阀线圈（方框+斜箭头），(x,y) 为中心"""
    ctx.rect(x - 20, y - 14, 40, 28)
    ctx.wire(x - 20, y + 14, x + 20, y - 14)
    ctx.wire(x + 12, y - 10, x + 20, y - 14)
    ctx.wire(x + 16, y - 4, x + 20, y - 14)
