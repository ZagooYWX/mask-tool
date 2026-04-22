#!/bin/bash
# mask-tool 启动脚本 (macOS)
# 双击此文件即可启动 Web 界面

cd "$(dirname "$0")"

if [ ! -f "pyproject.toml" ]; then
    echo "错误：请在 mask-tool 项目目录中运行此脚本"
    read -p "按回车键退出..."
    exit 1
fi

# 激活虚拟环境（如果存在）
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

echo "正在启动 mask-tool..."
echo "浏览器会自动打开 http://localhost:8501"
echo "关闭此终端窗口即可停止服务"
echo ""

streamlit run src/mask_tool/web/app.py --server.port 8501
