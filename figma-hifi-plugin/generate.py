# -*- coding: utf-8 -*-
"""Generate high-fidelity Figma plugin code.js (UTF-8)."""
from __future__ import annotations

import json
from pathlib import Path

# All user-facing Chinese via unicode escapes (ASCII-safe source)
T = {
    "page": "Hi-Fi UI \u00b7 triangle-guide",
    "notify": "\u5df2\u751f\u6210\u9ad8\u4fdd\u771f UI\uff08\u65b0\u9875\u9762\uff09",
    "fail": "\u751f\u6210\u5931\u8d25: ",
    "cover": "\u89e3\u4e09\u89d2\u5f62 \u00b7 \u9ad8\u4fdd\u771f UI",
    "cover_sub": (
        "\u914d\u8272/\u4fa7\u680f/\u9996\u9875\u53cc\u5165\u53e3/\u753b\u677f\u5206\u680f "
        "\u5bf9\u9f50\u4f60\u7684 Figma \u00b7 \u72ec\u7acb\u65b0\u9875\uff0c\u4e0d\u6539\u539f\u6587\u4ef6"
    ),
    "s01": "01 Home \u00b7 \u9996\u9875",
    "s02": "02 Search \u00b7 \u641c\u7d22\u9898\u76ee",
    "s03": "03 Guide \u00b7 AI \u5f15\u5bfc",
    "s04": "04 Solid \u00b7 \u7acb\u4f53",
    "s05": "05 Done \u00b7 \u5b8c\u6574\u89e3\u7b54",
    "greet1": "\u65e9\u4e0a\u597d\uff0c",
    "greet2": "\u4eca\u5929\u60f3\u5b66\u70b9\u4ec0\u4e48\uff1f",
    "search": "\u641c\u7d22\u9898\u76ee",
    "search_desc": "\u62cd\u7167 / \u4e0a\u4f20 / \u7c98\u8d34\u622a\u56fe\uff0c\u81ea\u52a8\u8bc6\u5b57\u4e0e\u63cf\u6469\u51e0\u4f55\u56fe",
    "practice": "\u5feb\u901f\u7ec3\u4e60",
    "practice_desc": "\u9009\u793a\u4f8b\u9898\uff0cAI \u9010\u6b65\u5f15\u5bfc\uff1b\u652f\u6301\u5e73\u9762\u4e0e\u7acb\u4f53\u56fe\u5f62",
    "zh": "\u4e2d\u6587",
    "nav_home": "\u9996",
    "nav_prac": "\u7ec3",
    "nav_done": "\u89e3",
    "avatar": "\u5b66",
    "title_search": "\u641c\u7d22\u9898\u76ee",
    "status_geo": "\u5df2\u8bc6\u522b\u51e0\u4f55\u7ed3\u6784",
    "photo": "\u9898\u76ee\u7167\u7247",
    "photo_meta": "\u53ef\u53e0\u52a0\u539f\u56fe\u5bf9\u9f50 \u00b7 \u652f\u6301\u6e05\u7a7a\u91cd\u62cd",
    "clear": "\u6e05\u7a7a",
    "reshoot": "\u91cd\u62cd",
    "board": "\u753b\u677f",
    "plane": "\u5e73\u9762",
    "tools": [
        "\u62d6\u52a8",
        "\u8fd8\u539f\u56fe\u5f62",
        "\u753b\u7b14",
        "\u6a61\u76ae",
        "\u6e05\u7a7a\u6807\u6ce8",
        "\u793a\u610f\u56fe",
        "\u53e0\u52a0\u539f\u56fe",
        "\u53ea\u770b\u539f\u56fe",
    ],
    "prob_h": "\u9898\u76ee\u6587\u5b57",
    "editable": "\u53ef\u7f16\u8f91",
    "prob": (
        "\u5982\u56fe\uff0c\u5728\u25b3ABC\u4e2d\uff0cD\u3001E\u5206\u522b\u662fAB\u3001AC\u4e0a\u7684\u70b9\uff0c"
        "DE\u2225BC\uff0c\u2220ADE=70\u00b0\uff0c\u2220A=40\u00b0\uff0c\u6c42\u2220C\u7684\u5ea6\u6570\u3002"
    ),
    "voice": "\u8bed\u97f3\u8f93\u5165",
    "camera": "\u6253\u5f00\u6444\u50cf\u5934",
    "start": "\u5f00\u59cb AI \u5f15\u5bfc",
    "title_prac": "\u5feb\u901f\u7ec3\u4e60",
    "status_guide": "\u5df2\u5f00\u59cb\u5f15\u5bfc\uff0c\u8bf7\u5728\u4e0b\u65b9\u6309\u6b65\u9aa4\u4f5c\u7b54",
    "chips": [
        "2024\u00b7\u7b49\u8fb9\u4e09\u89d2\u5f62+\u5e73\u884c\u7ebf",
        "2022\u00b7\u5e73\u884c\u7ebf\u6c42\u89d2\u5ea6",
        "2023\u00b7\u4e09\u89d2\u5f62\u5916\u89d2\u6027\u8d28",
        "\u7acb\u4f53\u00b7\u6b63\u65b9\u4f53\u8868\u9762\u79ef",
    ],
    "board_meta": "\u793a\u610f\u56fe \u00b7 \u53ef\u53e0\u539f\u56fe",
    "ai_h": "AI \u5f15\u5bfc",
    "step": "\u9010\u6b65\u63a8\u8fdb",
    "who_ai": "AI",
    "who_you": "\u4f60",
    "who_hint": "\u63d0\u793a",
    "ai1": (
        "\u5148\u770b\u770b\u5df2\u77e5\u6761\u4ef6\uff1aDE\u2225BC\uff0c\u2220ADE=70\u00b0\uff0c\u2220A=40\u00b0\u3002"
        "\u4f60\u6253\u7b97\u600e\u4e48\u5229\u7528\u5e73\u884c\u7ebf\u6765\u627e\u2220C\uff1f"
    ),
    "me1": "\u540c\u4f4d\u89d2\u76f8\u7b49\uff1f",
    "hint1": (
        "\u5e73\u884c\u7ebf\u4f1a\u4ea7\u751f\u540c\u4f4d\u89d2\u3001\u5185\u9519\u89d2\u6216\u540c\u65c1\u5185\u89d2\uff0c"
        "\u60f3\u60f3\u54ea\u4e2a\u548c\u2220C\u6709\u5173\uff1f"
    ),
    "ai2": "\u65b9\u5411\u5bf9\u3002\u518d\u60f3\u4e00\u6b65\uff1a\u2220ADE \u4e0e\u54ea\u4e2a\u89d2\u662f\u540c\u4f4d\u89d2\uff1f",
    "ph": "\u5199\u4e0b\u4f60\u7684\u7b54\u6848\u6216\u601d\u8def",
    "hint_btn": "\u5361\u4f4f\u4e86\uff0c\u63d0\u793a\u4e00\u4e0b",
    "confirm": "\u786e\u8ba4",
    "fb": "\u53cd\u9988\uff1a\u601d\u8def\u6b63\u786e\uff0c\u7ee7\u7eed\u5f80\u4e0b\u63a8\u3002",
    "title_solid": "\u7acb\u4f53 \u00b7 \u6b63\u65b9\u4f53\u8868\u9762\u79ef",
    "status_3d": "3D \u65cb\u8f6c\u6a21\u5f0f",
    "solid_meta": "\u7acb\u4f53 \u00b7 \u5f62\u72b6\u9501\u5b9a",
    "rotate": "\u65cb\u8f6c",
    "pen": "\u753b\u7b14",
    "eraser": "\u6a61\u76ae",
    "clear_m": "\u6e05\u7a7a\u6807\u6ce8",
    "solid_ai": (
        "\u8fd9\u662f\u6b63\u65b9\u4f53\u8868\u9762\u79ef\u9898\u3002"
        "\u5148\u6570\u4e00\u6570\uff1a\u6b63\u65b9\u4f53\u4e00\u5171\u6709\u51e0\u4e2a\u9762\uff1f\u6bcf\u4e2a\u9762\u662f\u4ec0\u4e48\u5f62\u72b6\uff1f"
    ),
    "solid_ans": "6 \u4e2a\u6b63\u65b9\u5f62\u9762",
    "title_done": "\u5b8c\u6574\u89e3\u7b54",
    "copy": "\u590d\u5236\u5168\u6587",
    "writeup": (
        "\u3010\u9898\u76ee\u3011\n"
        "\u5982\u56fe\uff0c\u5728\u25b3ABC\u4e2d\uff0cD\u3001E\u5206\u522b\u662fAB\u3001AC\u4e0a\u7684\u70b9\uff0c"
        "DE\u2225BC\uff0c\u2220ADE=70\u00b0\uff0c\u2220A=40\u00b0\uff0c\u6c42\u2220C\u7684\u5ea6\u6570\u3002\n\n"
        "\u3010\u5206\u6790\u3011\n"
        "\u7531 DE\u2225BC\uff0c\u53ef\u5f97\u540c\u4f4d\u89d2\u76f8\u7b49\uff1b\u7ed3\u5408\u4e09\u89d2\u5f62\u5185\u89d2\u548c\u6c42 \u2220C\u3002\n\n"
        "\u3010\u89e3\u7b54\u3011\n"
        "\u2235 DE\u2225BC\n"
        "\u2234 \u2220ADE = \u2220ABC = 70\u00b0\uff08\u540c\u4f4d\u89d2\uff09\n"
        "\u2235 \u2220A = 40\u00b0\n"
        "\u2234 \u2220C = 180\u00b0 \u2212 40\u00b0 \u2212 70\u00b0 = 70\u00b0\n\n"
        "\u3010\u7b54\u6848\u3011 \u2220C = 70\u00b0"
    ),
    "footer": "\u7531 DeepSeek \u63d0\u4f9b\u89e3\u9898\u5f15\u5bfc \u00b7 \u6bcf\u6b21\u53ea\u63a8\u8fdb\u4e00\u6b65",
}


def j(s: str) -> str:
    return json.dumps(s, ensure_ascii=False)


def main() -> None:
    tools = ", ".join(j(x) for x in T["tools"])
    chips = ", ".join(j(x) for x in T["chips"])

    out = f'''/**
 * Triangle Guide Hi-Fi UI — Figma plugin
 * Creates a NEW page. Does not modify other pages.
 */

function hex(h) {{
  const n = h.replace("#", "");
  return {{
    r: parseInt(n.slice(0, 2), 16) / 255,
    g: parseInt(n.slice(2, 4), 16) / 255,
    b: parseInt(n.slice(4, 6), 16) / 255,
  }};
}}

const C = {{
  white: hex("#ffffff"),
  ink: hex("#0f172a"),
  muted: hex("#8796af"),
  line: hex("#dee4ee"),
  soft: hex("#f7f9fb"),
  softBlue: hex("#e1efff"),
  navy: hex("#123873"),
  orange: hex("#f15024"),
  ok: hex("#1f7a4c"),
  hintBg: hex("#fff8eb"),
  hintLine: hex("#e0b56a"),
  hintInk: hex("#6b4510"),
  dark: hex("#0f1c33"),
  pre: hex("#d7e0ef"),
  canvas: hex("#e8f0fa"),
  stageBg: hex("#eef1f6"),
}};

let FONT = {{ family: "Inter", style: "Regular" }};
let FONT_B = {{ family: "Inter", style: "Bold" }};
let FONT_M = {{ family: "Inter", style: "Medium" }};

function solid(color, opacity) {{
  return [{{ type: "SOLID", color: color, opacity: opacity == null ? 1 : opacity }}];
}}

function frame(name, x, y, w, h, opts) {{
  opts = opts || {{}};
  const f = figma.createFrame();
  f.name = name;
  f.x = x;
  f.y = y;
  f.resize(w, h);
  f.fills = opts.fills !== undefined ? opts.fills : solid(C.white);
  f.strokes = opts.strokes || [];
  f.strokeWeight = opts.strokeWeight == null ? 1 : opts.strokeWeight;
  if (opts.stroke) {{
    f.strokes = solid(opts.stroke);
    f.strokeWeight = opts.strokeWeight == null ? 1 : opts.strokeWeight;
  }}
  f.cornerRadius = opts.radius || 0;
  f.clipsContent = opts.clips !== false;
  if (opts.parent) opts.parent.appendChild(f);
  return f;
}}

function rect(parent, name, x, y, w, h, opts) {{
  opts = opts || {{}};
  const r = figma.createRectangle();
  r.name = name;
  r.x = x;
  r.y = y;
  r.resize(w, h);
  r.fills = opts.fills !== undefined ? opts.fills : solid(C.soft);
  r.strokes = opts.stroke ? solid(opts.stroke) : [];
  r.strokeWeight = opts.strokeWeight == null ? 1 : opts.strokeWeight;
  r.dashPattern = opts.dashed ? [5, 4] : [];
  r.cornerRadius = opts.radius || 0;
  parent.appendChild(r);
  return r;
}}

async function txt(parent, name, chars, x, y, size, opts) {{
  opts = opts || {{}};
  const t = figma.createText();
  t.name = name;
  let font = FONT;
  if (opts.bold) font = FONT_B;
  else if (opts.medium) font = FONT_M;
  t.fontName = font;
  t.characters = chars;
  t.fontSize = size;
  t.x = x;
  t.y = y;
  t.fills = solid(opts.color || C.ink);
  if (opts.w) {{
    t.resize(opts.w, t.height);
    t.textAutoResize = "HEIGHT";
  }}
  parent.appendChild(t);
  return t;
}}

async function btn(parent, label, x, y, w, h, kind) {{
  // kind: primary | navy | secondary | ghost | tool | toolOn | chip | chipOn
  let fill = C.white;
  let stroke = C.line;
  let color = C.ink;
  let sw = 1;
  let radius = 10;
  if (kind === "primary") {{
    fill = C.orange; stroke = C.orange; color = C.white; sw = 0;
  }} else if (kind === "navy") {{
    fill = C.navy; stroke = C.navy; color = C.white; sw = 0;
  }} else if (kind === "secondary") {{
    fill = C.white; stroke = C.line; color = C.navy;
  }} else if (kind === "ghost") {{
    fill = C.white; stroke = C.line; color = C.muted;
  }} else if (kind === "tool") {{
    fill = C.white; stroke = C.line; color = C.ink; radius = 8;
  }} else if (kind === "toolOn") {{
    fill = C.navy; stroke = C.navy; color = C.white; radius = 8; sw = 0;
  }} else if (kind === "chip") {{
    fill = C.white; stroke = C.line; color = C.muted; radius = 999;
  }} else if (kind === "chipOn") {{
    fill = C.softBlue; stroke = hex("#b7d0f0"); color = C.navy; radius = 999;
  }} else if (kind === "langOn") {{
    fill = C.navy; stroke = C.navy; color = C.white; radius = 8; sw = 0;
  }} else if (kind === "lang") {{
    fill = C.white; stroke = C.line; color = C.muted; radius = 8;
  }}
  const g = frame("btn/" + label, x, y, w, h, {{
    parent: parent,
    fills: solid(fill),
    stroke: stroke,
    strokeWeight: sw,
    radius: radius,
  }});
  const fs = kind === "tool" || kind === "toolOn" || kind === "chip" || kind === "chipOn" ? 11 : 12;
  await txt(g, "l", label, 8, Math.max(3, (h - fs) / 2 - 1), fs, {{
    color: color,
    bold: kind === "primary" || kind === "navy" || kind === "chipOn",
    w: w - 16,
  }});
  return g;
}}

async function sidebar(parent, active) {{
  const s = frame("sidebar", 0, 0, 72, parent.height, {{
    parent: parent,
    fills: solid(C.white),
    stroke: C.line,
    strokeWeight: 1,
  }});
  // logo
  const logo = frame("logo", 16, 18, 40, 40, {{
    parent: s,
    fills: solid(C.navy),
    strokeWeight: 0,
    radius: 12,
  }});
  await txt(logo, "t", "\\u25b3", 12, 8, 16, {{ color: C.white, bold: true }});

  const items = [
    {{ k: "home", label: {j(T["nav_home"])}, y: 78 }},
    {{ k: "prac", label: {j(T["nav_prac"])}, y: 130 }},
    {{ k: "done", label: {j(T["nav_done"])}, y: 182 }},
  ];
  for (let i = 0; i < items.length; i++) {{
    const it = items[i];
    const on = it.k === active;
    const b = frame("nav-" + it.k, 15, it.y, 42, 42, {{
      parent: s,
      fills: solid(on ? C.softBlue : C.white),
      strokeWeight: 0,
      radius: 12,
    }});
    await txt(b, "t", it.label, 13, 12, 13, {{ color: on ? C.navy : C.muted, bold: on }});
  }}

  const av = frame("avatar", 16, s.height - 56, 40, 40, {{
    parent: s,
    fills: solid(C.soft),
    stroke: C.line,
    strokeWeight: 2,
    radius: 999,
  }});
  await txt(av, "t", {j(T["avatar"])}, 11, 10, 13, {{ color: C.navy, bold: true }});
  const badge = figma.createEllipse();
  badge.resize(12, 12);
  badge.x = 42;
  badge.y = s.height - 28;
  badge.fills = solid(C.orange);
  badge.strokes = solid(C.white);
  badge.strokeWeight = 2;
  s.appendChild(badge);
  return s;
}}

async function deviceShell(page, name, x, y, activeNav) {{
  const outer = frame(name, x, y, 1180, 720, {{
    parent: page,
    fills: solid(C.stageBg),
    strokeWeight: 0,
    radius: 0,
  }});
  const device = frame("Device", 0, 40, 1180, 680, {{
    parent: outer,
    fills: solid(C.white),
    stroke: hex("#d0d7e4"),
    strokeWeight: 1,
    radius: 28,
  }});
  await sidebar(device, activeNav);
  const main = frame("main", 72, 0, 1108, 680, {{
    parent: device,
    fills: solid(C.soft),
    strokeWeight: 0,
  }});
  return {{ outer, device, main }};
}}

function triangle(parent, x, y) {{
  const poly = figma.createPolygon();
  poly.name = "triangle";
  poly.pointCount = 3;
  poly.resize(200, 160);
  poly.x = x;
  poly.y = y;
  poly.fills = solid(C.canvas);
  poly.strokes = solid(C.navy);
  poly.strokeWeight = 2.5;
  parent.appendChild(poly);
  return poly;
}}

async function buildCover(page) {{
  const c = frame("00 Cover", 0, 0, 1180, 200, {{
    parent: page,
    fills: solid(C.white),
    stroke: C.line,
    strokeWeight: 1,
    radius: 16,
  }});
  await txt(c, "t", {j(T["cover"])}, 36, 40, 28, {{ bold: true, w: 900 }});
  await txt(c, "s", {j(T["cover_sub"])}, 36, 90, 13, {{ color: C.muted, w: 1000 }});
  const swatches = [
    ["navy", C.navy],
    ["orange", C.orange],
    ["softBlue", C.softBlue],
    ["line", C.line],
  ];
  for (let i = 0; i < swatches.length; i++) {{
    rect(c, swatches[i][0], 36 + i * 56, 140, 40, 40, {{
      fills: solid(swatches[i][1]),
      radius: 10,
      stroke: C.line,
    }});
  }}
}}

async function buildHome(page, ox, oy) {{
  await txt(page, "label-01", {j(T["s01"])}, ox, oy - 28, 14, {{ bold: true, color: C.ink }});
  const {{ main }} = await deviceShell(page, "01 Home", ox, oy, "home");

  // lang
  await btn(main, {j(T["zh"])}, 980, 20, 52, 28, "langOn");
  await btn(main, "EN", 1038, 20, 40, 28, "lang");

  await txt(main, "g1", {j(T["greet1"])}, 280, 180, 36, {{ bold: true, w: 560 }});
  await txt(main, "g2", {j(T["greet2"])}, 280, 228, 36, {{ bold: true, color: C.navy, w: 560 }});

  const card1 = frame("entry-search", 200, 320, 320, 200, {{
    parent: main,
    fills: solid(C.white),
    stroke: C.line,
    strokeWeight: 1,
    radius: 20,
  }});
  const ico1 = frame("ico", 28, 28, 52, 52, {{
    parent: card1,
    fills: solid(C.softBlue),
    strokeWeight: 0,
    radius: 14,
  }});
  await txt(ico1, "i", "\\u0950", 14, 12, 18, {{ color: C.navy }});
  await txt(ico1, "cam", "CAM", 10, 16, 11, {{ color: C.navy, bold: true }});
  await txt(card1, "h", {j(T["search"])}, 28, 100, 18, {{ bold: true }});
  await txt(card1, "d", {j(T["search_desc"])}, 28, 132, 12, {{ color: C.muted, w: 260 }});

  const card2 = frame("entry-practice", 560, 320, 320, 200, {{
    parent: main,
    fills: solid(C.white),
    stroke: C.line,
    strokeWeight: 1,
    radius: 20,
  }});
  const ico2 = frame("ico", 28, 28, 52, 52, {{
    parent: card2,
    fills: solid(C.softBlue),
    strokeWeight: 0,
    radius: 14,
  }});
  await txt(ico2, "i", "DOC", 10, 16, 11, {{ color: C.navy, bold: true }});
  await txt(card2, "h", {j(T["practice"])}, 28, 100, 18, {{ bold: true }});
  await txt(card2, "d", {j(T["practice_desc"])}, 28, 132, 12, {{ color: C.muted, w: 260 }});
}}

async function buildSearch(page, ox, oy) {{
  await txt(page, "label-02", {j(T["s02"])}, ox, oy - 28, 14, {{ bold: true }});
  const {{ main }} = await deviceShell(page, "02 Search", ox, oy, "prac");

  await txt(main, "title", {j(T["title_search"])}, 24, 18, 18, {{ bold: true }});
  const pill = frame("pill", 880, 18, 180, 28, {{
    parent: main,
    fills: solid(C.white),
    stroke: C.line,
    strokeWeight: 1,
    radius: 999,
  }});
  const dot = figma.createEllipse();
  dot.resize(7, 7);
  dot.x = 12;
  dot.y = 10;
  dot.fills = solid(hex("#22c55e"));
  pill.appendChild(dot);
  await txt(pill, "t", {j(T["status_geo"])}, 28, 6, 11, {{ color: C.muted, w: 140 }});

  // left panel
  const left = frame("board-panel", 20, 60, 620, 580, {{
    parent: main,
    fills: solid(C.white),
    stroke: C.line,
    strokeWeight: 1,
    radius: 20,
  }});
  const strip = frame("upload", 0, 0, 620, 64, {{
    parent: left,
    fills: solid(C.soft),
    stroke: C.line,
    strokeWeight: 1,
  }});
  rect(strip, "thumb", 16, 10, 64, 44, {{ fills: solid(C.softBlue), radius: 8, stroke: C.line }});
  await txt(strip, "ph", {j(T["photo"])}, 96, 12, 13, {{ bold: true }});
  await txt(strip, "pm", {j(T["photo_meta"])}, 96, 34, 11, {{ color: C.muted, w: 300 }});
  await btn(strip, {j(T["clear"])}, 460, 18, 56, 28, "ghost");
  await btn(strip, {j(T["reshoot"])}, 524, 18, 56, 28, "ghost");

  await txt(left, "bh", {j(T["board"])}, 16, 78, 14, {{ bold: true }});
  await txt(left, "bm", {j(T["plane"])}, 70, 80, 11, {{ color: C.muted }});

  const tools = [{tools}];
  for (let i = 0; i < tools.length; i++) {{
    const on = i === 0 || i === 5;
    await btn(left, tools[i], 12 + (i % 4) * 148, 108 + Math.floor(i / 4) * 34, 140, 28, on ? "toolOn" : "tool");
  }}

  const stage = frame("stage", 16, 190, 588, 360, {{
    parent: left,
    fills: solid(C.soft),
    stroke: C.line,
    strokeWeight: 1,
    radius: 14,
  }});
  stage.dashPattern = [5, 4];
  rect(stage, "photo-ghost", 24, 24, 540, 312, {{
    fills: solid(C.softBlue, 0.35),
    stroke: C.muted,
    strokeWeight: 1,
    dashed: true,
    radius: 10,
  }});
  triangle(stage, 194, 100);

  // right
  const right = frame("prob-panel", 656, 60, 420, 580, {{
    parent: main,
    fills: solid(C.white),
    stroke: C.line,
    strokeWeight: 1,
    radius: 20,
  }});
  await txt(right, "h", {j(T["prob_h"])}, 16, 16, 14, {{ bold: true }});
  await txt(right, "m", {j(T["editable"])}, 100, 18, 11, {{ color: C.muted }});
  const box = frame("prob", 16, 48, 388, 420, {{
    parent: right,
    fills: solid(C.soft),
    stroke: C.line,
    strokeWeight: 1,
    radius: 12,
  }});
  await txt(box, "p", {j(T["prob"])}, 14, 14, 13, {{ w: 360 }});
  await btn(right, {j(T["voice"])}, 16, 490, 80, 32, "ghost");
  await btn(right, {j(T["camera"])}, 104, 490, 100, 32, "secondary");
  await btn(right, {j(T["start"])}, 240, 490, 164, 36, "primary");
}}

async function buildGuide(page, ox, oy) {{
  await txt(page, "label-03", {j(T["s03"])}, ox, oy - 28, 14, {{ bold: true }});
  const {{ main }} = await deviceShell(page, "03 Guide", ox, oy, "prac");

  await txt(main, "title", {j(T["title_prac"])}, 24, 16, 18, {{ bold: true }});
  const pill = frame("pill", 820, 16, 250, 28, {{
    parent: main,
    fills: solid(C.white),
    stroke: C.line,
    strokeWeight: 1,
    radius: 999,
  }});
  const dot = figma.createEllipse();
  dot.resize(7, 7);
  dot.x = 10;
  dot.y = 10;
  dot.fills = solid(hex("#22c55e"));
  pill.appendChild(dot);
  await txt(pill, "t", {j(T["status_guide"])}, 24, 6, 10, {{ color: C.muted, w: 210 }});

  const chips = [{chips}];
  for (let i = 0; i < chips.length; i++) {{
    await btn(main, chips[i], 20 + i * 200, 56, 190, 28, i === 0 ? "chipOn" : "chip");
  }}

  const left = frame("board", 20, 100, 560, 540, {{
    parent: main,
    fills: solid(C.white),
    stroke: C.line,
    strokeWeight: 1,
    radius: 20,
  }});
  await txt(left, "h", {j(T["board"])}, 16, 14, 14, {{ bold: true }});
  await txt(left, "m", {j(T["board_meta"])}, 70, 16, 11, {{ color: C.muted }});
  const t2 = [{j(T["tools"][0])}, {j(T["tools"][2])}, {j(T["tools"][3])}, {j(T["tools"][4])}, {j(T["tools"][5])}, {j(T["tools"][6])}, {j(T["tools"][7])}];
  for (let i = 0; i < t2.length; i++) {{
    const on = i === 0 || i === 4;
    await btn(left, t2[i], 12 + i * 76, 44, 72, 26, on ? "toolOn" : "tool");
  }}
  const stage = frame("stage", 16, 86, 528, 420, {{
    parent: left,
    fills: solid(C.soft),
    stroke: C.line,
    strokeWeight: 1,
    radius: 14,
  }});
  triangle(stage, 164, 120);

  const right = frame("chat", 600, 100, 480, 540, {{
    parent: main,
    fills: solid(C.white),
    stroke: C.line,
    strokeWeight: 1,
    radius: 20,
  }});
  await txt(right, "h", {j(T["ai_h"])}, 16, 14, 14, {{ bold: true }});
  await txt(right, "m", {j(T["step"])}, 100, 16, 11, {{ color: C.muted }});

  const b1 = frame("ai1", 16, 48, 400, 78, {{
    parent: right,
    fills: solid(C.soft),
    stroke: C.line,
    strokeWeight: 1,
    radius: 14,
  }});
  await txt(b1, "w", {j(T["who_ai"])}, 12, 8, 10, {{ color: C.muted, bold: true }});
  await txt(b1, "t", {j(T["ai1"])}, 12, 26, 12, {{ w: 376 }});

  const b2 = frame("me1", 64, 140, 400, 44, {{
    parent: right,
    fills: solid(C.navy),
    strokeWeight: 0,
    radius: 14,
  }});
  await txt(b2, "w", {j(T["who_you"])}, 12, 6, 10, {{ color: C.white }});
  await txt(b2, "t", {j(T["me1"])}, 12, 22, 12, {{ color: C.white, w: 376 }});

  const b3 = frame("hint", 16, 200, 400, 64, {{
    parent: right,
    fills: solid(C.hintBg),
    stroke: C.hintLine,
    strokeWeight: 1,
    radius: 14,
  }});
  b3.dashPattern = [4, 3];
  await txt(b3, "w", {j(T["who_hint"])}, 12, 8, 10, {{ color: C.hintInk, bold: true }});
  await txt(b3, "t", {j(T["hint1"])}, 12, 26, 12, {{ color: C.hintInk, w: 376 }});

  const b4 = frame("ai2", 16, 280, 400, 50, {{
    parent: right,
    fills: solid(C.soft),
    stroke: C.line,
    strokeWeight: 1,
    radius: 14,
  }});
  await txt(b4, "t", {j(T["ai2"])}, 12, 14, 12, {{ w: 376 }});

  const ta = frame("input", 16, 360, 448, 70, {{
    parent: right,
    fills: solid(C.soft),
    stroke: C.line,
    strokeWeight: 1,
    radius: 12,
  }});
  await txt(ta, "ph", {j(T["ph"])}, 12, 12, 12, {{ color: C.muted, w: 420 }});
  await btn(right, {j(T["voice"])}, 16, 448, 80, 32, "ghost");
  await btn(right, {j(T["hint_btn"])}, 104, 448, 140, 32, "secondary");
  await btn(right, {j(T["confirm"])}, 360, 448, 88, 34, "primary");
  await txt(right, "fb", {j(T["fb"])}, 16, 500, 12, {{ color: C.ok, w: 400 }});
}}

async function buildSolid(page, ox, oy) {{
  await txt(page, "label-04", {j(T["s04"])}, ox, oy - 28, 14, {{ bold: true }});
  const {{ main }} = await deviceShell(page, "04 Solid", ox, oy, "prac");
  await txt(main, "title", {j(T["title_solid"])}, 24, 18, 18, {{ bold: true }});
  const pill = frame("pill", 920, 18, 140, 28, {{
    parent: main,
    fills: solid(C.white),
    stroke: C.line,
    strokeWeight: 1,
    radius: 999,
  }});
  await txt(pill, "t", {j(T["status_3d"])}, 14, 6, 11, {{ color: C.muted, w: 120 }});

  const left = frame("board", 20, 60, 560, 580, {{
    parent: main,
    fills: solid(C.white),
    stroke: C.line,
    strokeWeight: 1,
    radius: 20,
  }});
  await txt(left, "h", {j(T["board"])}, 16, 14, 14, {{ bold: true }});
  await txt(left, "m", {j(T["solid_meta"])}, 70, 16, 11, {{ color: C.muted }});
  await btn(left, {j(T["rotate"])}, 12, 48, 64, 28, "toolOn");
  await btn(left, {j(T["pen"])}, 84, 48, 56, 28, "tool");
  await btn(left, {j(T["eraser"])}, 148, 48, 56, 28, "tool");
  await btn(left, {j(T["clear_m"])}, 212, 48, 88, 28, "tool");
  const stage = frame("stage", 16, 96, 528, 440, {{
    parent: left,
    fills: solid(C.soft),
    stroke: C.line,
    strokeWeight: 1,
    radius: 14,
  }});
  rect(stage, "cube", 204, 150, 120, 120, {{
    fills: solid(C.softBlue, 0.8),
    stroke: C.navy,
    strokeWeight: 2,
    radius: 4,
  }});

  const right = frame("chat", 600, 60, 480, 580, {{
    parent: main,
    fills: solid(C.white),
    stroke: C.line,
    strokeWeight: 1,
    radius: 20,
  }});
  await txt(right, "h", {j(T["ai_h"])}, 16, 14, 14, {{ bold: true }});
  const b = frame("ai", 16, 48, 448, 70, {{
    parent: right,
    fills: solid(C.soft),
    stroke: C.line,
    strokeWeight: 1,
    radius: 14,
  }});
  await txt(b, "t", {j(T["solid_ai"])}, 12, 14, 12, {{ w: 420 }});
  const ta = frame("ans", 16, 140, 448, 70, {{
    parent: right,
    fills: solid(C.soft),
    stroke: C.line,
    strokeWeight: 1,
    radius: 12,
  }});
  await txt(ta, "t", {j(T["solid_ans"])}, 12, 14, 13, {{ w: 420 }});
  await btn(right, {j(T["hint_btn"])}, 16, 230, 140, 34, "secondary");
  await btn(right, {j(T["confirm"])}, 360, 230, 88, 34, "primary");
}}

async function buildDone(page, ox, oy) {{
  await txt(page, "label-05", {j(T["s05"])}, ox, oy - 28, 14, {{ bold: true }});
  const {{ main }} = await deviceShell(page, "05 Done", ox, oy, "done");
  await txt(main, "title", {j(T["title_done"])}, 24, 18, 18, {{ bold: true }});
  await btn(main, {j(T["copy"])}, 960, 14, 110, 36, "primary");

  const pre = frame("writeup", 24, 70, 1050, 520, {{
    parent: main,
    fills: solid(C.dark),
    strokeWeight: 0,
    radius: 20,
  }});
  await txt(pre, "body", {j(T["writeup"])}, 28, 28, 13, {{ color: C.pre, w: 990 }});
  await txt(main, "foot", {j(T["footer"])}, 24, 610, 11, {{ color: C.muted, w: 600 }});
}}

async function main() {{
  try {{
    await figma.loadFontAsync({{ family: "Inter", style: "Regular" }});
    await figma.loadFontAsync({{ family: "Inter", style: "Bold" }});
    try {{
      await figma.loadFontAsync({{ family: "Inter", style: "Medium" }});
    }} catch (e) {{
      FONT_M = FONT_B;
    }}
  }} catch (e) {{
    FONT = {{ family: "Roboto", style: "Regular" }};
    FONT_B = {{ family: "Roboto", style: "Bold" }};
    FONT_M = FONT_B;
    await figma.loadFontAsync(FONT);
    await figma.loadFontAsync(FONT_B);
  }}

  const page = figma.createPage();
  page.name = {j(T["page"])};
  await figma.setCurrentPageAsync(page);

  await buildCover(page);
  await buildHome(page, 0, 260);
  await buildSearch(page, 0, 1100);
  await buildGuide(page, 0, 1960);
  await buildSolid(page, 0, 2820);
  await buildDone(page, 0, 3680);

  figma.viewport.scrollAndZoomIntoView(page.children);
  figma.notify({j(T["notify"])});
  figma.closePlugin();
}}

main().catch(function (err) {{
  figma.notify({j(T["fail"])} + String(err));
  figma.closePlugin();
}});
'''

    dest = Path(__file__).with_name("code.js")
    dest.write_text(out, encoding="utf-8")
    text = dest.read_text(encoding="utf-8")
    assert "早上好" in text
    assert "开始 AI 引导" in text
    assert "#f15024" in text or "f15024" in text
    print("OK", dest, dest.stat().st_size, "bytes")


if __name__ == "__main__":
    main()
