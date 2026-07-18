#!/usr/bin/env bash
# 树莓派 / Linux / macOS 启动脚本
set -e
cd "$(dirname "$0")"

echo "[1/3] 检查虚拟环境..."
if [ ! -x ".venv/bin/python" ]; then
  echo "正在创建 .venv ..."
  python3 -m venv .venv
fi

echo "[2/3] 安装依赖（首次在树莓派上可能较慢）..."
.venv/bin/python -m pip install -U pip
.venv/bin/pip install -r requirements.txt

if [ ! -f ".env" ]; then
  echo
  echo "未找到 .env：已从 .env.example 复制"
  cp .env.example .env
  echo "请编辑 .env，填入 DEEPSEEK_API_KEY 和 DASHSCOPE_API_KEY："
  echo "  nano .env"
  exit 0
fi

# 0.0.0.0 = 局域网其他设备也能访问（手机/电脑浏览器）
HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8001}"

echo "[3/3] 启动服务 http://${HOST}:${PORT}"
echo "本机访问: http://127.0.0.1:${PORT}"
echo "局域网访问: http://<树莓派IP>:${PORT}"
echo "查 IP 可执行: hostname -I"
echo "按 Ctrl+C 停止"
echo
.venv/bin/python -m uvicorn app.main:app --host "$HOST" --port "$PORT"
