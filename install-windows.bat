@echo off
chcp 65001 >nul 2>&1
title mask-tool 文件脱敏工具 - 安装程序

echo.
echo ============================================
echo    lock mask-tool 文件脱敏工具 - 安装程序
echo ============================================
echo.

:: 获取脚本所在目录
cd /d "%~dp0"

:: 1. 检查 Python
echo [1/4] 检查 Python...
where python >nul 2>&1
if %errorlevel% neq 0 (
    where python3 >nul 2>&1
    if %errorlevel% neq 0 (
        echo   [X] 未找到 Python
        echo.
        echo   请先安装 Python 3.8+：
        echo   1. 访问 https://www.python.org/downloads/
        echo   2. 下载 Windows 安装包
        echo   3. 安装时勾选 "Add Python to PATH"
        echo   4. 重新运行此脚本
        echo.
        pause
        exit /b 1
    ) else (
        set PYTHON=python3
    )
) else (
    set PYTHON=python
)

for /f "tokens=2 delims= " %%v in ('%PYTHON% --version 2^>^&1') do set PY_VER=%%v
echo   [OK] 找到 Python %PY_VER%

:: 2. 创建虚拟环境
echo.
echo [2/4] 创建虚拟环境...
if exist ".venv" (
    echo   [!] 虚拟环境已存在，跳过创建
) else (
    %PYTHON% -m venv .venv
    if %errorlevel% neq 0 (
        echo   [X] 虚拟环境创建失败
        pause
        exit /b 1
    )
    echo   [OK] 虚拟环境创建成功
)

:: 激活虚拟环境
call .venv\Scripts\activate.bat

:: 3. 安装依赖
echo.
echo [3/4] 安装依赖（可能需要几分钟）...
pip install --upgrade pip --quiet 2>nul
pip install -e ".[web]"
if %errorlevel% neq 0 (
    echo   [!] 部分依赖安装失败，尝试重新安装...
    pip install -e ".[web]"
)

echo   [OK] 依赖安装完成

:: 4. 初始化配置
echo.
echo [4/4] 初始化配置...
if not exist "config\lexicon.yaml" (
    if exist "config\sample_lexicon.yaml" (
        copy "config\sample_lexicon.yaml" "config\lexicon.yaml" >nul
        echo   [OK] 已创建用户词库 config\lexicon.yaml
    )
) else (
    echo   [OK] 配置已就绪
)

:: 创建历史目录
if not exist "%USERPROFILE%\.mask-tool" mkdir "%USERPROFILE%\.mask-tool"

:: 创建桌面启动脚本
echo.
echo 创建桌面快捷方式...
set DESKTOP=%USERPROFILE%\Desktop
set START_SCRIPT=%DESKTOP%\mask-tool启动.bat

echo @echo off > "%START_SCRIPT%"
echo chcp 65001 ^>nul 2^>^&1 >> "%START_SCRIPT%"
echo title mask-tool 文件脱敏工具 >> "%START_SCRIPT%"
echo cd /d "%%~dp0" >> "%START_SCRIPT%"
echo :: 定位到项目目录 >> "%START_SCRIPT%"
echo for %%%%d in ("%cd%") do set "PARENT=%%%%~nxd" >> "%START_SCRIPT%"
echo if "%%PARENT%%"=="Desktop" ( >> "%START_SCRIPT%"
echo     cd /d "%~dp0" >> "%START_SCRIPT%"
echo ) >> "%START_SCRIPT%"
echo if not exist pyproject.toml ( >> "%START_SCRIPT%"
echo     echo 错误：找不到 mask-tool 项目目录 >> "%START_SCRIPT%"
echo     pause >> "%START_SCRIPT%"
echo     exit /b 1 >> "%START_SCRIPT%"
echo ) >> "%START_SCRIPT%"
echo call .venv\Scripts\activate.bat >> "%START_SCRIPT%"
echo echo 正在启动 mask-tool... >> "%START_SCRIPT%"
echo echo 启动后浏览器会自动打开 http://localhost:8501 >> "%START_SCRIPT%"
echo echo 关闭此窗口即可停止服务 >> "%START_SCRIPT%"
echo streamlit run src\mask_tool\web\app.py --server.port 8501 >> "%START_SCRIPT%"
echo pause >> "%START_SCRIPT%"

echo   [OK] 桌面快捷方式已创建

:: 完成
echo.
echo ============================================
echo   [OK] 安装完成！
echo ============================================
echo.
echo   使用方式：
echo   1. 双击桌面上的「mask-tool启动.bat」
echo   2. 浏览器会自动打开 http://localhost:8501
echo   3. 关闭命令行窗口即可停止服务
echo.
echo   如需卸载，删除项目文件夹即可。
echo.
pause
