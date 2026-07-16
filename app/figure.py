"""把结构化几何描述渲染成 SVG（主要用于三角形提示配图）。"""

from __future__ import annotations

import math
from typing import Any, Optional

from .parser import parse_problem_text


def _parse_point(raw: Any) -> Optional[tuple[float, float]]:
    """解析归一化或像素坐标点，返回 (x, y)。"""
    if not isinstance(raw, dict):
        return None
    try:
        x = float(raw.get("x"))
        y = float(raw.get("y"))
    except (TypeError, ValueError):
        return None
    if not math.isfinite(x) or not math.isfinite(y):
        return None
    return (x, y)


def _normalize_points_map(
    raw_points: Any,
    img_w: Optional[float] = None,
    img_h: Optional[float] = None,
) -> dict[str, dict[str, float]]:
    """把 points 规范为整图像素比例 0~1（保留在图中的绝对位置，不做裁剪居中）。"""
    if not isinstance(raw_points, dict):
        return {}
    parsed: dict[str, tuple[float, float]] = {}
    for k, v in raw_points.items():
        name = str(k).upper().replace("∠", "").strip()[:3]
        pt = _parse_point(v)
        if name and pt:
            parsed[name] = pt
    if len(parsed) < 2:
        return {}

    xs = [p[0] for p in parsed.values()]
    ys = [p[1] for p in parsed.values()]
    max_x, max_y = max(xs), max(ys)

    # 像素坐标 → 除以整图宽高（不要用点集 min-max，否则叠原图会对不齐）
    if max_x > 1.5 or max_y > 1.5:
        dw = float(img_w) if img_w and img_w > 1 else max(max_x, 1.0)
        dh = float(img_h) if img_h and img_h > 1 else max(max_y, 1.0)
        return {
            name: {
                "x": min(1.0, max(0.0, x / dw)),
                "y": min(1.0, max(0.0, y / dh)),
            }
            for name, (x, y) in parsed.items()
        }

    return {
        name: {"x": min(1.0, max(0.0, x)), "y": min(1.0, max(0.0, y))}
        for name, (x, y) in parsed.items()
    }


def layout_points(
    figure: dict[str, Any],
    width: int = 360,
    height: int = 280,
    pad: float = 28.0,
    mode: str = "fit",
) -> dict[str, tuple[float, float]]:
    """把 figure.points（整图 0~1）映射到画布像素。

    mode:
      - fit: 把点集裁剪居中（聊天小图更好看）
      - image: 按整图比例铺满画布（与 object-fit:contain 叠原图一致）
    """
    verts = figure.get("vertices") or ["A", "B", "C"]
    a_name, b_name, c_name = verts[0], verts[1], verts[2]
    points = figure.get("points") or {}

    pts: dict[str, tuple[float, float]] = {}
    if isinstance(points, dict) and len(points) >= 3 and all(
        n in points for n in (a_name, b_name, c_name)
    ):
        if mode == "image":
            for name, p in points.items():
                pts[str(name)] = (float(p["x"]) * width, float(p["y"]) * height)
        else:
            xs = [float(points[n]["x"]) for n in points]
            ys = [float(points[n]["y"]) for n in points]
            min_x, max_x = min(xs), max(xs)
            min_y, max_y = min(ys), max(ys)
            span_x = max(max_x - min_x, 0.08)
            span_y = max(max_y - min_y, 0.08)
            usable_w = width - 2 * pad
            usable_h = height - 2 * pad
            scale = min(usable_w / span_x, usable_h / span_y)
            ox = pad + (usable_w - span_x * scale) / 2
            oy = pad + (usable_h - span_y * scale) / 2
            for name, p in points.items():
                pts[str(name)] = (
                    ox + (float(p["x"]) - min_x) * scale,
                    oy + (float(p["y"]) - min_y) * scale,
                )
    else:
        pts = {
            a_name: (60.0, 220.0),
            b_name: (180.0, 50.0),
            c_name: (300.0, 220.0),
        }

    for ep in figure.get("extra_points") or []:
        name = ep.get("name")
        on = str(ep.get("on") or "")
        if not name or len(on) < 2:
            continue
        if name in pts:
            continue
        p1, p2 = on[0], on[1]
        if p1 in pts and p2 in pts:
            t = float(ep.get("ratio", 0.5))
            pts[name] = _lerp(pts[p1], pts[p2], t)

    return pts


def normalize_figure(
    raw: Any,
    img_w: Optional[float] = None,
    img_h: Optional[float] = None,
) -> Optional[dict[str, Any]]:
    if not isinstance(raw, dict):
        return None
    ftype = str(raw.get("type") or "triangle").lower()
    if ftype not in ("triangle", "tri"):
        ftype = "triangle"

    vertices = raw.get("vertices") or ["A", "B", "C"]
    if not isinstance(vertices, list) or len(vertices) < 3:
        vertices = ["A", "B", "C"]
    vertices = [str(v).upper()[:3] for v in vertices[:3]]

    angle_labels = raw.get("angle_labels") or raw.get("angles") or {}
    if not isinstance(angle_labels, dict):
        angle_labels = {}
    angle_labels = {str(k).upper()[:3]: str(v) for k, v in angle_labels.items()}

    side_labels = raw.get("side_labels") or {}
    if not isinstance(side_labels, dict):
        side_labels = {}

    highlight = raw.get("highlight") or raw.get("highlight_angle")
    if highlight:
        highlight = str(highlight).upper().replace("∠", "").replace("ANGLE", "").strip()[:3]

    # 合并 points + 带坐标的辅助点，再统一归一化
    raw_points: dict[str, Any] = {}
    if isinstance(raw.get("points"), dict):
        raw_points.update(raw.get("points") or {})

    extra_points = []
    for p in raw.get("extra_points") or []:
        if not isinstance(p, dict):
            continue
        name = str(p.get("name") or "").upper()[:3]
        on = str(p.get("on") or "").upper().replace(" ", "")
        try:
            ratio = float(p.get("ratio", 0.5))
        except (TypeError, ValueError):
            ratio = 0.5
        ratio = min(0.92, max(0.08, ratio))
        if name and len(on) >= 2:
            extra_points.append({"name": name, "on": on[:2], "ratio": ratio})
        pt = _parse_point(p)
        if name and pt and name not in raw_points:
            raw_points[name] = {"x": pt[0], "y": pt[1]}

    points = _normalize_points_map(raw_points, img_w=img_w, img_h=img_h)

    # 保证三个主顶点有坐标；缺则用默认（仅兜底）
    for i, name in enumerate(vertices):
        if name not in points:
            defaults = [(0.15, 0.78), (0.50, 0.18), (0.85, 0.78)]
            x, y = defaults[min(i, 2)]
            points[name] = {"x": x, "y": y}

    segments = []
    for s in raw.get("segments") or []:
        if isinstance(s, (list, tuple)) and len(s) >= 2:
            segments.append([str(s[0]).upper()[:3], str(s[1]).upper()[:3]])

    caption = str(raw.get("caption") or "")[:80]

    return {
        "type": "triangle",
        "vertices": vertices,
        "points": points,
        "angle_labels": angle_labels,
        "side_labels": {str(k): str(v) for k, v in side_labels.items()},
        "highlight": highlight,
        "extra_points": extra_points,
        "segments": segments,
        "caption": caption,
    }


def figure_from_problem_text(text: str) -> Optional[dict[str, Any]]:
    """题目里有三角形/已知角时，自动生成一张基础示意图。"""
    problem = parse_problem_text(text)
    has_triangle = "三角" in text or "△" in text or "Δ" in text or "triangle" in text.lower()
    if not has_triangle and not problem.known_angles and not problem.find_targets:
        return None

    labels: dict[str, str] = {}
    for a in problem.known_angles:
        if a.value is not None:
            labels[a.name] = f"{a.value:g}°"
    for t in problem.find_targets:
        labels.setdefault(t, "?")

    # 默认 A/B/C
    for name in ("A", "B", "C"):
        labels.setdefault(name, "")

    highlight = problem.find_targets[0] if problem.find_targets else None
    return {
        "type": "triangle",
        "vertices": ["A", "B", "C"],
        "points": {
            "A": {"x": 0.15, "y": 0.78},
            "B": {"x": 0.50, "y": 0.18},
            "C": {"x": 0.85, "y": 0.78},
        },
        "angle_labels": {k: v for k, v in labels.items() if v},
        "side_labels": {},
        "highlight": highlight,
        "extra_points": [],
        "segments": [],
        "caption": "题目示意图",
    }


def _lerp(p1: tuple[float, float], p2: tuple[float, float], t: float) -> tuple[float, float]:
    return (p1[0] + (p2[0] - p1[0]) * t, p1[1] + (p2[1] - p1[1]) * t)


def _angle_at(vertex: tuple[float, float], p_prev: tuple[float, float], p_next: tuple[float, float]) -> tuple[float, float]:
    a1 = math.atan2(p_prev[1] - vertex[1], p_prev[0] - vertex[0])
    a2 = math.atan2(p_next[1] - vertex[1], p_next[0] - vertex[0])
    return a1, a2


def render_triangle_svg(figure: dict[str, Any], width: int = 360, height: int = 280) -> str:
    verts = figure.get("vertices") or ["A", "B", "C"]
    a_name, b_name, c_name = verts[0], verts[1], verts[2]
    pts = layout_points(figure, width=width, height=height)

    # 三角形边
    poly = f"{pts[a_name][0]},{pts[a_name][1]} {pts[b_name][0]},{pts[b_name][1]} {pts[c_name][0]},{pts[c_name][1]}"

    parts: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" role="img">',
        '<rect width="100%" height="100%" fill="#fffdf8"/>',
        f'<polygon points="{poly}" fill="#eef7f2" stroke="#1c2a24" stroke-width="2.5"/>',
    ]

    # 额外线段（如角平分线 AD）
    for s in figure.get("segments") or []:
        if s[0] in pts and s[1] in pts:
            x1, y1 = pts[s[0]]
            x2, y2 = pts[s[1]]
            parts.append(
                f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
                f'stroke="#0f6b4c" stroke-width="2" stroke-dasharray="6 4"/>'
            )

    highlight = figure.get("highlight")
    angle_labels = figure.get("angle_labels") or {}

    # 角标弧线 + 文字
    order = [a_name, b_name, c_name]
    for i, name in enumerate(order):
        prev_n = order[(i - 1) % 3]
        next_n = order[(i + 1) % 3]
        v = pts[name]
        a1, a2 = _angle_at(v, pts[prev_n], pts[next_n])
        # 取较小内角方向画弧
        diff = (a2 - a1) % (2 * math.pi)
        if diff > math.pi:
            a1, a2 = a2, a1
            diff = (a2 - a1) % (2 * math.pi)
        r = 28
        x1 = v[0] + r * math.cos(a1)
        y1 = v[1] + r * math.sin(a1)
        x2 = v[0] + r * math.cos(a2)
        y2 = v[1] + r * math.sin(a2)
        large = 1 if diff > math.pi else 0
        color = "#c45c26" if highlight and name == highlight else "#5a6b62"
        width_s = "2.5" if highlight and name == highlight else "1.5"
        parts.append(
            f'<path d="M {x1:.1f} {y1:.1f} A {r} {r} 0 {large} 1 {x2:.1f} {y2:.1f}" '
            f'fill="none" stroke="{color}" stroke-width="{width_s}"/>'
        )
        mid = a1 + diff / 2
        lx = v[0] + (r + 16) * math.cos(mid)
        ly = v[1] + (r + 16) * math.sin(mid)
        label = angle_labels.get(name, "")
        if label:
            parts.append(
                f'<text x="{lx:.1f}" y="{ly:.1f}" text-anchor="middle" dominant-baseline="middle" '
                f'font-size="14" font-family="Segoe UI, Microsoft YaHei, sans-serif" fill="{color}" '
                f'font-weight="700">{_escape(label)}</text>'
            )

    # 顶点字母
    offsets = {
        a_name: (-14, 10),
        b_name: (0, -14),
        c_name: (14, 10),
    }
    for name, (x, y) in pts.items():
        dx, dy = offsets.get(name, (0, -12))
        parts.append(
            f'<text x="{x + dx:.1f}" y="{y + dy:.1f}" text-anchor="middle" '
            f'font-size="16" font-family="Segoe UI, Microsoft YaHei, sans-serif" '
            f'font-weight="700" fill="#1c2a24">{_escape(name)}</text>'
        )
        parts.append(f'<circle cx="{x}" cy="{y}" r="3.5" fill="#1c2a24"/>')

    # 边长标签（可选）
    for key, val in (figure.get("side_labels") or {}).items():
        key_u = str(key).upper()
        if len(key_u) >= 2 and key_u[0] in pts and key_u[1] in pts:
            mx, my = _lerp(pts[key_u[0]], pts[key_u[1]], 0.5)
            parts.append(
                f'<text x="{mx:.1f}" y="{my - 10:.1f}" text-anchor="middle" font-size="12" '
                f'fill="#0f6b4c">{_escape(str(val))}</text>'
            )

    caption = figure.get("caption") or ""
    if caption:
        parts.append(
            f'<text x="{width / 2}" y="{height - 16}" text-anchor="middle" font-size="13" '
            f'fill="#5a6b62" font-family="Segoe UI, Microsoft YaHei, sans-serif">{_escape(caption)}</text>'
        )

    parts.append("</svg>")
    return "\n".join(parts)


def _escape(s: str) -> str:
    return (
        str(s)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def build_figure_payload(ai_figure: Any, problem_text: str = "") -> Optional[dict[str, Any]]:
    """返回供前端展示的 {svg, caption, figure}；失败则 None。"""
    fig = normalize_figure(ai_figure)
    if fig is None and problem_text:
        fig = figure_from_problem_text(problem_text)
    if fig is None:
        return None
    try:
        svg = render_triangle_svg(fig)
    except Exception:
        return None
    return {
        "svg": svg,
        "caption": fig.get("caption") or "",
        "figure": fig,
    }
