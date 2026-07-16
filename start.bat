@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo [1/3] 检查虚拟环境...
if not exist ".venv\Scripts\python.exe" (
  echo 正在创建 .venv ...
  py -3 -m venv .venv 2>nul || python -m venv .venv
  if errorlevel 1 (
    echo 未找到 Python，请先安装 Python 3.10+ 并勾选 Add to PATH
    pause
    exit /b 1
  )
)

echo [2/3] 安装依赖（首次可能较慢）...
".venv\Scripts\python.exe" -m pip install -q -r requirements.txt
if errorlevel 1 (
  echo 依赖安装失败
  pause
  exit /b 1
)

if not exist ".env" (
  echo.
  echo 未找到 .env：已从 .env.example 复制一份
  copy /Y ".env.example" ".env" >nul
  echo 请用记事本打开 .env，填入 DEEPSEEK_API_KEY 和 DASHSCOPE_API_KEY 后重新运行本脚本
  notepad ".env"
  pause
  exit /b 0
)

echo [3/3] 启动服务 http://127.0.0.1:8001
echo 浏览器打开上述地址；关闭本窗口即停止服务
echo.
start "" "http://127.0.0.1:8001"
".venv\Scripts\python.exe" -m uvicorn app.main:app --host 127.0.0.1 --port 8001
pause
