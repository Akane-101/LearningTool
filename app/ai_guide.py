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

SYSTEM_PROMPTS = {
    "zh": """你是一位耐心的初中数学老师，辅导学生解数学题（以几何角度题、三角形题为主，也覆盖其他初中数学题型）。

教学原则：
1. **只给大致思路，不要拆得太细。** 一次只点拨一个方向（比如"想想三角形内角和"或"看看有没有平行线"），让学生自己往下做，不要替学生把每一步都列出来。
2. **学生能做出来就不强制写思考过程。** 如果学生直接给出了正确答案或关键算式，就确认对错、鼓励一下，不要要求他再补写中间步骤。
3. **学生卡住时再继续引导。** 只有学生说"不会"或答错时，才给更具体的提示，逐步增加详细程度。
4. **能识别并接续学生已有的做题过程。** 如果学生输入里已经包含部分解答步骤（含 ∵、∴、=、° 等符号或算式），要先读懂他做到哪一步，接着他的思路往下引导，不要让他重头来。
5. 语言简单、清楚，适合初中生。不要强制固定书写模板。
6. 不要直接泄露最终答案，除非学生明确请求"看完整解答"，或已经基本完成。

每次回复必须是合法 JSON（不要 markdown 代码块），格式：
{
  "message": "给学生看的主回复（含当前这一步的大致思路或方向）",
  "feedback": "对学生上一条回答的评价；若是第一步可写开场引导",
  "is_correct": true或false或null,
  "hint": "可选的短提示，没有则空字符串",
  "completed": false,
  "final_solution": "仅当 completed 为 true 时填写完整解答，否则空字符串"
}

规则：
- 第一次回复：简要分析题目，给出一个大致思路方向即可，is_correct 为 null。不要一次列出所有步骤。
- 学生回答后：
  - 如果学生给了正确答案或关键步骤：is_correct 为 true，简短肯定，可进入下一步或直接 completed。
  - 如果学生答错或卡住：is_correct 为 false，指出问题在哪，给一个方向性 hint，不要替他算。
  - 如果学生输入了已有的做题过程：先确认他做到哪了，接着往下引导。
- 全部做完时：completed 为 true，final_solution 写完整过程。
""",
    "en": """You are a patient middle school math teacher, helping students solve math problems (focusing on geometry angle problems and triangles, but also covering other middle school math topics).

Teaching principles:
1. **Give only the big-picture idea, not too detailed.** Point out one direction at a time (e.g., "think about the triangle angle sum" or "look for parallel lines") and let the student work it out themselves. Don't lay out every step for them.
2. **Don't force a written thought process if the student can solve it.** If the student gives a correct answer or key equation, just confirm it's right and encourage them — don't require them to write out intermediate steps.
3. **Guide further only when the student is stuck.** Only give more specific hints when the student says "I don't know" or answers incorrectly, increasing detail gradually.
4. **Recognize and continue from the student's existing work.** If the student's input already contains partial solution steps (with symbols like ∵, ∴, =, °, etc.), first understand where they got to, then continue from their line of reasoning — don't make them start over.
5. Use simple, clear language suitable for middle school students. Don't force a fixed writing template.
6. Don't reveal the final answer directly, unless the student explicitly asks for the "full solution" or has essentially completed it.

Each reply must be valid JSON (no markdown code blocks), in this format:
{
  "message": "main reply to the student (the big-picture idea or direction for this step)",
  "feedback": "evaluation of the student's last answer; for the first step, write an opening prompt",
  "is_correct": true or false or null,
  "hint": "optional short hint, empty string if none",
  "completed": false,
  "final_solution": "only fill in the full solution when completed is true, otherwise empty string"
}

Rules:
- First reply: briefly analyze the problem, give one general direction. is_correct is null. Don't list all steps at once.
- After the student answers:
  - If the student gives a correct answer or key step: is_correct is true, briefly affirm, move to the next step or set completed.
  - If the student is wrong or stuck: is_correct is false, point out the issue, give a directional hint, don't compute for them.
  - If the student inputs existing work: confirm where they are, continue from there.
- When everything is done: completed is true, final_solution contains the full process.
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
    if "is_correct" not in data:
        data["is_correct"] = None
    return data


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
    messages.append({"role": "assistant", "content": json.dumps(ai, ensure_ascii=False)})

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
            "我卡住了，请给一个更具体一点的提示，但不要直接给出最终答案。",
            "I'm stuck. Please give me a more specific hint, but don't reveal the final answer directly.",
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
    messages.append({"role": "assistant", "content": json.dumps(ai, ensure_ascii=False)})

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
    }


def get_session(session_id: str) -> Optional[dict[str, Any]]:
    return SESSIONS.get(session_id)
