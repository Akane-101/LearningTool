"""看几何题图片：优先阿里云百炼（通义 Qwen-VL），可选回退 Gemini。"""

from __future__ import annotations

import base64
import io
import json
import re
import urllib.error
import urllib.request
from typing import Any, Optional

from openai import APIStatusError, OpenAI
from PIL import Image

from .config import (
    DASHSCOPE_API_KEY,
    DASHSCOPE_BASE_URL,
    DASHSCOPE_VL_MODEL,
    GEMINI_API_KEY,
    GEMINI_MODEL,
    dashscope_configured,
    gemini_configured,
)
from .figure import normalize_figure

# 百炼 VL 备用模型（某型号不可用时依次尝试）
_DASHSCOPE_FALLBACKS = (
    "qwen-vl-max",
    "qwen-vl-plus",
    "qwen3-vl-plus",
    "qwen2.5-vl-72b-instruct",
)

_GEMINI_FALLBACKS = (
    "gemini-2.0-flash-lite",
    "gemini-2.0-flash",
    "gemini-1.5-flash",
)

VISION_PROMPT = """你是初中几何读图助手。目标：把原题图片里的几何图形「描」成可编辑矢量，叠加后要和原图重合。

请只返回 JSON（不要 markdown），格式：
{
  "problem_text": "尽量完整还原题干文字",
  "geometry_description": "简要描述图形",
  "figure": {
    "type": "triangle",
    "vertices": ["A", "B", "C"],
    "points": {
      "A": {"x": 0.22, "y": 0.61},
      "B": {"x": 0.48, "y": 0.28},
      "C": {"x": 0.71, "y": 0.66}
    },
    "angle_labels": {"A": "50°", "B": "60°", "C": "?"},
    "highlight": "C",
    "extra_points": [{"name": "D", "on": "BC", "ratio": 0.45}],
    "segments": [["A", "D"]],
    "caption": "描摹原题图形"
  }
}

硬性要求：
1. points 的坐标是相对于【整张图片】：左上角 (0,0)，右下角 (1,1)，x 向右，y 向下。
2. 每个点必须对准原图中该顶点/交点的像素位置（看字母标注旁的角点），误差尽量小于 0.02。
3. 不要把图形单独「摆正」或放大到画布中央；原图三角形在照片左边，points 也必须在左边。
4. 所有可见的重要点都写入 points（含辅助点）；边上的点可同时给 extra_points（on 如 "BC"，ratio 从起点到终点）。
5. segments 只包含原图中真实存在的线（实线/虚线辅助线）。
6. 不要编造点或线；未知角用 "?"。
"""


def _shrink_image(data: bytes, max_side: int = 1280) -> tuple[bytes, str, int, int]:
    img = Image.open(io.BytesIO(data))
    if img.mode not in ("RGB", "L"):
        img = img.convert("RGB")
    elif img.mode == "L":
        img = img.convert("RGB")
    w, h = img.size
    scale = min(1.0, max_side / max(w, h))
    if scale < 1.0:
        img = img.resize((int(w * scale), int(h * scale)), Image.Resampling.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85)
    return buf.getvalue(), "image/jpeg", img.size[0], img.size[1]


def _extract_json(text: str) -> dict[str, Any]:
    text = (text or "").strip()
    if "```" in text:
        m = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
        if m:
            text = m.group(1).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start >= 0 and end > start:
            try:
                return json.loads(text[start : end + 1])
            except json.JSONDecodeError:
                pass
    return {}


def _parse_vision_text(
    text: str,
    engine: str,
    img_w: Optional[int] = None,
    img_h: Optional[int] = None,
) -> dict[str, Any]:
    data_obj = _extract_json(text)
    problem_text = str(data_obj.get("problem_text") or "").strip()
    geometry_description = str(data_obj.get("geometry_description") or "").strip()
    figure = normalize_figure(data_obj.get("figure"), img_w=img_w, img_h=img_h)

    if not problem_text and not geometry_description and not figure:
        return {
            "ok": False,
            "message": "未能从图片中识别出题目或图形",
            "problem_text": "",
            "geometry_description": "",
            "figure": None,
        }

    return {
        "ok": True,
        "message": "已按原图描摹几何图形，可拖动调整",
        "problem_text": problem_text,
        "geometry_description": geometry_description,
        "figure": figure,
        "engine": engine,
    }


def analyze_geometry_image(
    data: bytes,
    mime: Optional[str] = None,
    lang: str = "zh",
) -> dict[str, Any]:
    """返回看图结果。优先百炼 Qwen-VL，其次 Gemini。"""
    if not dashscope_configured() and not gemini_configured():
        return {
            "ok": False,
            "message": (
                "未配置看图 API。请到阿里云百炼申请 Key，写入 .env 的 DASHSCOPE_API_KEY："
                "https://bailian.console.aliyun.com/"
            ),
            "problem_text": "",
            "geometry_description": "",
            "figure": None,
        }

    try:
        jpeg_bytes, used_mime, img_w, img_h = _shrink_image(data)
    except Exception:
        return {
            "ok": False,
            "message": "无法读取图片",
            "problem_text": "",
            "geometry_description": "",
            "figure": None,
        }

    prompt = VISION_PROMPT
    if lang == "en":
        prompt += "\nPlease write problem_text and geometry_description in English."

    errors: list[str] = []

    if dashscope_configured():
        result = _analyze_with_dashscope(jpeg_bytes, used_mime, prompt, img_w, img_h)
        if result.get("ok"):
            return result
        errors.append(result.get("message") or "百炼看图失败")

    if gemini_configured():
        result = _analyze_with_gemini(jpeg_bytes, used_mime, prompt, img_w, img_h)
        if result.get("ok"):
            return result
        errors.append(result.get("message") or "Gemini 看图失败")

    return {
        "ok": False,
        "message": "；".join(errors) if errors else "看图失败",
        "problem_text": "",
        "geometry_description": "",
        "figure": None,
    }


def _analyze_with_dashscope(
    jpeg_bytes: bytes,
    mime: str,
    prompt: str,
    img_w: int,
    img_h: int,
) -> dict[str, Any]:
    b64 = base64.b64encode(jpeg_bytes).decode("ascii")
    data_url = f"data:{mime};base64,{b64}"

    models: list[str] = []
    for m in (DASHSCOPE_VL_MODEL, *_DASHSCOPE_FALLBACKS):
        if m and m not in models:
            models.append(m)

    client = OpenAI(
        api_key=DASHSCOPE_API_KEY,
        base_url=DASHSCOPE_BASE_URL,
        timeout=60.0,
    )
    last_error = "百炼看图失败"

    for model in models:
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": data_url}},
                ],
            }
        ]
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.1,
                max_tokens=1600,
            )
            text = (resp.choices[0].message.content or "").strip()
            if not text:
                last_error = f"百炼模型 {model} 返回空内容"
                continue
            parsed = _parse_vision_text(
                text, engine=f"dashscope:{model}", img_w=img_w, img_h=img_h
            )
            if parsed.get("ok"):
                return parsed
            last_error = parsed.get("message") or last_error
        except APIStatusError as exc:
            detail = ""
            try:
                detail = exc.response.text[:200]
            except Exception:
                pass
            last_error = _friendly_dashscope_error(exc.status_code, detail, model)
            if exc.status_code in (401, 403):
                break
            continue
        except Exception as exc:
            last_error = f"百炼看图失败：{type(exc).__name__}"
            continue

    return {
        "ok": False,
        "message": last_error,
        "problem_text": "",
        "geometry_description": "",
        "figure": None,
    }


def _friendly_dashscope_error(code: int, detail: str, model: str) -> str:
    low = (detail or "").lower()
    if code in (401, 403) or "invalid" in low and "key" in low:
        return "百炼 API Key 无效，请检查 .env 里的 DASHSCOPE_API_KEY。"
    if code == 429 or "quota" in low or "限流" in detail or "Throttling" in detail:
        return "百炼请求过于频繁或额度不足，请稍后再试。"
    if code == 404 or "model" in low and ("not" in low or "exist" in low):
        return f"百炼模型 {model} 不可用，正在尝试其他模型…"
    if "Arrearage" in detail or "欠费" in detail:
        return "百炼账户欠费或未开通计费，请到控制台检查。"
    return f"百炼看图失败（{code}），请稍后重试。"


def _analyze_with_gemini(
    jpeg_bytes: bytes,
    mime: str,
    prompt: str,
    img_w: int,
    img_h: int,
) -> dict[str, Any]:
    b64 = base64.b64encode(jpeg_bytes).decode("ascii")
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt},
                    {"inline_data": {"mime_type": mime, "data": b64}},
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.1,
            "responseMimeType": "application/json",
        },
    }

    models: list[str] = []
    for m in (GEMINI_MODEL, *_GEMINI_FALLBACKS):
        if m and m not in models:
            models.append(m)

    last_error = "Gemini 看图失败"
    body: Optional[dict[str, Any]] = None
    used_model = ""

    for model in models:
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{model}:generateContent?key={GEMINI_API_KEY}"
        )
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                body = json.loads(resp.read().decode("utf-8"))
            used_model = model
            break
        except urllib.error.HTTPError as exc:
            detail = ""
            try:
                detail = exc.read().decode("utf-8")
            except Exception:
                pass
            if exc.code == 429:
                last_error = "Gemini 免费额度用尽（429），请稍后再试。"
                continue
            last_error = f"Gemini 看图失败（{exc.code}）"
            if exc.code in (401, 403):
                break
            continue
        except Exception:
            last_error = "Gemini 看图请求失败"
            continue

    if body is None:
        return {
            "ok": False,
            "message": last_error,
            "problem_text": "",
            "geometry_description": "",
            "figure": None,
        }

    try:
        text = body["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError, TypeError):
        return {
            "ok": False,
            "message": "Gemini 没有返回有效内容",
            "problem_text": "",
            "geometry_description": "",
            "figure": None,
        }

    return _parse_vision_text(
        text, engine=f"gemini:{used_model}", img_w=img_w, img_h=img_h
    )
