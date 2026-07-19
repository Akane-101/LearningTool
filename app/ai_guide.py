"""DeepSeek AI 逐步引导解题（中英双语）。

看图：DeepSeek 官方 API 不接受图片；几何图由阿里云百炼（Qwen-VL）看图后结构化，再交给 DeepSeek 引导与画板。
"""

from __future__ import annotations

import base64
import json
import re
import uuid
from typing import Any, Optional

from openai import APIStatusError, OpenAI

from .config import (
    DEEPSEEK_API_KEY,
    DEEPSEEK_BASE_URL,
    DEEPSEEK_MODEL,
    api_key_configured,
)
from .figure import build_figure_payload, normalize_figure
from .solid import figure_solid_from_text, is_solid_figure
from .vision import analyze_geometry_image

SYSTEM_PROMPTS = {
    "zh": """你是一位耐心的初中数学老师，辅导学生解数学题（平面几何、立体几何与其他初中题型）。

教学原则：
1. **只给大致思路，不要拆得太细。** 一次只点拨一个方向，让学生自己往下做。
2. **学生能做出来就不强制写思考过程。**
3. **学生卡住时再继续引导。**
4. **能识别并接续学生已有的做题过程。**
5. 语言简单、清楚，适合初中生。
6. 不要直接泄露最终答案，除非学生明确请求完整解答。
7. **几何题尽量配示意图。** 若题目里已有「根据原题图片识别的图形」，你的 figure 必须严格按该描述还原，不要另画无关图形。
8. **立体几何题请返回立体 figure**（正方体/长方体/三棱柱/四棱锥/圆柱/圆锥），便于前端生成可旋转立体图。

每次回复必须是合法 JSON（不要 markdown 代码块），格式：
{
  "message": "给学生看的主回复",
  "feedback": "对学生上一条回答的评价；第一步可写开场",
  "is_correct": true或false或null,
  "hint": "可选短提示，没有则空字符串",
  "completed": false,
  "final_solution": "仅 completed 为 true 时填写",
  "review": null,
  "figure": null或对象
}

当且仅当 completed 为 true 时，必须填写 review（做完整道题后的反馈与建议）：
{
  "summary": "一两句总评，鼓励为主",
  "strengths": ["做得好的点1", "点2"],
  "improvements": ["可改进的点1"],
  "suggestions": ["方法记忆/易错提醒", "可继续练习的题型方向"]
}
未完成时 review 填 null。

平面几何 figure（三角形等）：
{
  "type": "triangle",
  "vertices": ["A", "B", "C"],
  "points": {"A": {"x": 0.15, "y": 0.75}, "B": {"x": 0.50, "y": 0.18}, "C": {"x": 0.88, "y": 0.78}},
  "angle_labels": {"A": "50°", "B": "60°", "C": "?"},
  "highlight": "C",
  "extra_points": [{"name": "D", "on": "BC", "ratio": 0.5}],
  "segments": [["A", "D"]],
  "caption": "标出已知角，求∠C"
}

立体几何 figure（表面积/体积/展开图等）：
{
  "type": "solid",
  "solid": "cube|rectangular_prism|triangular_prism|square_pyramid|cylinder|cone",
  "dims": {"length": 4, "width": 3, "height": 5, "radius": 2},
  "labels": {"length": "4", "width": "3", "height": "5"},
  "highlight_edges": [["A", "B"]],
  "caption": "长方体示意图"
}

说明：
- 平面 points 用 0~1 坐标（左上原点，y 向下），贴近原题形状
- 立体 dims 用题目给出的长宽高/棱长/底面半径；未知可省略，用合理示意值
- labels 写尺寸文字（如 "4cm" 或 "a"）；不要编造题目没有的数据
""",
    "en": """You are a patient middle school math teacher helping with plane geometry, solid geometry, and other middle-school math.

Teaching principles:
1. Give only the big-picture idea, not too detailed.
2. Don't force a written thought process if the student can solve it.
3. Guide further only when the student is stuck.
4. Recognize and continue from the student's existing work.
5. Use simple language.
6. Don't reveal the final answer unless asked for the full solution.
7. **For geometry, include a figure when helpful.** Match any photo-derived geometry description.
8. **For solid geometry, return a solid figure** so the UI can render a rotatable 3D sketch.

Each reply must be valid JSON (no markdown), format:
{
  "message": "main reply",
  "feedback": "evaluation of last answer",
  "is_correct": true or false or null,
  "hint": "optional short hint",
  "completed": false,
  "final_solution": "only when completed is true",
  "review": null,
  "figure": null or object
}

When and only when completed is true, you MUST include review (end-of-problem feedback):
{
  "summary": "1–2 sentence overall feedback, encouraging",
  "strengths": ["what went well 1", "item 2"],
  "improvements": ["what to improve 1"],
  "suggestions": ["method tip / common pitfall", "what to practice next"]
}
If not completed, set review to null.

Plane figure:
{
  "type": "triangle",
  "vertices": ["A", "B", "C"],
  "points": {"A": {"x": 0.15, "y": 0.75}, "B": {"x": 0.50, "y": 0.18}, "C": {"x": 0.88, "y": 0.78}},
  "angle_labels": {"A": "50°", "B": "60°", "C": "?"},
  "highlight": "C",
  "extra_points": [{"name": "D", "on": "BC", "ratio": 0.5}],
  "segments": [["A", "D"]],
  "caption": "Mark known angles, find angle C"
}

Solid figure:
{
  "type": "solid",
  "solid": "cube|rectangular_prism|triangular_prism|square_pyramid|cylinder|cone",
  "dims": {"length": 4, "width": 3, "height": 5, "radius": 2},
  "labels": {"length": "4", "width": "3", "height": "5"},
  "highlight_edges": [["A", "B"]],
  "caption": "Rectangular prism"
}

Rules: do not invent data; use given dimensions when present.
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


def _call_ai(messages: list[dict[str, Any]]) -> dict[str, Any]:
    client = _client()
    try:
        resp = client.chat.completions.create(
            model=DEEPSEEK_MODEL,
            messages=messages,
            temperature=0.3,
            max_tokens=800,
        )
    except APIStatusError as exc:
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
    data.setdefault("review", None)
    if "is_correct" not in data:
        data["is_correct"] = None
    return data


def _as_str_list(value: Any, limit: int = 5) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        text = value.strip()
        return [text] if text else []
    if isinstance(value, list):
        out: list[str] = []
        for item in value:
            s = str(item).strip()
            if s:
                out.append(s)
            if len(out) >= limit:
                break
        return out
    return []


def _normalize_review(raw: Any, lang: str = "zh") -> Optional[dict[str, Any]]:
    """把 AI 返回的 review 整理成统一结构；无效则返回 None。"""
    if raw is None:
        return None
    if isinstance(raw, str):
        text = raw.strip()
        if not text:
            return None
        return {
            "summary": text,
            "strengths": [],
            "improvements": [],
            "suggestions": [],
        }
    if not isinstance(raw, dict):
        return None

    summary = str(
        raw.get("summary")
        or raw.get("overview")
        or raw.get("overall")
        or ""
    ).strip()
    strengths = _as_str_list(raw.get("strengths") or raw.get("pros"))
    improvements = _as_str_list(
        raw.get("improvements") or raw.get("weaknesses") or raw.get("to_improve")
    )
    suggestions = _as_str_list(
        raw.get("suggestions") or raw.get("advice") or raw.get("next_steps")
    )

    if not summary and not strengths and not improvements and not suggestions:
        return None
    if not summary:
        summary = (
            "本题已完成，下面是针对你做题过程的反馈。"
            if lang == "zh"
            else "Problem completed. Here is feedback on your work."
        )
    return {
        "summary": summary,
        "strengths": strengths,
        "improvements": improvements,
        "suggestions": suggestions,
    }


def _generate_review(session: dict[str, Any], ai: dict[str, Any]) -> dict[str, Any]:
    """完成后若模型未带 review，再单独生成一份做题反馈。"""
    lang = session.get("lang", "zh")
    problem = session.get("problem_text", "")
    solution = ai.get("final_solution") or session.get("final_solution") or ai.get("message", "")
    turns = session.get("turns", 0)

    # 从对话里抽取学生发言摘要
    student_bits: list[str] = []
    for msg in session.get("messages") or []:
        if msg.get("role") != "user":
            continue
        content = str(msg.get("content") or "").strip()
        if not content or content.startswith("题目如下") or content.startswith("Here is the problem"):
            continue
        if "卡住了" in content or "I'm stuck" in content:
            student_bits.append("[asked for a hint]" if lang == "en" else "[请求过提示]")
            continue
        student_bits.append(content[:400])
    student_log = "\n---\n".join(student_bits[-6:]) or (
        "(no detailed student answers recorded)" if lang == "en" else "（对话中学生作答较少）"
    )

    if lang == "en":
        prompt = (
            "The student just finished this middle-school math problem with step-by-step guidance.\n"
            "Write an encouraging post-problem review as JSON only (no markdown):\n"
            '{"summary":"...","strengths":["..."],"improvements":["..."],"suggestions":["..."]}\n'
            f"Problem:\n{problem[:1200]}\n\n"
            f"Final solution:\n{str(solution)[:1200]}\n\n"
            f"Student turns (~{turns}):\n{student_log}\n\n"
            "Keep each list to 1–3 short bullets. Focus on reasoning habits, not repeating the whole solution."
        )
    else:
        prompt = (
            "学生刚在逐步引导下做完一道初中数学题。请根据过程给出鼓励性的做题反馈。"
            "只返回 JSON（不要 markdown）：\n"
            '{"summary":"...","strengths":["..."],"improvements":["..."],"suggestions":["..."]}\n'
            f"题目：\n{problem[:1200]}\n\n"
            f"完整解答：\n{str(solution)[:1200]}\n\n"
            f"学生互动约 {turns} 轮，作答摘要：\n{student_log}\n\n"
            "每项列表 1～3 条短句。侧重思路习惯与易错点，不要整段重抄解答。"
        )

    client = _client()
    try:
        resp = client.chat.completions.create(
            model=DEEPSEEK_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You output only valid JSON for student learning feedback."
                        if lang == "en"
                        else "你只输出合法 JSON，用于学生做题反馈。"
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.4,
            max_tokens=500,
        )
        data = _extract_json(_message_text(resp.choices[0].message))
        review = _normalize_review(data.get("review") or data, lang=lang)
        if review:
            return review
    except Exception:
        pass

    # 兜底：不依赖模型也能展示
    if lang == "en":
        return {
            "summary": "Nice work finishing this problem. Keep practicing explaining why each step works.",
            "strengths": ["You stayed with the problem until the end."],
            "improvements": ["Try stating the key theorem or property before calculating."],
            "suggestions": [
                "Review similar problems and mark which condition unlocks the next step.",
            ],
        }
    return {
        "summary": "这道题你已经做完了，坚持跟着思路走下去很棒。",
        "strengths": ["能跟着引导把题目做完。"],
        "improvements": ["下一步可以试着先说出用到的定理/性质，再动手算。"],
        "suggestions": ["同类题多练时，标出「哪一个条件推出下一步」。"],
    }


def _local_review(session: dict[str, Any]) -> dict[str, Any]:
    """不额外调模型、立刻可用的反馈（保证完成页一定有内容）。"""
    lang = session.get("lang", "zh")
    turns = int(session.get("turns") or 0)
    asked_hint = False
    for msg in session.get("messages") or []:
        if msg.get("role") != "user":
            continue
        c = str(msg.get("content") or "")
        if "卡住了" in c or "I'm stuck" in c:
            asked_hint = True
            break
    if lang == "en":
        strengths = ["You finished the whole problem with guided steps."]
        improvements = []
        suggestions = [
            "After solving, restate the key property in one sentence from memory.",
            "Try a similar problem and mark which given unlocks the next step.",
        ]
        if asked_hint:
            strengths.append("You asked for a hint when stuck — good habit.")
            improvements.append("Before asking for a hint, write the knowns and what you want to find.")
        elif turns <= 3:
            strengths.append("You reached the answer in relatively few steps.")
            improvements.append("Try writing a short reason (because…) for the key step.")
        else:
            improvements.append("Try naming the theorem/property before calculating.")
        return {
            "summary": "Great job finishing this problem. Below is quick feedback; a fuller review may follow.",
            "strengths": strengths[:3],
            "improvements": improvements[:3] or ["Keep explaining why each step works."],
            "suggestions": suggestions[:3],
            "source": "local",
        }
    strengths = ["能跟着引导把整道题做完。"]
    improvements = []
    suggestions = [
        "做完后试着不看解答，用一句话说出关键性质/定理。",
        "同类题练习时，标出「哪个条件推出下一步」。",
    ]
    if asked_hint:
        strengths.append("卡住时会求助提示，这是好习惯。")
        improvements.append("下次求助前提前写下已知和要求什么。")
    elif turns <= 3:
        strengths.append("用较少轮次就接近答案。")
        improvements.append("关键步骤可以补一句「因为…所以…」。")
    else:
        improvements.append("动手算之前，先说出用到的定理/性质。")
    return {
        "summary": "这道题你已经做完了。下面是针对过程的反馈与建议（完整解答在下方）。",
        "strengths": strengths[:3],
        "improvements": improvements[:3] or ["关键步骤可以写得更清楚一点。"],
        "suggestions": suggestions[:3],
        "source": "local",
    }


def _finalize_review(
    session: dict[str, Any],
    ai: dict[str, Any],
    *,
    enrich: bool = False,
) -> dict[str, Any]:
    """题目完成时写入 session.review。

    默认先用模型自带 review，否则用本地即时反馈，避免再卡一轮 API。
    enrich=True 时再调模型生成更细的反馈。
    """
    lang = session.get("lang", "zh")
    review = _normalize_review(ai.get("review"), lang=lang)
    if review is None and enrich:
        review = _generate_review(session, ai)
    if review is None:
        review = _local_review(session)
    elif "source" not in review:
        review["source"] = "model"
    session["review"] = review
    return review


def ensure_session_review(session_id: str, *, enrich: bool = True) -> dict[str, Any]:
    """给已完成会话补全/增强做题反馈。"""
    session = SESSIONS.get(session_id)
    if not session:
        return {"ok": False, "message": "会话不存在或已过期。"}
    if not session.get("completed"):
        return {"ok": False, "message": "题目尚未完成，还没有总结反馈。"}

    existing = _normalize_review(session.get("review"), lang=session.get("lang", "zh"))
    need_enrich = enrich and (
        existing is None or existing.get("source") == "local"
    )
    if need_enrich:
        ai_stub = {
            "final_solution": session.get("final_solution", ""),
            "message": "",
            "review": None,
        }
        review = _generate_review(session, ai_stub)
        if review:
            review["source"] = "model"
            session["review"] = review
        elif existing:
            session["review"] = existing
        else:
            session["review"] = _local_review(session)
    elif existing is None:
        session["review"] = _local_review(session)
    else:
        session["review"] = existing

    return {
        "ok": True,
        "session_id": session_id,
        "completed": True,
        "final_solution": session.get("final_solution", ""),
        "review": session.get("review"),
    }


def _attach_figure(
    ai: dict[str, Any],
    problem_text: str,
    preferred_figure: Optional[dict[str, Any]] = None,
    force_fallback: bool = False,
) -> dict[str, Any]:
    """优先用看图/立体锁定 figure，其次 AI 的 figure，再文字兜底。"""
    ai_fig = ai.get("figure")
    # 立体题锁定：已有立体结构时，不让 AI 的平面三角形覆盖
    if preferred_figure and is_solid_figure(preferred_figure):
        raw_fig = preferred_figure
    elif is_solid_figure(ai_fig):
        raw_fig = ai_fig
    else:
        raw_fig = preferred_figure or ai_fig
        # 题干是立体题但 AI 只给了平面图时，改用文字立体示意图
        text_solid = figure_solid_from_text(problem_text or "")
        if text_solid and not is_solid_figure(raw_fig):
            raw_fig = text_solid

    fig_payload = build_figure_payload(raw_fig, problem_text if force_fallback else "")
    if fig_payload is None and force_fallback:
        fig_payload = build_figure_payload(None, problem_text)
    if fig_payload:
        ai = {
            **ai,
            "figure": fig_payload.get("figure") or raw_fig,
            "figure_svg": fig_payload["svg"],
            "figure_caption": fig_payload["caption"],
            "figure_data": fig_payload.get("figure"),
        }
    return ai


def _lang_prefixed(lang: str, zh: str, en: str) -> str:
    return zh if lang == "zh" else en


def _resolve_vision(
    problem_text: str,
    lang: str,
    image_base64: Optional[str],
    image_mime: Optional[str],
    geometry_description: Optional[str],
    figure_data: Optional[dict[str, Any]],
) -> tuple[str, str, Optional[dict[str, Any]], Optional[str]]:
    """返回 (enriched_text, geometry_description, vision_figure, vision_note)。"""
    geom = (geometry_description or "").strip()
    vision_figure = normalize_figure(figure_data) if figure_data else None
    vision_note = None

    need_vision = bool(image_base64) and (not geom or not vision_figure)
    if need_vision:
        try:
            raw = base64.b64decode(image_base64)
        except Exception:
            raw = b""
        if raw:
            result = analyze_geometry_image(raw, image_mime, lang=lang)
            if result.get("ok"):
                if not geom:
                    geom = (result.get("geometry_description") or "").strip()
                if not vision_figure:
                    vision_figure = result.get("figure")
                vision_note = result.get("message")
                vt = (result.get("problem_text") or "").strip()
                if vt and (not problem_text.strip() or len(vt) > len(problem_text.strip()) * 0.8):
                    # 看图题干更完整时并入
                    if vt not in problem_text:
                        problem_text = vt if not problem_text.strip() else f"{problem_text.strip()}\n\n{vt}"
            else:
                vision_note = result.get("message")

    if geom:
        marker_zh = "【根据原题图片识别的图形】"
        marker_en = "[Geometry from the original photo]"
        marker = marker_en if lang == "en" else marker_zh
        if marker not in problem_text and geom not in problem_text:
            problem_text = f"{problem_text.strip()}\n\n{marker}\n{geom}"

    return problem_text.strip(), geom, vision_figure, vision_note


def start_session(
    problem_text: str,
    lang: str = "zh",
    image_base64: Optional[str] = None,
    image_mime: Optional[str] = None,
    geometry_description: Optional[str] = None,
    figure_data: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    session_id = str(uuid.uuid4())
    system_prompt = SYSTEM_PROMPTS.get(lang, SYSTEM_PROMPTS["zh"])

    enriched, geom, vision_figure, vision_note = _resolve_vision(
        problem_text,
        lang,
        image_base64,
        image_mime,
        geometry_description,
        figure_data,
    )

    if lang == "en":
        text_part = (
            f"Here is the problem. Please give only a general direction, not too detailed:\n\n"
            f"{enriched}\n\n"
            "Note: if the text already contains the student's partial solution, first identify "
            "where they got to, then continue from their reasoning — don't make them start over. "
            "If a geometry description from the photo is included, base your figure on it."
        )
    else:
        text_part = (
            f"题目如下，请只给一个大致思路方向，不要拆太细：\n\n{enriched}\n\n"
            "注意：如果题目文字里已经包含学生写的部分解答过程，请先识别他做到哪一步，"
            "接着他的思路往下引导，不要让他重头来。"
            "若已有「根据原题图片识别的图形」，figure 必须按该描述画，不要另画无关图形。"
        )

    messages: list[dict[str, Any]] = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": text_part},
    ]
    ai = _call_ai(messages)
    # 有原题看图结果时优先用它画板；立体题用文字立体结构锁定；否则 AI / 文字兜底
    preferred = vision_figure or figure_solid_from_text(enriched)
    ai = _attach_figure(
        ai,
        enriched,
        preferred_figure=preferred,
        force_fallback=not preferred,
    )
    messages.append({"role": "assistant", "content": json.dumps(
        {k: v for k, v in ai.items() if k not in ("figure_svg", "figure_caption", "figure_data")},
        ensure_ascii=False,
    )})

    session = {
        "session_id": session_id,
        "problem_text": enriched,
        "messages": messages,
        "lang": lang,
        "has_image": bool(image_base64),
        "geometry_description": geom,
        "vision_figure": vision_figure or (
            ai.get("figure_data") if is_solid_figure(ai.get("figure_data")) else None
        ),
        "completed": bool(ai.get("completed")),
        "final_solution": ai.get("final_solution") or "",
        "review": None,
        "turns": 1,
    }
    SESSIONS[session_id] = session

    review = None
    if session["completed"]:
        review = _finalize_review(session, ai)

    return {
        "ok": True,
        "session_id": session_id,
        "message": ai.get("message", ""),
        "feedback": ai.get("feedback", ""),
        "hint": ai.get("hint", ""),
        "completed": session["completed"],
        "final_solution": session["final_solution"],
        "review": review,
        "figure_svg": ai.get("figure_svg"),
        "figure_caption": ai.get("figure_caption"),
        "figure_data": ai.get("figure_data") or vision_figure,
        "geometry_description": geom,
        "vision_note": vision_note,
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
                "本题已经完成。可以查看完整解答与做题反馈，或换一题继续。",
                "This problem is done. You can view the full solution and review, or try another.",
            ),
            "completed": True,
            "final_solution": session.get("final_solution", ""),
            "review": session.get("review"),
        }

    lang = session.get("lang", "zh")
    messages: list[dict[str, str]] = session["messages"]

    if want_hint:
        # 点「提示」时始终走提示路径（不因输入框里有草稿而改成普通批改）
        draft = student_answer.strip()
        if lang == "en":
            user_content = (
                "I'm stuck. Give ONE more concrete hint in the JSON field \"hint\" "
                "(required, non-empty). Also put a short encouragement in \"message\". "
                "Do NOT set completed=true. Do NOT reveal the final numerical answer. "
                "Include a figure if helpful."
            )
            if draft:
                user_content += f"\n\nMy current draft (for context only):\n{draft}"
        else:
            user_content = (
                "我卡住了。请务必在 JSON 的 hint 字段给出一条更具体的提示（必填、不能为空），"
                "message 里写一句简短鼓励或下一步方向。"
                "不要 completed=true，不要直接给出最终数值答案。"
                "如有需要可配 figure 示意图。"
            )
            if draft:
                user_content += f"\n\n这是我输入框里的草稿（仅供参考，请据此给提示）：\n{draft}"
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
    if want_hint:
        # 模型常把提示写进 message/feedback，这里兜底保证 hint 有内容
        hint = str(ai.get("hint") or "").strip()
        if not hint:
            hint = str(ai.get("message") or ai.get("feedback") or "").strip()
        if not hint:
            hint = _lang_prefixed(
                lang,
                "先把已知角写出来，再想想三角形内角和还缺哪一个。",
                "Write down the known angles, then think which angle the triangle angle sum still needs.",
            )
        ai["hint"] = hint
        ai["completed"] = False  # 点提示不应直接判完成
        if not str(ai.get("message") or "").strip():
            ai["message"] = _lang_prefixed(
                lang,
                "看下面的提示，试着自己算一步。",
                "Use the hint below and try the next step yourself.",
            )
    preferred = session.get("vision_figure")
    # 立体锁定 / 原题图：始终作为 preferred，避免后续变成可拖边的平面图
    if want_hint and not ai.get("figure") and preferred:
        ai["figure"] = preferred
    elif preferred and not ai.get("figure"):
        ai["figure"] = preferred
    ai = _attach_figure(
        ai,
        session.get("problem_text", ""),
        preferred_figure=preferred,
        force_fallback=want_hint and not preferred,
    )
    if is_solid_figure(ai.get("figure_data")) and not session.get("vision_figure"):
        session["vision_figure"] = ai.get("figure_data")
    messages.append({"role": "assistant", "content": json.dumps(
        {k: v for k, v in ai.items() if k not in ("figure_svg", "figure_caption", "figure_data")},
        ensure_ascii=False,
    )})

    session["turns"] = session.get("turns", 0) + 1
    review = None
    if ai.get("completed"):
        session["completed"] = True
        session["final_solution"] = ai.get("final_solution") or ai.get("message", "")
        review = _finalize_review(session, ai)

    return {
        "ok": True,
        "session_id": session_id,
        "message": ai.get("message", ""),
        "feedback": ai.get("feedback", ""),
        "is_correct": ai.get("is_correct"),
        "hint": ai.get("hint", ""),
        "completed": bool(session.get("completed")),
        "final_solution": session.get("final_solution", ""),
        "review": review or session.get("review"),
        "turns": session["turns"],
        "figure_svg": ai.get("figure_svg"),
        "figure_caption": ai.get("figure_caption"),
        "figure_data": ai.get("figure_data"),
    }


def get_session(session_id: str) -> Optional[dict[str, Any]]:
    return SESSIONS.get(session_id)
