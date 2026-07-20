@echo off
chcp 65001 >nul
cd /d "%~dp0"
title PathSolve 向解 - 启动中

echo [1/4] 检查虚拟环境...
if not exist ".venv\Scripts\python.exe" (
  echo 正在创建 .venv ...
  py -3 -m venv .venv 2>nul || python -m venv .venv
  if errorlevel 1 (
    echo 未找到 Python，请先安装 Python 3.10+ 并勾选 Add to PATH
    pause
    exit /b 1
  )
)

echo [2/4] 安装依赖（首次可能较慢，请稍候）...
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

echo [3/4] 启动服务 http://127.0.0.1:8001
echo 请保持本黑窗口开着；关掉窗口服务就会停止
echo.

REM 先后台启动 uvicorn，等端口就绪后再打开浏览器（避免“打不开”的错觉）
start "PathSolve-server" /MIN ".venv\Scripts\python.exe" -m uvicorn app.main:app --host 127.0.0.1 --port 8001

echo [4/4] 等待服务就绪...
set /a _tries=0
:wait_loop
set /a _tries+=1
REM 用 venv 里的 Python 探测（不依赖系统 powershell 是否在 PATH）
".venv\Scripts\python.exe" -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8001/api/health', timeout=1).read()" >nul 2>&1
if %errorlevel%==0 goto ready
if %_tries% geq 40 (
  echo.
  echo 启动超时。请看是否弹出了名为 PathSolve-server 的窗口，里面是否有报错。
  echo 也可手动运行：
  echo   .venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8001
  pause
  exit /b 1
)
timeout /t 1 /nobreak >nul
goto wait_loop

:ready
echo 服务已就绪，正在打开浏览器...
start "" "http://127.0.0.1:8001"
echo.
echo 已启动：http://127.0.0.1:8001
echo 最小化窗口 PathSolve-server 里是服务进程，不要关掉。
echo 本窗口可关闭；若要停止服务，关掉 PathSolve-server 窗口即可。
pause
