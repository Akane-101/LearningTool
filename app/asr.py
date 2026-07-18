"""语音转文字：阿里云百炼 Qwen3-ASR-Flash（本地 base64，不依赖公网 URL）。"""

from __future__ import annotations

import base64
import json
import os
import urllib.error
import urllib.request
from typing import Any

from .config import DASHSCOPE_API_KEY, dashscope_configured

DASHSCOPE_ASR_MODEL = os.getenv("DASHSCOPE_ASR_MODEL", "qwen3-asr-flash").strip()
ASR_URL = "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"

_MIME_ALIASES = {
    "audio/mp3": "audio/mpeg",
    "audio/x-wav": "audio/wav",
    "audio/wave": "audio/wav",
}


def asr_configured() -> bool:
    return dashscope_configured()


def _normalize_mime(mime: str | None) -> str:
    raw = (mime or "audio/webm").split(";")[0].strip().lower() or "audio/webm"
    return _MIME_ALIASES.get(raw, raw)


def _extract_text(body: dict[str, Any]) -> str:
    try:
        content = body["output"]["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        return ""

    if isinstance(content, str):
        return content.strip()

    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, str) and item.strip():
                parts.append(item.strip())
            elif isinstance(item, dict):
                text = item.get("text")
                if isinstance(text, str) and text.strip():
                    parts.append(text.strip())
        return "".join(parts).strip()

    return ""


def transcribe_audio(
    data: bytes,
    mime: str | None = None,
    language: str = "zh",
) -> dict[str, Any]:
    if not asr_configured():
        return {
            "ok": False,
            "text": "",
            "message": "未配置 DASHSCOPE_API_KEY，语音识别不可用。",
        }
    if not data:
        return {"ok": False, "text": "", "message": "没有收到音频，请再说一次。"}
    if len(data) > 10 * 1024 * 1024:
        return {"ok": False, "text": "", "message": "录音太长（超过 10MB），请短一点再说。"}

    mime_type = _normalize_mime(mime)
    data_uri = f"data:{mime_type};base64,{base64.b64encode(data).decode('ascii')}"
    lang = "zh" if (language or "zh").lower().startswith("zh") else "en"

    payload = {
        "model": DASHSCOPE_ASR_MODEL,
        "input": {
            "messages": [
                {
                    "role": "user",
                    "content": [{"audio": data_uri}],
                }
            ]
        },
        "parameters": {
            "asr_options": {
                "language": lang,
                "enable_itn": True,
            }
        },
    }

    req = urllib.request.Request(
        ASR_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {DASHSCOPE_API_KEY}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = ""
        try:
            detail = exc.read().decode("utf-8")
        except Exception:
            pass
        msg = f"语音识别失败（{exc.code}）"
        if exc.code in (401, 403):
            msg = "语音识别鉴权失败，请检查 DASHSCOPE_API_KEY。"
        elif exc.code == 429:
            msg = "语音识别请求过多，请稍后再试。"
        elif detail:
            try:
                err = json.loads(detail)
                msg = (
                    err.get("message")
                    or (err.get("error") or {}).get("message")
                    or msg
                )
            except Exception:
                pass
        return {"ok": False, "text": "", "message": msg}
    except Exception as exc:
        return {"ok": False, "text": "", "message": f"语音识别请求失败：{exc}"}

    if isinstance(body, dict) and body.get("code") and str(body.get("code")) not in ("", "200"):
        return {
            "ok": False,
            "text": "",
            "message": body.get("message") or f"语音识别失败：{body.get('code')}",
        }

    text = _extract_text(body if isinstance(body, dict) else {})
    if not text:
        return {
            "ok": False,
            "text": "",
            "message": "没有识别出文字，请靠近麦克风再说清楚一点。",
        }

    return {
        "ok": True,
        "text": text,
        "message": "识别完成",
        "model": DASHSCOPE_ASR_MODEL,
    }
