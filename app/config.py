"""从 .env 读取 DeepSeek 配置（不打印密钥）。"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "").strip()
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com").strip()
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat").strip()
# 视觉模型（看图解题用，deepseek-v4-pro 支持图片输入）
DEEPSEEK_VISION_MODEL = os.getenv("DEEPSEEK_VISION_MODEL", "deepseek-v4-pro").strip()


def api_key_configured() -> bool:
    key = DEEPSEEK_API_KEY
    if not key:
        return False
    if "换成" in key or key.startswith("把这里"):
        return False
    return len(key) >= 8
