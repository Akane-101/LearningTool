"""从粘贴的题目文本中抽取解三角形相关信息（规则原型，非 OCR）。"""

from __future__ import annotations

import re
from .models import AngleFact, ParsedProblem

# 角度写法：∠A=50° / 角A=50度 / ∠BAC＝40° / 角BAC是70°
ANGLE_VALUE_PATTERNS = [
    re.compile(
        r"[∠角]\s*([A-Za-zΑ-Ωα-ω]{1,4})\s*[=＝是为]\s*(\d+(?:\.\d+)?)\s*[°度]?",
        re.I,
    ),
    re.compile(
        r"([A-Za-z]{1,4})\s*[=＝]\s*(\d+(?:\.\d+)?)\s*[°度]",
        re.I,
    ),
]

# 求：∠C / 求角C的度数 / 求∠ABC的大小
FIND_PATTERNS = [
    re.compile(r"求\s*[∠角]?\s*([A-Za-zΑ-Ωα-ω]{1,4})\s*(?:的)?\s*(?:度数|大小|度)?", re.I),
    re.compile(r"[∠角]\s*([A-Za-z]{1,4})\s*[=＝]\s*[?？_＿xX]", re.I),
]

KEYWORD_RULES: list[tuple[str, str, str]] = [
    # keyword_key, display, suggested reason
    ("平行", "两直线平行", "两直线平行，同位角（或内错角）相等"),
    ("同位角", "同位角", "两直线平行，同位角相等"),
    ("内错角", "内错角", "两直线平行，内错角相等"),
    ("同旁内角", "同旁内角", "两直线平行，同旁内角互补"),
    ("平分", "角平分线", "角平分线定义：平分后两角相等"),
    ("角平分线", "角平分线", "角平分线定义：平分后两角相等"),
    ("等腰", "等腰三角形", "等腰三角形两底角相等"),
    ("等边", "等边三角形", "等边三角形三个内角都是 60°"),
    ("直角", "直角三角形", "直角三角形两锐角互余"),
    ("外角", "三角形外角", "三角形外角等于不相邻两内角之和"),
    ("互补", "互补", "邻补角（或同旁内角）互补，和为 180°"),
    ("互余", "互余", "直角三角形两锐角互余，和为 90°"),
    ("对顶角", "对顶角", "对顶角相等"),
    ("邻补角", "邻补角", "邻补角互补，和为 180°"),
    ("内角和", "三角形内角和", "三角形内角和等于 180°"),
]


def _normalize(text: str) -> str:
    text = text.replace("／", "/").replace("，", ",").replace("。", ".")
    text = text.replace("：", ":").replace("（", "(").replace("）", ")")
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def _extract_known_angles(text: str) -> list[AngleFact]:
    found: dict[str, float] = {}
    for pat in ANGLE_VALUE_PATTERNS:
        for m in pat.finditer(text):
            name = m.group(1).upper()
            value = float(m.group(2))
            found[name] = value
    return [AngleFact(name=k, value=v) for k, v in found.items()]


def _extract_find_targets(text: str, known: list[AngleFact]) -> list[str]:
    known_names = {a.name for a in known}
    targets: list[str] = []
    for pat in FIND_PATTERNS:
        for m in pat.finditer(text):
            name = m.group(1).upper()
            if name not in known_names and name not in targets:
                targets.append(name)
    # 常见写法：求∠C
    for m in re.finditer(r"求\s*[∠角]\s*([A-Za-z]{1,4})", text, re.I):
        name = m.group(1).upper()
        if name not in known_names and name not in targets:
            targets.append(name)
    return targets


def _extract_keywords(text: str) -> tuple[list[str], list[str]]:
    keywords: list[str] = []
    reasons: list[str] = []
    for key, display, reason in KEYWORD_RULES:
        if key in text:
            if display not in keywords:
                keywords.append(display)
            if reason not in reasons:
                reasons.append(reason)
    # 默认兜底：三角形内角和（支持「三角」「△」）
    if (
        ("三角" in text or "△" in text or "Δ" in text)
        and "三角形内角和" not in keywords
    ):
        keywords.append("三角形内角和")
        reasons.append("三角形内角和等于 180°")
    # 有两个已知内角 + 一个所求角时，也倾向内角和
    return keywords, reasons


def _build_clues(known: list[AngleFact], targets: list[str], keywords: list[str]) -> list[str]:
    clues: list[str] = []
    if known:
        parts = [f"∠{a.name}={a.value:g}°" for a in known]
        clues.append("已知角度：" + "，".join(parts))
    if targets:
        clues.append("要求的角度：" + "，".join(f"∠{t}" for t in targets))
    if keywords:
        clues.append("可能用到的知识：" + "，".join(keywords))
    if not clues:
        clues.append("未能自动抽出具体角度，请人工确认题目信息后继续引导。")
    return clues


def _summary(known: list[AngleFact], targets: list[str], keywords: list[str]) -> str:
    known_s = "，".join(f"∠{a.name}={a.value:g}°" for a in known) or "（未识别到具体已知角）"
    target_s = "，".join(f"∠{t}" for t in targets) or "（未识别到所求角）"
    kw = "、".join(keywords[:3]) or "三角形基本性质"
    return f"识别结果：已知 {known_s}；求 {target_s}；线索偏向「{kw}」。"


def parse_problem_text(text: str) -> ParsedProblem:
    raw = text.strip()
    norm = _normalize(raw)
    known = _extract_known_angles(norm)
    targets = _extract_find_targets(norm, known)
    keywords, reasons = _extract_keywords(norm)
    # 两个已知角 + 一个所求角：常见就是内角和题
    if len(known) >= 2 and targets and "三角形内角和" not in keywords:
        keywords.append("三角形内角和")
        reasons.append("三角形内角和等于 180°")
    clues = _build_clues(known, targets, keywords)

    # 简单置信度：抽到已知角 + 所求角越高越好
    score = 0.2
    if known:
        score += 0.35
    if targets:
        score += 0.25
    if keywords:
        score += 0.2
    score = min(score, 0.95)

    unknowns = list(targets)
    for a in known:
        if a.name in unknowns:
            unknowns.remove(a.name)

    return ParsedProblem(
        raw_text=raw,
        summary=_summary(known, targets, keywords),
        known_angles=known,
        unknown_angles=unknowns,
        find_targets=targets,
        keywords=keywords,
        clues=clues,
        suggested_reasons=reasons,
        confidence=score,
    )
