@echo off
chcp 65001 >nul 2>&1
title mask-tool 文件脱敏工具

cd /d "%~dp0"

if not exist "pyproject.toml" (
    echo 错误：请在 mask-tool 项目目录中运行此脚本
    pause
    exit /b 1
)

:: 激活虚拟环境（如果存在）
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
)

echo 正在启动 mask-tool...
echo 浏览器会自动打开 http://localhost:8501
echo 关闭此窗口即可停止服务
echo.

streamlit run src\mask_tool\web\app.py --server.port 8501
pause
