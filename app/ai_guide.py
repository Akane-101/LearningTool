"""DeepSeek AI 逐步引导解题（中英双语）。"""

from __future__ import annotations

import json
import re
import uuid
from typing import Any, Optional

from openai import APIStatusError, OpenAI

from .config import (
    DEEPSEEK_API_KEY,
    DEEPSEEK_BASE_URL,
    DEEPSEEK_MODEL,
    DEEPSEEK_VISION_MODEL,
    api_key_configured,
)
from .figure import build_figure_payload

SYSTEM_PROMPTS = {
    "zh": """你是一位耐心的初中数学老师，辅导学生解数学题（以几何角度题、三角形题为主，也覆盖其他初中数学题型）。

教学原则：
1. **只给大致思路，不要拆得太细。** 一次只点拨一个方向，让学生自己往下做。
2. **学生能做出来就不强制写思考过程。**
3. **学生卡住时再继续引导。**
4. **能识别并接续学生已有的做题过程。**
5. 语言简单、清楚，适合初中生。
6. 不要直接泄露最终答案，除非学生明确请求完整解答。
7. **几何题尽量配示意图。** 当题目涉及三角形/角度，且你在给方向或提示时，填写 figure 字段，便于系统画图。第一次引导、学生卡住要提示时尤其要给 figure。

每次回复必须是合法 JSON（不要 markdown 代码块），格式：
{
  "message": "给学生看的主回复",
  "feedback": "对学生上一条回答的评价；第一步可写开场",
  "is_correct": true或false或null,
  "hint": "可选短提示，没有则空字符串",
  "completed": false,
  "final_solution": "仅 completed 为 true 时填写",
  "figure": null或对象
}

figure 对象（几何题需要画图时填写，否则 null）：
{
  "type": "triangle",
  "vertices": ["A", "B", "C"],
  "angle_labels": {"A": "50°", "B": "60°", "C": "?"},
  "highlight": "C",
  "extra_points": [{"name": "D", "on": "BC", "ratio": 0.5}],
  "segments": [["A", "D"]],
  "caption": "标出已知角，求∠C"
}

说明：
- angle_labels 填已知角度或 "?" 表示所求
- highlight 填需要强调的角（顶点字母）
- 有角平分线/中点时用 extra_points + segments
- 不要编造题目没有的数据；未知用 "?"
""",
    "en": """You are a patient middle school math teacher helping with geometry and other middle-school math.

Teaching principles:
1. Give only the big-picture idea, not too detailed.
2. Don't force a written thought process if the student can solve it.
3. Guide further only when the student is stuck.
4. Recognize and continue from the student's existing work.
5. Use simple language.
6. Don't reveal the final answer unless asked for the full solution.
7. **For geometry, include a figure when helpful.** Especially on the first guidance turn and when the student asks for a hint.

Each reply must be valid JSON (no markdown), format:
{
  "message": "main reply",
  "feedback": "evaluation of last answer",
  "is_correct": true or false or null,
  "hint": "optional short hint",
  "completed": false,
  "final_solution": "only when completed is true",
  "figure": null or object
}

figure object when drawing is needed:
{
  "type": "triangle",
  "vertices": ["A", "B", "C"],
  "angle_labels": {"A": "50°", "B": "60°", "C": "?"},
  "highlight": "C",
  "extra_points": [{"name": "D", "on": "BC", "ratio": 0.5}],
  "segments": [["A", "D"]],
  "caption": "Mark known angles, find angle C"
}

Rules: do not invent data not in the problem; use "?" for unknowns.
""",
}

SESSIONS: dict[str, dict[str, Any]] = {}


def _client() -> OpenAI:
    if not api_key_configured():
        raise RuntimeError(
            "未配置 DeepSeek API Key。请在 triangle-guide/.env 中设置 DEEPSEEK_API_KEY"
        )
    return OpenAI(
        api_key=DEEPSEEK_API_KEY,
        base_url=DEEPSEEK_BASE_URL,
        timeout=45.0,
    )


def _extract_json(text: str) -> dict[str, Any]:
    text = (text or "").strip()
    if not text:
        return {
            "message": "",
            "feedback": "",
            "is_correct": None,
            "hint": "",
            "completed": False,
            "final_solution": "",
        }
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
        return {
            "message": text,
            "feedback": "",
            "is_correct": None,
            "hint": "",
            "completed": False,
            "final_solution": "",
        }


def _friendly_api_error(exc: Exception) -> str:
    if isinstance(exc, APIStatusError):
        code = exc.status_code
        if code == 401:
            return "API Key 无效，请检查 .env 里的 DEEPSEEK_API_KEY 是否正确。"
        if code == 402:
            return "DeepSeek 账户余额不足，请到 platform.deepseek.com 充值后再试。"
        if code == 429:
            return "请求太频繁，请稍等几秒再试。"
        try:
            body = exc.response.json()
            msg = body.get("error", {}).get("message")
            if msg:
                return f"DeepSeek 返回错误：{msg}"
        except Exception:
            pass
    name = type(exc).__name__
    if "Timeout" in name or "timeout" in str(exc).lower():
        return "DeepSeek 响应超时，请再点一次重试。"
    return f"AI 调用失败：{exc}"


def _message_text(msg: Any) -> str:
    content = getattr(msg, "content", None) or ""
    if content:
        return str(content)
    reasoning = getattr(msg, "reasoning_content", None) or ""
    return str(reasoning)


def _call_ai(messages: list[dict[str, Any]], use_vision: bool = False) -> dict[str, Any]:
    client = _client()
    model = DEEPSEEK_VISION_MODEL if use_vision else DEEPSEEK_MODEL
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.3,
            max_tokens=800,
        )
    except APIStatusError as exc:
        # 视觉不支持时自动降级为纯文字
        if use_vision and exc.status_code in (400, 422):
            text_only_messages = _strip_images(messages)
            return _call_ai(text_only_messages, use_vision=False)
        raise RuntimeError(_friendly_api_error(exc)) from exc
    except Exception as exc:
        raise RuntimeError(_friendly_api_error(exc)) from exc

    content = _message_text(resp.choices[0].message)
    data = _extract_json(content)
    data.setdefault("message", content or "请继续。")
    data.setdefault("feedback", "")
    data.setdefault("hint", "")
    data.setdefault("completed", False)
    data.setdefault("final_solution", "")
    data.setdefault("figure", None)
    if "is_correct" not in data:
        data["is_correct"] = None
    return data


def _with_figure(ai: dict[str, Any], problem_text: str, force_fallback: bool = False) -> dict[str, Any]:
    """给 AI 回复附上可展示的 SVG。"""
    fig_payload = build_figure_payload(ai.get("figure"), problem_text if force_fallback else "")
    if fig_payload is None and force_fallback:
        fig_payload = build_figure_payload(None, problem_text)
    if fig_payload:
        ai = {**ai, "figure_svg": fig_payload["svg"], "figure_caption": fig_payload["caption"]}
    return ai


def _strip_images(messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """把含图片的 content 数组降级为纯文字。"""
    result = []
    for msg in messages:
        content = msg.get("content")
        if isinstance(content, list):
            text_parts = [p.get("text", "") for p in content if p.get("type") == "text"]
            result.append({**msg, "content": "\n".join(text_parts)})
        else:
            result.append(msg)
    return result


def _lang_prefixed(lang: str, zh: str, en: str) -> str:
    return zh if lang == "zh" else en


def start_session(
    problem_text: str,
    lang: str = "zh",
    image_base64: Optional[str] = None,
    image_mime: Optional[str] = None,
) -> dict[str, Any]:
    session_id = str(uuid.uuid4())
    system_prompt = SYSTEM_PROMPTS.get(lang, SYSTEM_PROMPTS["zh"])

    has_image = bool(image_base64)
    use_vision = has_image

    if lang == "en":
        text_part = (
            f"Here is the problem. Please give only a general direction, not too detailed:\n\n"
            f"{problem_text.strip()}\n\n"
            "Note: if the text already contains the student's partial solution, first identify "
            "where they got to, then continue from their reasoning — don't make them start over."
        )
        if has_image:
            text_part += "\n\nI've also attached a photo of the problem (it may include a geometry figure). Please look at the image carefully to understand the full problem."
    else:
        text_part = (
            f"题目如下，请只给一个大致思路方向，不要拆太细：\n\n{problem_text.strip()}\n\n"
            "注意：如果题目文字里已经包含学生写的部分解答过程，请先识别他做到哪一步，"
            "接着他的思路往下引导，不要让他重头来。"
        )
        if has_image:
            text_part += "\n\n我还附上了题目的照片（可能包含几何图形），请仔细看图，结合图片理解完整题目。"

    if has_image:
        mime = image_mime or "image/jpeg"
        user_content: Any = [
            {"type": "text", "text": text_part},
            {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{image_base64}"}},
        ]
    else:
        user_content = text_part

    messages: list[dict[str, Any]] = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content},
    ]
    ai = _call_ai(messages, use_vision=use_vision)
    # 第一次引导：尽量给示意图（AI 没给 figure 时用题目文字兜底）
    ai = _with_figure(ai, problem_text.strip(), force_fallback=True)
    messages.append({"role": "assistant", "content": json.dumps(
        {k: v for k, v in ai.items() if k not in ("figure_svg", "figure_caption")},
        ensure_ascii=False,
    )})

    session = {
        "session_id": session_id,
        "problem_text": problem_text.strip(),
        "messages": messages,
        "lang": lang,
        "has_image": has_image,
        "completed": bool(ai.get("completed")),
        "final_solution": ai.get("final_solution") or "",
        "turns": 1,
    }
    SESSIONS[session_id] = session

    return {
        "ok": True,
        "session_id": session_id,
        "message": ai.get("message", ""),
        "feedback": ai.get("feedback", ""),
        "hint": ai.get("hint", ""),
        "completed": session["completed"],
        "final_solution": session["final_solution"],
        "figure_svg": ai.get("figure_svg"),
        "figure_caption": ai.get("figure_caption"),
    }


def reply_session(
    session_id: str,
    student_answer: str,
    want_hint: bool = False,
) -> dict[str, Any]:
    session = SESSIONS.get(session_id)
    if not session:
        return {"ok": False, "message": "会话不存在或已过期，请重新开始。"}

    if session.get("completed"):
        return {
            "ok": True,
            "message": _lang_prefixed(
                session.get("lang", "zh"),
                "本题已经完成。可以查看完整解答，或换一题继续。",
                "This problem is done. You can view the full solution or try another.",
            ),
            "completed": True,
            "final_solution": session.get("final_solution", ""),
        }

    lang = session.get("lang", "zh")
    messages: list[dict[str, str]] = session["messages"]

    if want_hint and not student_answer.strip():
        user_content = _lang_prefixed(
            lang,
            "我卡住了，请给一个更具体一点的提示，并尽量在 figure 里给出示意图（标已知角和所求角），但不要直接给出最终答案。",
            "I'm stuck. Please give a more specific hint and include a figure object with known/unknown angles, but don't reveal the final answer.",
        )
    else:
        ans = student_answer.strip()
        if not ans:
            user_content = _lang_prefixed(lang, "（学生未填写，请继续引导）", "(Student left it blank, please continue guiding.)")
        elif any(sym in ans for sym in "∵∴=°∠"):
            user_content = _lang_prefixed(
                lang,
                f"以下是我已经写出的做题过程，请看懂我做到哪一步，接着我的思路继续引导：\n\n{ans}",
                f"Here is my work so far. Please understand where I got to and continue from my reasoning:\n\n{ans}",
            )
        else:
            user_content = _lang_prefixed(
                lang,
                f"我的回答/思路：{ans}",
                f"My answer / approach: {ans}",
            )

    messages.append({"role": "user", "content": user_content})
    ai = _call_ai(messages)
    # 学生要提示时强制尽量出图；其他时候有 figure 就渲染
    ai = _with_figure(ai, session.get("problem_text", ""), force_fallback=want_hint)
    messages.append({"role": "assistant", "content": json.dumps(
        {k: v for k, v in ai.items() if k not in ("figure_svg", "figure_caption")},
        ensure_ascii=False,
    )})

    session["turns"] = session.get("turns", 0) + 1
    if ai.get("completed"):
        session["completed"] = True
        session["final_solution"] = ai.get("final_solution") or ai.get("message", "")

    return {
        "ok": True,
        "session_id": session_id,
        "message": ai.get("message", ""),
        "feedback": ai.get("feedback", ""),
        "is_correct": ai.get("is_correct"),
        "hint": ai.get("hint", ""),
        "completed": bool(session.get("completed")),
        "final_solution": session.get("final_solution", ""),
        "turns": session["turns"],
        "figure_svg": ai.get("figure_svg"),
        "figure_caption": ai.get("figure_caption"),
    }


def get_session(session_id: str) -> Optional[dict[str, Any]]:
    return SESSIONS.get(session_id)
