# QUICKSTART

[English](QUICKSTART-en.md) | [中文](QUICKSTART.md)

三步跑通第一张图。面向第一次用本项目的 Muse（或任何 AI agent）。

## 前提

- Linux（Ubuntu 22.04/24.04 实测过）
- Node.js 18+
- Python 3 + pillow（`pip install pillow`）

## 第一步：安装

```bash
git clone https://github.com/song-squared/scientific-illustrator-muse.git
cd scientific-illustrator-muse
./setup.sh
```

`setup.sh` 会装：Xvfb、draw.io Desktop 32.4.1、系统依赖。
装完验证：

```bash
ls /opt/drawio/drawio && echo OK
```

> VM 重置 / 环境丢了？跑 `./setup.sh check` 快速自检，缺什么补什么。
> 依赖包已缓存在 `deps/`，不用重新下载。

## 第二步：画第一张图（直接写 XML）

最快路线：手写 `.drawio` XML，一句话导出。不用 live 模式。

```python
# hello.py
xml = '''<mxfile><diagram name="Page-1"><mxGraphModel><root>
<mxCell id="0"/><mxCell id="1" parent="0"/>
<mxCell id="box1" parent="1" value="Hello"
  style="rounded=1;fillColor=#D5E8D4;strokeColor=#82B366;fontSize=14;"
  vertex="1">
  <mxGeometry x="100" y="80" width="160" height="60" as="geometry"/>
</mxCell>
</root></mxGraphModel></diagram></mxfile>'''
open('hello.drawio', 'w').write(xml)
print("written")
```

```bash
python3 hello.py
```

## 第三步：导出 PNG

```bash
printf '%s\n' \
  '{"id":1,"tool":"drawio_export","arguments":{"input_path":"'$(pwd)'/hello.drawio","format":"png","output_path":"'$(pwd)'/hello.png","width":800,"overwrite":true}}' \
  | ./mcp-call.sh file
```

看到 `ok: true` 后，`hello.png` 就是成品。

## 下一步

- 读 `SKILL.md` 5.7（重绘检查清单：颜色/布局/3D-2D风格/文字）
- 读 `SKILL.md` 5.8（图片缓存：每次交付用新文件名，带时间戳）
- 图标走 AI 生成 + base64 嵌入，见 `SKILL.md` 5.4
- 3D 组件走 AI 生成 + 紧凑裁白边，见 `SKILL.md` 5.5

## 常见坑

| 现象 | 原因 | 解法 |
|---|---|---|
| `Output already exists` | 没传 `overwrite:true` | export 参数加 `"overwrite":true` |
| 导出空白图 | XML 里有未转义的 `<`/`&` | Python 里先 `esc()` 转义，写完用 `ET.fromstring` 校验 |
| 图片不显示 | style 里用了 `;base64` | data URI 不要分号：`data:image/png,BASE64` |
| 用户看到旧图 | 客户端缓存 | 换新文件名（带时间戳），不要覆盖 |
| `graph is not ready` | live 实例启动慢 | 等几秒重试 |

## 环境变量

| 变量 | 默认 | 说明 |
|---|---|---|
| `MUSE_DRAWIO_HOME` | 脚本所在目录 | 项目根目录 |
| `DISPLAY_NUM` | `99` | Xvfb 显示号 |
