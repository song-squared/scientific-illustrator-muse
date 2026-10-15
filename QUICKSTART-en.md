# QUICKSTART

[English](QUICKSTART-en.md) | [中文](QUICKSTART.md)

Get your first diagram done in three steps. Written for a Muse (or any AI agent) using this project for the first time.

## Prerequisites

- Linux (tested on Ubuntu 22.04/24.04)
- Node.js 18+
- Python 3 + pillow (`pip install pillow`)

## Step 1: Install

```bash
git clone https://github.com/song-squared/scientific-illustrator-muse.git
cd scientific-illustrator-muse
./setup.sh
```

`setup.sh` installs: Xvfb, draw.io Desktop 32.4.1, and system dependencies.
Verify after install:

```bash
ls /opt/drawio/drawio && echo OK
```

> VM reset / environment lost? Run `./setup.sh check` for a quick self-check — it installs whatever is missing.
> Dependency packages are cached in `deps/`, no need to download them again.

## Step 2: Draw your first diagram (write XML directly)

The fastest path: hand-write `.drawio` XML, then export with one command. No live mode needed.

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

## Step 3: Export to PNG

```bash
printf '%s\n' \
  '{"id":1,"tool":"drawio_export","arguments":{"input_path":"'$(pwd)'/hello.drawio","format":"png","output_path":"'$(pwd)'/hello.png","width":800,"overwrite":true}}' \
  | ./mcp-call.sh file
```

Once you see `ok: true`, `hello.png` is your finished product.

## Next steps

- Read `SKILL.md` 5.7 (redraw checklist: colors / layout / 3D-2D style / text)
- Read `SKILL.md` 5.8 (image caching: use a fresh filename with a timestamp for every delivery)
- Icons: AI-generate + base64-embed, see `SKILL.md` 5.4
- 3D components: AI-generate + tight whitespace-crop, see `SKILL.md` 5.5

## Common pitfalls

| Symptom | Cause | Fix |
|---|---|---|
| `Output already exists` | Missing `overwrite:true` | Add `"overwrite":true` to the export parameters |
| Blank export | Unescaped `<`/`&` in the XML | Escape with `esc()` in Python first, then validate with `ET.fromstring` |
| Image not showing | Used `;base64` in style | No semicolon in data URIs: `data:image/png,BASE64` |
| User sees an old image | Client cache | Use a new filename (with timestamp), never overwrite |
| `graph is not ready` | Live instance is slow to start | Wait a few seconds and retry |

## Environment variables

| Variable | Default | Description |
|---|---|---|
| `MUSE_DRAWIO_HOME` | Directory containing the scripts | Project root |
| `DISPLAY_NUM` | `99` | Xvfb display number |
