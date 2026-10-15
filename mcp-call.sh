#!/bin/bash
# mcp-call.sh — Muse 版 scientific-illustrator 的批量调用入口
#
# 用法:
#   ./mcp-call.sh live < calls.jsonl     # 调 drawio-live (实时画布)
#   ./mcp-call.sh file < calls.jsonl     # 调 drawio-file-utils (校验/导出)
#
# 输入: 每行一个 JSON:
#   {"id":1,"tool":"drawio_live_launch","arguments":{}}
#   {"id":2,"method":"tools/list"}
# 输出: 每行一个 JSON:
#   {"id":1,"ok":true,"text":"...","structured":{...},"images":["/path/shot.png"]}
# 截图自动落盘到 ./shots/, 只返回路径。
#
# 注意: 画布会话保存在 server 进程内, 一次 mcp-call.sh 调用 = 一个会话。
# 需要跨多次调用保持同一画布时, 用后台常驻垫片 (见 SKILL.md)。
#
# 环境变量:
#   MUSE_DRAWIO_HOME - 项目根目录 (默认: 脚本所在目录)
#   DISPLAY_NUM      - Xvfb 显示号 (默认: 99)

set -u
MODE="${1:-live}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
MUSE_DRAWIO_HOME="${MUSE_DRAWIO_HOME:-$SCRIPT_DIR}"
DISPLAY_NUM="${DISPLAY_NUM:-99}"

ROOT="$MUSE_DRAWIO_HOME/scripts"
case "$MODE" in
  live) SERVER="$ROOT/live-server.mjs" ;;
  file) SERVER="$ROOT/server.mjs" ;;
  *) echo "usage: $0 [live|file] < calls.jsonl" >&2; exit 2 ;;
esac

# 虚拟显示必须在跑 (draw.io 是 Electron 应用, 无显示器无法启动)
if ! ps aux | grep -q "[X]vfb :${DISPLAY_NUM}"; then
  Xvfb :${DISPLAY_NUM} -screen 0 1920x1080x24 >/tmp/xvfb-${DISPLAY_NUM}.log 2>&1 &
  sleep 2
fi

export DISPLAY=:${DISPLAY_NUM}
export DRAWIO_PATH="$MUSE_DRAWIO_HOME/drawio-ns.sh"

if [ ! -x "$DRAWIO_PATH" ]; then
  echo '{"id":null,"ok":false,"error":"DRAWIO_PATH wrapper missing: '"$DRAWIO_PATH"'"}'
  exit 1
fi

timeout 280 node "$MUSE_DRAWIO_HOME/mcp-shim.mjs" "$SERVER" 2>/tmp/mcp-call.err
