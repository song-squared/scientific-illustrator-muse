#!/bin/bash
# setup.sh - scientific-illustrator-muse 环境初始化与自检
# 用法:
#   ./setup.sh          # 完整安装
#   ./setup.sh check    # 快速自检：缺什么补什么（VM 重置后跑这个）
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DEPS_DIR="${SCRIPT_DIR}/deps"
DRAWIO_VERSION="32.4.1"
DRAWIO_DEB="drawio-${DRAWIO_VERSION}.deb"
DRAWIO_URL="https://github.com/jgraph/drawio-desktop/releases/download/v${DRAWIO_VERSION}/drawio-amd64-${DRAWIO_VERSION}.deb"

MODE="${1:-install}"

need_drawio() { [ ! -x "/opt/drawio/drawio" ]; }
need_xvfb() { ! which Xvfb >/dev/null 2>&1; }
need_pil() { ! python3 -c "import PIL" 2>/dev/null; }

install_cached_deps() {
    # 优先用 deps/ 目录里的本地包，不用重新下载
    local missing=0
    for deb in "${DEPS_DIR}"/*.deb; do
        [ -f "$deb" ] || continue
        local pkg
        pkg=$(dpkg-deb -f "$deb" Package 2>/dev/null)
        if ! dpkg -s "$pkg" >/dev/null 2>&1; then
            echo "  补装 ${pkg}（本地缓存）..."
            sudo dpkg -i "$deb" 2>&1 | tail -1 || missing=1
        fi
    done
    return $missing
}

install_drawio() {
    if [ ! -f "${SCRIPT_DIR}/${DRAWIO_DEB}" ]; then
        echo "下载 draw.io ${DRAWIO_VERSION}..."
        curl -L -o "${SCRIPT_DIR}/${DRAWIO_DEB}" "${DRAWIO_URL}"
    fi
    echo "安装 draw.io..."
    install_cached_deps || true
    sudo dpkg -i "${SCRIPT_DIR}/${DRAWIO_DEB}" 2>&1 | tail -2 || true
    # 还缺依赖才走 apt（可能卡，尽量避免）
    if need_drawio; then
        echo "尝试 apt 修复依赖..."
        sudo apt-get update -qq 2>&1 | tail -1 || true
        sudo apt-get install -f -y -qq 2>&1 | tail -2 || true
    fi
}

do_check() {
    local fixed=0
    echo "=== 环境自检 ==="
    if need_xvfb; then
        echo "✗ Xvfb 缺失，安装..."
        sudo apt-get install -y -qq xvfb 2>&1 | tail -1 || true
        fixed=1
    else echo "✓ Xvfb"; fi

    if need_drawio; then
        echo "✗ draw.io 缺失（可能 VM 重置），重装..."
        install_drawio
        fixed=1
    else echo "✓ draw.io"; fi

    if need_pil; then
        echo "✗ PIL 缺失，安装..."
        pip install -q pillow 2>&1 | tail -1 || true
        fixed=1
    else echo "✓ PIL"; fi

    which python3 >/dev/null && echo "✓ python3" || echo "✗ python3 缺失"
    which node >/dev/null && echo "✓ node" || echo "✗ node 缺失"

    if need_drawio; then
        echo ""; echo "✗ 自检后 draw.io 仍缺失，请手动排查"
        return 1
    fi
    [ "$fixed" = "1" ] && echo "" && echo "已修复缺失组件 ✓" || echo "" && echo "环境完好，无需修复 ✓"
}

do_install() {
    echo "=== 1. 安装系统依赖 ==="
    install_cached_deps || true
    # 本地缓存装完还缺的，才走 apt
    for pkg in xvfb libnss3 libxss1 libasound2; do
        dpkg -s "$pkg" >/dev/null 2>&1 || {
            echo "apt 安装 $pkg..."
            sudo apt-get update -qq 2>&1 | tail -1 || true
            sudo apt-get install -y -qq "$pkg" 2>&1 | tail -1 || true
        }
    done

    echo "=== 2. 安装 draw.io Desktop ==="
    if need_drawio; then install_drawio; else echo "draw.io 已安装，跳过"; fi

    echo "=== 3. 验证 ==="
    do_check
    echo ""
    echo "=== 完成 ==="
    echo "mcp-call.sh 会自动启动 Xvfb，直接用即可。"
}

case "$MODE" in
    check) do_check ;;
    install) do_install ;;
    *) echo "用法: $0 [install|check]" >&2; exit 2 ;;
esac
