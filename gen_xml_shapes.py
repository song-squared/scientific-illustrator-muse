#!/usr/bin/env python3
"""录制 iec_symbols.py 的绘图原语，生成 draw.io stencil XML。

保证 Python 库与 XML 库 1:1 一致，新增符号只需写 Python 函数，
在这里加一行 spec 即可。用法：python3 gen_xml_shapes.py >> 输出片段
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iec_symbols as S


class RecCtx:
    """只记录、不落盘的绘图上下文。"""
    WHITE = "#FFFFFF"
    RED = "#FF0000"

    def __init__(self):
        self.ops = []
        self.minx = self.miny = 1e9
        self.maxx = self.maxy = -1e9

    def _box(self, x1, y1, x2, y2):
        self.minx = min(self.minx, x1, x2)
        self.maxx = max(self.maxx, x1, x2)
        self.miny = min(self.miny, y1, y2)
        self.maxy = max(self.maxy, y1, y2)

    def wire(self, x1, y1, x2, y2, color=None, w=3, dashed=False):
        self.ops.append(("wire", x1, y1, x2, y2, w, dashed))
        self._box(x1, y1, x2, y2)

    def dot(self, x, y, r=7, color=None):
        self.ops.append(("dot", x, y, r))
        self._box(x - r, y - r, x + r, y + r)

    def rect(self, x, y, w, h, fill="none", stroke=None, sw=3):
        self.ops.append(("rect", x, y, w, h, sw))
        self._box(x, y, x + w, y + h)

    def ellipse(self, x, y, w, h, fill="none", stroke=None, sw=3):
        self.ops.append(("ellipse", x, y, w, h, sw))
        self._box(x, y, x + w, y + h)

    def text(self, x, y, s, size=22, color=None):
        self.ops.append(("text", x, y, s, size))
        n_cjk = sum(1 for ch in s if ord(ch) > 127)
        n_asc = len(s) - n_cjk
        w = n_cjk * size * 1.0 + n_asc * size * 0.62 + 12
        h = size * 1.45
        self._box(x - w / 2, y - h / 2, x + w / 2, y + h / 2)

    def library_shape(self, x, y, w, h, shape, stroke=None, sw=3):
        pass  # 自带库符号不进自建 XML


def R(v):
    s = round(v, 1)
    return int(s) if s == int(s) else s


def shape_xml(name, rec, connections, aspect="variable"):
    w = rec.maxx - rec.minx
    h = rec.maxy - rec.miny
    ox, oy = -rec.minx, -rec.miny
    L = [f'  <!-- {name}（自动生成） -->',
         f'  <shape name="{name}" aspect="{aspect}" w="{R(w)}" h="{R(h)}" strokewidth="inherit">',
         '    <connections>']
    for cx, cy in connections:
        L.append(f'      <constraint x="{cx}" y="{cy}"/>')
    L.append('    </connections>')
    L.append('    <foreground>')
    cur_sw = None
    for op in rec.ops:
        k = op[0]
        sw = op[5] if k == "wire" else (op[5] if k in ("rect", "ellipse") else 2)
        sw = 2 if sw >= 2 else 1
        if sw != cur_sw:
            L.append(f'      <strokewidth width="{sw}"/>')
            cur_sw = sw
        if k == "wire":
            _, x1, y1, x2, y2, _, dashed = op
            if dashed:
                L.append('      <dashed dashed="1" fixDash="1"/>')
                L.append('      <dashpattern pattern="8 6"/>')
            L.append(f'      <path><move x="{R(x1+ox)}" y="{R(y1+oy)}"/><line x="{R(x2+ox)}" y="{R(y2+oy)}"/></path>')
            L.append('      <stroke/>')
            if dashed:
                L.append('      <dashed dashed="0"/>')
        elif k == "rect":
            _, x, y, w_, h_, _ = op
            L.append(f'      <rect x="{R(x+ox)}" y="{R(y+oy)}" w="{R(w_)}" h="{R(h_)}"/>')
            L.append('      <stroke/>')
        elif k == "ellipse":
            _, x, y, w_, h_, _ = op
            L.append(f'      <ellipse x="{R(x+ox)}" y="{R(y+oy)}" w="{R(w_)}" h="{R(h_)}"/>')
            L.append('      <stroke/>')
        elif k == "dot":
            _, x, y, rr = op
            L.append(f'      <ellipse x="{R(x-rr+ox)}" y="{R(y-rr+oy)}" w="{R(2*rr)}" h="{R(2*rr)}"/>')
            L.append('      <fillstroke/>')
        elif k == "text":
            _, x, y, s, size = op
            L.append(f'      <text str="{s}" x="{R(x+ox)}" y="{R(y+oy)}" align="center" valign="middle" fontsize="{size}"/>')
            L.append('      <stroke/>')
    L.append('    </foreground>')
    L.append('  </shape>')
    return "\n".join(L), R(w), R(h)


# (name, 绘制调用, 连接点[(x,y)分数], aspect)
SPECS = [
    ("contactor_main_contact", lambda c: S.contactor_main_contact(c, 100, 100),
     [(0.17, 0), (0.5, 0), (0.83, 0), (0.17, 1), (0.5, 1), (0.83, 1)], "variable"),
    ("spdt_switch", lambda c: S.spdt_switch(c, 100, 100),
     [(0, 0), (1, 0), (0.5, 1)], "variable"),
    ("time_relay_coil", lambda c: S.time_relay_coil(c, 100, 100),
     [(0, 0.5), (1, 0.5)], "variable"),
    ("dpdt_switch", lambda c: S.dpdt_switch(c, 100, 100),
     [(0.03, 0), (0.97, 0), (0.23, 1), (0.77, 1)], "variable"),
    ("load_break_switch", lambda c: S.load_break_switch(c, 100, 100),
     [(0.28, 0), (0.28, 1)], "variable"),
    ("fuse_disconnector", lambda c: S.fuse_disconnector(c, 100, 100),
     [(0.5, 0), (0.5, 1)], "variable"),
    ("earthing_switch", lambda c: S.earthing_switch(c, 100, 100),
     [(0.42, 0)], "variable"),
    ("proximity_switch", lambda c: S.proximity_switch(c, 100, 100),
     [(0, 0.5), (1, 0.5)], "fixed"),
    ("pressure_switch", lambda c: S.pressure_switch(c, 100, 100),
     [(0.5, 0), (0.5, 1)], "variable"),
    ("temperature_switch", lambda c: S.temperature_switch(c, 100, 100),
     [(0.5, 0), (0.5, 1)], "variable"),
    ("foot_switch", lambda c: S.foot_switch(c, 100, 100),
     [(0.5, 0), (0.5, 1)], "variable"),
    ("rcd", lambda c: S.rcd(c, 100, 100),
     [(0.32, 0), (0.32, 1)], "variable"),
    ("motor_protector", lambda c: S.motor_protector(c, 100, 100),
     [(0, 0.5), (1, 0.5)], "variable"),
    ("ats", lambda c: S.ats(c, 100, 100),
     [(0.17, 0), (0.83, 0), (0.5, 1)], "variable"),
    ("time_delay_nc", lambda c: S.time_delay_nc(c, 100, 100),
     [(0.64, 0), (0.64, 1)], "variable"),
    ("voltage_transformer", lambda c: S.voltage_transformer(c, 100, 100),
     [(0.5, 0), (0.5, 1)], "fixed"),
    ("energy_meter", lambda c: S.energy_meter(c, 100, 100),
     [(0.5, 0), (0.5, 1)], "fixed"),
    ("power_meter", lambda c: S.power_meter(c, 100, 100),
     [(0.5, 0), (0.5, 1)], "fixed"),
    ("frequency_meter", lambda c: S.frequency_meter(c, 100, 100),
     [(0.5, 0), (0.5, 1)], "fixed"),
    ("dc_motor", lambda c: S.dc_motor(c, 100, 100),
     [(0.5, 0), (0.5, 1)], "fixed"),
    ("transformer_2w", lambda c: S.transformer_2w(c, 100, 100),
     [(0.5, 0), (0.5, 1)], "fixed"),
]


def main():
    out = []
    for name, fn, conns, aspect in SPECS:
        rec = RecCtx()
        fn(rec)
        xml, w, h = shape_xml(name, rec, conns, aspect)
        out.append(xml)
        print(f"<!-- {name}: {w}x{h} -->", file=sys.stderr)
    print("\n".join(out))


if __name__ == "__main__":
    main()
