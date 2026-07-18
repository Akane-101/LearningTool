"""初中立体几何：结构化立体图形 + 斜二测/等轴 SVG 示意图。"""

from __future__ import annotations

import math
import re
from typing import Any, Optional

SOLID_TYPES = {
    "solid",
    "cube",
    "rectangular_prism",
    "box",
    "cuboid",
    "triangular_prism",
    "square_pyramid",
    "pyramid",
    "cylinder",
    "cone",
}

_ALIAS = {
    "box": "rectangular_prism",
    "cuboid": "rectangular_prism",
    "rectangular": "rectangular_prism",
    "长方体": "rectangular_prism",
    "正方体": "cube",
    "立方体": "cube",
    "三棱柱": "triangular_prism",
    "四棱锥": "square_pyramid",
    "棱锥": "square_pyramid",
    "pyramid": "square_pyramid",
    "圆柱": "cylinder",
    "圆锥": "cone",
}


def is_solid_figure(raw: Any) -> bool:
    if not isinstance(raw, dict):
        return False
    t = str(raw.get("type") or "").lower()
    s = str(raw.get("solid") or "").lower()
    return t in SOLID_TYPES or s in SOLID_TYPES or t in _ALIAS or s in _ALIAS


def _num(v: Any, default: float) -> float:
    try:
        x = float(v)
    except (TypeError, ValueError):
        return default
    if not math.isfinite(x) or x <= 0:
        return default
    return x


def _canon_solid(raw: dict[str, Any]) -> str:
    t = str(raw.get("solid") or raw.get("type") or "cube").lower().strip()
    t = _ALIAS.get(t, t)
    if t == "solid":
        t = "cube"
    if t not in (
        "cube",
        "rectangular_prism",
        "triangular_prism",
        "square_pyramid",
        "cylinder",
        "cone",
    ):
        t = "cube"
    return t


def normalize_solid(
    raw: Any,
    img_w: Optional[float] = None,
    img_h: Optional[float] = None,
) -> Optional[dict[str, Any]]:
    del img_w, img_h  # 立体图暂不用像素对齐
    if not isinstance(raw, dict) or not is_solid_figure(raw):
        return None

    solid = _canon_solid(raw)
    dims_in = raw.get("dims") if isinstance(raw.get("dims"), dict) else {}
    length = _num(dims_in.get("length") or dims_in.get("a") or dims_in.get("l"), 4.0)
    width = _num(dims_in.get("width") or dims_in.get("b") or dims_in.get("w"), 3.0)
    height = _num(dims_in.get("height") or dims_in.get("c") or dims_in.get("h"), 5.0)
    radius = _num(dims_in.get("radius") or dims_in.get("r"), 2.0)

    if solid == "cube":
        edge = _num(
            dims_in.get("edge") or dims_in.get("side") or dims_in.get("a") or length,
            4.0,
        )
        length = width = height = edge

    labels = raw.get("labels") if isinstance(raw.get("labels"), dict) else {}
    labels = {str(k)[:24]: str(v)[:24] for k, v in labels.items()}

    edge_labels = raw.get("edge_labels") if isinstance(raw.get("edge_labels"), dict) else {}
    edge_labels = {str(k)[:8]: str(v)[:24] for k, v in edge_labels.items()}

    highlight_edges = []
    for e in raw.get("highlight_edges") or []:
        if isinstance(e, (list, tuple)) and len(e) >= 2:
            highlight_edges.append([str(e[0])[:3], str(e[1])[:3]])
        elif isinstance(e, str) and len(e) >= 2:
            highlight_edges.append([e[0].upper(), e[1].upper()])

    caption = str(raw.get("caption") or "")[:80]

    return {
        "type": "solid",
        "solid": solid,
        "dims": {
            "length": length,
            "width": width,
            "height": height,
            "radius": radius,
        },
        "labels": labels,
        "edge_labels": edge_labels,
        "highlight_edges": highlight_edges,
        "caption": caption,
    }


def figure_solid_from_text(text: str) -> Optional[dict[str, Any]]:
    """从题干关键词推断一种常见立体，并尽量抽出尺寸数字。"""
    if not text:
        return None
    t = text
    tl = text.lower()

    solid = None
    if any(k in t for k in ("正方体", "立方体")) or "cube" in tl:
        solid = "cube"
    elif any(k in t for k in ("长方体",)) or "rectangular" in tl or "cuboid" in tl:
        solid = "rectangular_prism"
    elif "三棱柱" in t or "triangular prism" in tl:
        solid = "triangular_prism"
    elif any(k in t for k in ("四棱锥", "棱锥")) or "pyramid" in tl:
        solid = "square_pyramid"
    elif "圆柱" in t or "cylinder" in tl:
        solid = "cylinder"
    elif "圆锥" in t or "cone" in tl:
        solid = "cone"
    elif any(k in t for k in ("立体", "表面积", "体积", "展开图")):
        # 泛立体题默认长方体示意
        solid = "rectangular_prism"
    else:
        return None

    nums = [float(x) for x in re.findall(r"(\d+(?:\.\d+)?)\s*(?:cm|m|mm)?", t)]
    dims = {"length": 4.0, "width": 3.0, "height": 5.0, "radius": 2.0}
    labels: dict[str, str] = {}

    if solid == "cube":
        edge = nums[0] if nums else 4.0
        dims = {"length": edge, "width": edge, "height": edge, "radius": edge / 2}
        labels["edge"] = f"{edge:g}" if nums else "a"
        caption = "正方体示意图"
    elif solid == "rectangular_prism":
        if len(nums) >= 3:
            dims["length"], dims["width"], dims["height"] = nums[0], nums[1], nums[2]
            labels = {"length": f"{nums[0]:g}", "width": f"{nums[1]:g}", "height": f"{nums[2]:g}"}
        else:
            labels = {"length": "a", "width": "b", "height": "h"}
        caption = "长方体示意图"
    elif solid == "cylinder":
        if len(nums) >= 2:
            dims["radius"], dims["height"] = nums[0], nums[1]
            labels = {"radius": f"{nums[0]:g}", "height": f"{nums[1]:g}"}
        else:
            labels = {"radius": "r", "height": "h"}
        caption = "圆柱示意图"
    elif solid == "cone":
        if len(nums) >= 2:
            dims["radius"], dims["height"] = nums[0], nums[1]
            labels = {"radius": f"{nums[0]:g}", "height": f"{nums[1]:g}"}
        else:
            labels = {"radius": "r", "height": "h"}
        caption = "圆锥示意图"
    elif solid == "triangular_prism":
        if len(nums) >= 2:
            dims["length"], dims["height"] = nums[0], nums[1]
            labels = {"length": f"{nums[0]:g}", "height": f"{nums[1]:g}"}
        else:
            labels = {"length": "a", "height": "h"}
        caption = "三棱柱示意图"
    else:
        if len(nums) >= 2:
            dims["length"], dims["height"] = nums[0], nums[1]
            labels = {"length": f"{nums[0]:g}", "height": f"{nums[1]:g}"}
        else:
            labels = {"length": "a", "height": "h"}
        caption = "四棱锥示意图"

    return normalize_solid(
        {
            "type": "solid",
            "solid": solid,
            "dims": dims,
            "labels": labels,
            "caption": caption,
        }
    )


def _project(x: float, y: float, z: float, scale: float, ox: float, oy: float) -> tuple[float, float]:
    """斜二测：x 水平，y 进深（半角），z 竖直向上（屏幕 y 向下）。"""
    sx = ox + scale * (x + 0.5 * y)
    sy = oy - scale * (z + 0.5 * y)
    return sx, sy


def _mesh(solid: str, dims: dict[str, float]) -> tuple[dict[str, tuple[float, float, float]], list[tuple[str, str]]]:
    L = dims["length"]
    W = dims["width"]
    H = dims["height"]
    R = dims["radius"]

    if solid == "cube":
        a = L
        pts = {
            "A": (0, 0, 0),
            "B": (a, 0, 0),
            "C": (a, a, 0),
            "D": (0, a, 0),
            "E": (0, 0, a),
            "F": (a, 0, a),
            "G": (a, a, a),
            "H": (0, a, a),
        }
        edges = [
            ("A", "B"), ("B", "C"), ("C", "D"), ("D", "A"),
            ("E", "F"), ("F", "G"), ("G", "H"), ("H", "E"),
            ("A", "E"), ("B", "F"), ("C", "G"), ("D", "H"),
        ]
        return pts, edges

    if solid == "rectangular_prism":
        pts = {
            "A": (0, 0, 0),
            "B": (L, 0, 0),
            "C": (L, W, 0),
            "D": (0, W, 0),
            "E": (0, 0, H),
            "F": (L, 0, H),
            "G": (L, W, H),
            "H": (0, W, H),
        }
        edges = [
            ("A", "B"), ("B", "C"), ("C", "D"), ("D", "A"),
            ("E", "F"), ("F", "G"), ("G", "H"), ("H", "E"),
            ("A", "E"), ("B", "F"), ("C", "G"), ("D", "H"),
        ]
        return pts, edges

    if solid == "triangular_prism":
        pts = {
            "A": (0, 0, 0),
            "B": (L, 0, 0),
            "C": (L * 0.5, W, 0),
            "D": (0, 0, H),
            "E": (L, 0, H),
            "F": (L * 0.5, W, H),
        }
        edges = [
            ("A", "B"), ("B", "C"), ("C", "A"),
            ("D", "E"), ("E", "F"), ("F", "D"),
            ("A", "D"), ("B", "E"), ("C", "F"),
        ]
        return pts, edges

    if solid == "square_pyramid":
        pts = {
            "A": (0, 0, 0),
            "B": (L, 0, 0),
            "C": (L, W, 0),
            "D": (0, W, 0),
            "S": (L * 0.5, W * 0.5, H),
        }
        edges = [
            ("A", "B"), ("B", "C"), ("C", "D"), ("D", "A"),
            ("A", "S"), ("B", "S"), ("C", "S"), ("D", "S"),
        ]
        return pts, edges

    # cylinder / cone: approximate with polygons for SVG
    n = 12
    pts = {}
    edges = []
    for i in range(n):
        ang = 2 * math.pi * i / n
        x = R + R * math.cos(ang)
        y = R + R * math.sin(ang)
        pts[f"B{i}"] = (x, y, 0.0)
        if solid == "cylinder":
            pts[f"T{i}"] = (x, y, H)
            edges.append((f"B{i}", f"B{(i + 1) % n}"))
            edges.append((f"T{i}", f"T{(i + 1) % n}"))
            if i % 3 == 0:
                edges.append((f"B{i}", f"T{i}"))
        else:
            edges.append((f"B{i}", f"B{(i + 1) % n}"))
            edges.append((f"B{i}", "S"))
    if solid == "cone":
        pts["S"] = (R, R, H)
    return pts, edges


def render_solid_svg(figure: dict[str, Any], width: int = 360, height: int = 280) -> str:
    solid = str(figure.get("solid") or "cube")
    dims = figure.get("dims") or {}
    pts3, edges = _mesh(solid, {
        "length": float(dims.get("length", 4)),
        "width": float(dims.get("width", 3)),
        "height": float(dims.get("height", 5)),
        "radius": float(dims.get("radius", 2)),
    })

    xs = [p[0] for p in pts3.values()]
    ys = [p[1] for p in pts3.values()]
    zs = [p[2] for p in pts3.values()]
    # center
    cx = (min(xs) + max(xs)) / 2
    cy = (min(ys) + max(ys)) / 2
    cz = (min(zs) + max(zs)) / 2
    centered = {k: (x - cx, y - cy, z - cz) for k, (x, y, z) in pts3.items()}

    # estimate scale
    proj = [_project(x, y, z, 1.0, 0, 0) for x, y, z in centered.values()]
    min_px = min(p[0] for p in proj)
    max_px = max(p[0] for p in proj)
    min_py = min(p[1] for p in proj)
    max_py = max(p[1] for p in proj)
    span = max(max_px - min_px, max_py - min_py, 1e-6)
    pad = 36.0
    scale = min((width - 2 * pad) / span, (height - 2 * pad) / span)
    ox = width / 2 - scale * (min_px + max_px) / 2
    oy = height / 2 - scale * (min_py + max_py) / 2

    proj2 = {k: _project(x, y, z, scale, ox, oy) for k, (x, y, z) in centered.items()}

    hi = {tuple(sorted(e)) for e in (figure.get("highlight_edges") or [])}
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" role="img">',
        '<rect width="100%" height="100%" fill="#fffdf8"/>',
    ]

    # hidden-ish: draw farther edges thinner first by average y (depth)
    def depth(e: tuple[str, str]) -> float:
        a, b = e
        return (centered[a][1] + centered[b][1]) / 2

    for a, b in sorted(edges, key=depth):
        if a not in proj2 or b not in proj2:
            continue
        x1, y1 = proj2[a]
        x2, y2 = proj2[b]
        key = tuple(sorted((a[:1] if len(a) > 1 and a[0].isalpha() else a, b[:1] if len(b) > 1 else b)))
        # simplify highlight match for labeled verts
        is_hi = tuple(sorted((a, b))) in hi or tuple(sorted((a[0], b[0]))) in {
            tuple(sorted(x)) for x in hi
        }
        color = "#c45c26" if is_hi else "#1c2a24"
        width_s = "2.8" if is_hi else "2.2"
        # back edges dashed for polyhedra
        back = depth((a, b)) > 0.15 * max(abs(max(ys) - min(ys)), 1)
        dash = ' stroke-dasharray="5 4"' if back and solid not in ("cylinder", "cone") else ""
        parts.append(
            f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{width_s}"{dash}/>'
        )

    # vertex labels for polyhedra
    if solid in ("cube", "rectangular_prism", "triangular_prism", "square_pyramid"):
        for name, (x, y) in proj2.items():
            if len(name) > 2:
                continue
            parts.append(
                f'<text x="{x + 8:.1f}" y="{y - 6:.1f}" font-size="13" font-weight="700" '
                f'fill="#1c2a24" font-family="Segoe UI, Microsoft YaHei, sans-serif">{_escape(name)}</text>'
            )

    labels = figure.get("labels") or {}
    if labels:
        bits = " · ".join(f"{k}={v}" for k, v in list(labels.items())[:4])
        parts.append(
            f'<text x="{width / 2}" y="22" text-anchor="middle" font-size="13" fill="#0f6b4c" '
            f'font-family="Segoe UI, Microsoft YaHei, sans-serif">{_escape(bits)}</text>'
        )

    caption = figure.get("caption") or ""
    if caption:
        parts.append(
            f'<text x="{width / 2}" y="{height - 14}" text-anchor="middle" font-size="13" '
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
