#!/usr/bin/env python3
"""IEC 60617 符号库展示图：14 个符号一字排开。"""
import xml.etree.ElementTree as ET
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from iec_symbols import (Ctx, no_contact, nc_contact, coil, thermal_relay,
                         motor_3ph, indicator_lamp, buzzer, selector_switch,
                         float_switch, pushbutton, knife_switch, fuse,
                         ground_pe, terminal_circle, circuit_breaker,
                         disconnector, emergency_stop, limit_switch,
                         current_transformer, ammeter, voltmeter,
                         surge_arrester, time_delay_no, solenoid,
                         contactor_main_contact, spdt_switch, time_relay_coil,
                         dpdt_switch, load_break_switch, fuse_disconnector,
                         earthing_switch, proximity_switch, pressure_switch,
                         temperature_switch, foot_switch, rcd, motor_protector,
                         ats, time_delay_nc, voltage_transformer, energy_meter,
                         power_meter, frequency_meter, dc_motor, transformer_2w)

W, H = 1400, 2900
OUT_DIR = os.path.expanduser("~/workspace/goals/muse-draw-io-scientific-illustrator-port/files/scientific-illustrator-muse")

mxfile = ET.Element("mxfile", host="muse", type="device")
diagram = ET.SubElement(mxfile, "diagram", id="symbols-show", name="Page-1")
model = ET.SubElement(diagram, "mxGraphModel", pageWidth=str(W), pageHeight=str(H))
root = ET.SubElement(model, "root")
ET.SubElement(root, "mxCell", id="0")
ET.SubElement(root, "mxCell", id="1", parent="0")
ctx = Ctx(root)
ctx.rect(0, 0, W, H, fill="#000000", stroke="#000000", sw=1)
ctx.text(W // 2, 50, "IEC 60617 电气符号库（自建 45 符号）", 40)

# (名称, 绘制函数)
symbols = [
    ("常开触点 no_contact", lambda cx, cy: no_contact(ctx, cx, cy - 26)),
    ("常闭触点 nc_contact", lambda cx, cy: nc_contact(ctx, cx, cy - 26)),
    ("线圈 coil", lambda cx, cy: coil(ctx, cx, cy - 14)),
    ("热继电器 thermal_relay", lambda cx, cy: thermal_relay(ctx, cx - 65, cy - 25)),
    ("三相电机 motor_3ph", lambda cx, cy: motor_3ph(ctx, cx, cy)),
    ("指示灯 indicator_lamp", lambda cx, cy: indicator_lamp(ctx, cx, cy)),
    ("蜂鸣器 buzzer", lambda cx, cy: buzzer(ctx, cx - 10, cy)),
    ("选择开关 selector_switch", lambda cx, cy: selector_switch(ctx, cx, cy)),
    ("浮球开关 float_switch", lambda cx, cy: float_switch(ctx, cx - 5, cy + 5)),
    ("按钮 pushbutton", lambda cx, cy: pushbutton(ctx, cx, cy)),
    ("刀开关 knife_switch", lambda cx, cy: knife_switch(ctx, cx - 25, cy + 5)),
    ("熔断器 fuse", lambda cx, cy: fuse(ctx, cx, cy - 26)),
    ("保护接地 ground_pe（调自带库）", lambda cx, cy: ground_pe(ctx, cx, cy)),
    ("端子 terminal", lambda cx, cy: terminal_circle(ctx, cx, cy)),
    ("断路器 circuit_breaker", lambda cx, cy: circuit_breaker(ctx, cx, cy - 31)),
    ("隔离开关 disconnector", lambda cx, cy: disconnector(ctx, cx, cy - 30)),
    ("急停按钮 emergency_stop", lambda cx, cy: emergency_stop(ctx, cx, cy)),
    ("限位开关 limit_switch", lambda cx, cy: limit_switch(ctx, cx, cy - 28)),
    ("电流互感器 current_transformer", lambda cx, cy: current_transformer(ctx, cx, cy)),
    ("电流表 ammeter", lambda cx, cy: ammeter(ctx, cx, cy)),
    ("电压表 voltmeter", lambda cx, cy: voltmeter(ctx, cx, cy)),
    ("避雷器 surge_arrester", lambda cx, cy: surge_arrester(ctx, cx, cy - 28)),
    ("延时常开 time_delay_no", lambda cx, cy: time_delay_no(ctx, cx, cy - 26)),
    ("电磁铁 solenoid", lambda cx, cy: solenoid(ctx, cx, cy)),
    ("接触器主触点 contactor_main", lambda cx, cy: contactor_main_contact(ctx, cx - 40, cy - 26)),
    ("单刀双掷 spdt_switch", lambda cx, cy: spdt_switch(ctx, cx, cy)),
    ("时间继电器线圈 time_relay_coil", lambda cx, cy: time_relay_coil(ctx, cx, cy)),
    ("双刀双掷 dpdt_switch", lambda cx, cy: dpdt_switch(ctx, cx, cy)),
    ("负荷开关 load_break_switch", lambda cx, cy: load_break_switch(ctx, cx, cy - 30)),
    ("熔断器式隔离开关 fuse_disconnector", lambda cx, cy: fuse_disconnector(ctx, cx, cy - 27)),
    ("接地开关 earthing_switch", lambda cx, cy: earthing_switch(ctx, cx - 4, cy - 26)),
    ("接近开关 proximity_switch", lambda cx, cy: proximity_switch(ctx, cx, cy)),
    ("压力开关 pressure_switch", lambda cx, cy: pressure_switch(ctx, cx, cy - 28)),
    ("温度开关 temperature_switch", lambda cx, cy: temperature_switch(ctx, cx, cy - 26)),
    ("脚踏开关 foot_switch", lambda cx, cy: foot_switch(ctx, cx, cy - 27)),
    ("漏电保护器 rcd", lambda cx, cy: rcd(ctx, cx - 5, cy - 31)),
    ("电动机保护器 motor_protector", lambda cx, cy: motor_protector(ctx, cx, cy)),
    ("双电源切换 ats", lambda cx, cy: ats(ctx, cx, cy)),
    ("断电延时常闭 time_delay_nc", lambda cx, cy: time_delay_nc(ctx, cx, cy - 26)),
    ("电压互感器 voltage_transformer", lambda cx, cy: voltage_transformer(ctx, cx, cy)),
    ("电能表 energy_meter", lambda cx, cy: energy_meter(ctx, cx, cy)),
    ("功率表 power_meter", lambda cx, cy: power_meter(ctx, cx, cy)),
    ("频率表 frequency_meter", lambda cx, cy: frequency_meter(ctx, cx, cy)),
    ("直流电机 dc_motor", lambda cx, cy: dc_motor(ctx, cx, cy)),
    ("双绕组变压器 transformer_2w", lambda cx, cy: transformer_2w(ctx, cx, cy)),
]

COLS = 4
CW, CH = W // COLS, 230
assert len(symbols) == 45, len(symbols)

COLS = 4
CW, CH = W // COLS, 230
for i, (name, fn) in enumerate(symbols):
    col, row = i % COLS, i // COLS
    cx = col * CW + CW // 2
    cy = 130 + row * CH + 80
    # 分隔线
    if col > 0:
        ctx.wire(col * CW, 110, col * CW, 110 + 4 * CH, color="#333333", w=1)
    fn(cx, cy)
    ctx.text(cx, cy + 95, name, 20)

p = os.path.join(OUT_DIR, "iec60617-符号展示-v4.drawio")
with open(p, "w", encoding="utf-8") as f:
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    f.write(ET.tostring(mxfile, encoding="unicode"))
print("drawio:", p)
