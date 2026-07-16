"""从 .env 读取 API 配置（不打印密钥）。"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
# override=True：改 .env 后 reload 能立刻吃到新 Key
load_dotenv(ROOT / ".env", override=True)

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "").strip()
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com").strip()
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat").strip()
# DeepSeek 官方 API 目前不接受图片；看图用百炼 Qwen-VL（可回退 Gemini）
DEEPSEEK_VISION_MODEL = os.getenv("DEEPSEEK_VISION_MODEL", "deepseek-v4-pro").strip()

# 阿里云百炼（通义千问 VL）— 主看图
DASHSCOPE_API_KEY = "".join(os.getenv("DASHSCOPE_API_KEY", "").split())
DASHSCOPE_BASE_URL = os.getenv(
    "DASHSCOPE_BASE_URL",
    "https://dashscope.aliyuncs.com/compatible-mode/v1",
).strip()
# max 描点更准；也可改成 qwen-vl-plus 更便宜
DASHSCOPE_VL_MODEL = os.getenv("DASHSCOPE_VL_MODEL", "qwen-vl-max").strip()

# Gemini — 可选回退
GEMINI_API_KEY = "".join(os.getenv("GEMINI_API_KEY", "").split())
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-lite").strip()


def _key_ok(key: str) -> bool:
    if not key:
        return False
    if "换成" in key or key.startswith("把这里"):
        return False
    return len(key) >= 8


def api_key_configured() -> bool:
    return _key_ok(DEEPSEEK_API_KEY)


def dashscope_configured() -> bool:
    return _key_ok(DASHSCOPE_API_KEY)


def gemini_configured() -> bool:
    return _key_ok(GEMINI_API_KEY)


def vision_configured() -> bool:
    return dashscope_configured() or gemini_configured()


def vision_provider() -> str:
    if dashscope_configured():
        return "dashscope"
    if gemini_configured():
        return "gemini"
    return "none"
