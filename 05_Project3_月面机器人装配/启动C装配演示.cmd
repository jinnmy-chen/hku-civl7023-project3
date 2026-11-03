@echo off
chcp 65001 >nul
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo 请先按仓库README创建Python 3.12虚拟环境并安装requirements.txt。
  pause
  exit /b 1
)
set PYTHONDONTWRITEBYTECODE=1
".venv\Scripts\python.exe" "C_仿真与装配\run_preloaded_tray_assembly_fast.py" --gui %*
if errorlevel 1 pause
