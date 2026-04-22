#!/bin/bash
# ============================================================
#  mask-tool 一键安装脚本 (macOS)
#  用法：双击 install-mac.command 或在终端中运行
# ============================================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo ""
echo "============================================"
echo "   🔒 mask-tool 文件脱敏工具 - 安装程序"
echo "============================================"
echo ""

# 获取脚本所在目录（无论从哪里运行都能正确定位）
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# 1. 检查 Python3
echo "📦 [1/4] 检查 Python3..."
if command -v python3 &> /dev/null; then
    PYTHON=python3
    PY_VERSION=$(python3 --version 2>&1)
    echo -e "  ${GREEN}✓${NC} 找到 $PY_VERSION"
elif command -v python &> /dev/null; then
    PYTHON=python
    PY_VERSION=$(python --version 2>&1)
    echo -e "  ${GREEN}✓${NC} 找到 $PY_VERSION"
else
    echo -e "  ${RED}✗${NC} 未找到 Python3"
    echo ""
    echo "  请先安装 Python 3.9+："
    echo "  1. 访问 https://www.python.org/downloads/"
    echo "  2. 下载 macOS 安装包并安装"
    echo "  3. 重新运行此脚本"
    echo ""
    read -p "按回车键退出..."
    exit 1
fi

# 检查 Python 版本 >= 3.8
PY_MAJOR=$($PYTHON -c "import sys; print(sys.version_info.major)")
PY_MINOR=$($PYTHON -c "import sys; print(sys.version_info.minor)")
if [ "$PY_MAJOR" -lt 3 ] || ([ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -lt 8 ]); then
    echo -e "  ${RED}✗${NC} Python 版本过低（需要 3.8+，当前 $PY_MAJOR.$PY_MINOR）"
    read -p "按回车键退出..."
    exit 1
fi

# 2. 创建虚拟环境
echo ""
echo "📦 [2/4] 创建虚拟环境..."
if [ -d ".venv" ]; then
    echo -e "  ${YELLOW}!${NC} 虚拟环境已存在，跳过创建"
else
    $PYTHON -m venv .venv
    echo -e "  ${GREEN}✓${NC} 虚拟环境创建成功"
fi

# 激活虚拟环境
source .venv/bin/activate

# 3. 安装依赖
echo ""
echo "📦 [3/4] 安装依赖（可能需要几分钟）..."
pip install --upgrade pip --quiet 2>/dev/null
pip install -e ".[web]" --quiet 2>/dev/null
if [ $? -eq 0 ]; then
    echo -e "  ${GREEN}✓${NC} 依赖安装成功"
else
    echo -e "  ${YELLOW}!${NC} 部分依赖安装失败，尝试重新安装..."
    pip install -e ".[web]"
fi

# 4. 初始化用户词库
echo ""
echo "📦 [4/4] 初始化配置..."
if [ ! -f "config/lexicon.yaml" ] && [ -f "config/sample_lexicon.yaml" ]; then
    cp config/sample_lexicon.yaml config/lexicon.yaml
    echo -e "  ${GREEN}✓${NC} 已创建用户词库 config/lexicon.yaml"
else
    echo -e "  ${GREEN}✓${NC} 配置已就绪"
fi

# 创建历史目录
mkdir -p ~/.mask-tool

# 创建桌面启动脚本
echo ""
echo "🚀 创建桌面快捷方式..."
DESKTOP_DIR="$HOME/Desktop"
START_SCRIPT="$DESKTOP_DIR/mask-tool启动.command"

cat > "$START_SCRIPT" << 'STARTSCRIPT'
#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# 如果从桌面运行，尝试定位到项目目录
if [ -f "$SCRIPT_DIR/mask-tool启动.command" ]; then
    # 查找 mask-tool 项目目录
    for search_dir in "$HOME/Documents" "$HOME/Desktop" "$HOME/projects" "$HOME"; do
        if [ -d "$search_dir/TRAE SOLO PROJECTS/mask-tool" ]; then
            cd "$search_dir/TRAE SOLO PROJECTS/mask-tool"
            break
        fi
        if [ -d "$search_dir/mask-tool" ]; then
            cd "$search_dir/mask-tool"
            break
        fi
    done
fi
if [ ! -f "pyproject.toml" ]; then
    echo "错误：找不到 mask-tool 项目目录"
    echo "请将此脚本放在 mask-tool 项目目录中运行"
    read -p "按回车键退出..."
    exit 1
fi
source .venv/bin/activate
echo "正在启动 mask-tool..."
echo "启动后浏览器会自动打开，关闭浏览器即停止服务"
echo ""
streamlit run src/mask_tool/web/app.py --server.port 8501
STARTSCRIPT

chmod +x "$START_SCRIPT"
echo -e "  ${GREEN}✓${NC} 桌面快捷方式已创建：$START_SCRIPT"

# 完成
echo ""
echo "============================================"
echo -e "  ${GREEN}✅ 安装完成！${NC}"
echo "============================================"
echo ""
echo "  使用方式："
echo "  1. 双击桌面上的「mask-tool启动.command」"
echo "  2. 浏览器会自动打开 http://localhost:8501"
echo "  3. 关闭终端窗口即可停止服务"
echo ""
echo "  如需卸载，删除项目文件夹即可。"
echo ""
read -p "按回车键退出..."
