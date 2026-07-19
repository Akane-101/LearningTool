# -*- coding: utf-8 -*-
"""Generate code.js with proper UTF-8 Chinese text."""
from pathlib import Path

# Chinese strings as unicode escapes so this file stays ASCII-safe in transit
C = {
    "cover_title": "\u89e3\u4e09\u89d2\u5f62 AI \u5f15\u5bfc \u00b7 UI Wireframe v2",
    "cover_sub": (
        "\u57fa\u4e8e\u73b0\u6709\u529f\u80fd + \u7ebf\u4e0a UI \u91cd\u7ed8 \u00b7 "
        "\u72ec\u7acb\u65b0\u9875\uff0c\u672a\u6539\u52a8\u539f Untitled Figma\n"
        "\u8986\u76d6\uff1a\u591a\u5165\u53e3\u51fa\u9898 \u00b7 OCR \u00b7 \u8bed\u97f3 \u00b7 "
        "\u793a\u4f8b \u00b7 AI \u5bf9\u8bdd \u00b7 \u5e73\u9762\u53e0\u56fe \u00b7 "
        "\u7acb\u4f53\u65cb\u8f6c \u00b7 \u5b8c\u6574\u89e3\u7b54 \u00b7 \u4e2d\u82f1 \u00b7 \u79fb\u52a8\u7aef"
    ),
    "steps": [
        "01 \u8f93\u5165",
        "02 \u8bc6\u56fe",
        "03 \u6444\u50cf\u5934",
        "04 \u5f15\u5bfc\u00b7\u5e73\u9762",
        "05 \u5f15\u5bfc\u00b7\u7acb\u4f53",
        "06 \u5b8c\u6210",
        "07 \u79fb\u52a8\u7aef",
    ],
    "legend": (
        "\u56fe\u4f8b\uff1a\u5b9e\u7ebf\u6846=\u5185\u5bb9\u533a \u00b7 \u865a\u7ebf\u6846=\u6295\u653e\u533a "
        "\u00b7 \u7ea2\u70b9=\u5173\u952e\u4ea4\u4e92 \u00b7 \u84dd\u5361\u7247=\u6ce8\u91ca\n"
        "\u751f\u6210\u65b9\u5f0f\uff1a\u672c\u5730\u63d2\u4ef6 Triangle Guide Wireframe v2"
        "\uff08\u4ed3\u5e93 figma-wireframe-plugin/\uff09"
    ),
    "s01": "SCREEN 01 \u00b7 \u9996\u9875\u8f93\u5165",
    "url_home": "127.0.0.1:8001 \u2014 AI \u89e3\u9898\u5f15\u5bfc",
    "nav": ["\u9898", "\u804a", "\u89e3"],
    "zh": "\u4e2d",
    "h1": "AI \u5e26\u4f60\u4e00\u6b65\u4e00\u6b65\u89e3\u9898",
    "sub": "\u62cd\u7167\u770b\u56fe + \u6587\u5b57 \u2192 \u8bc6\u51e0\u4f55\u56fe \u00b7 \u9010\u6b65\u5f15\u5bfc",
    "lang_zh": "\u4e2d\u6587",
    "drop1": "\u62d6\u5165\u9898\u76ee\u56fe\u7247 / Ctrl+V \u7c98\u8d34",
    "drop2": "\u4e5f\u652f\u6301\u76f8\u518c\u3001\u62cd\u7167\u3001\u6253\u5f00\u6444\u50cf\u5934",
    "upload": "\u4e0a\u4f20\u56fe\u7247",
    "photo": "\u62cd\u7167",
    "open_cam": "\u6253\u5f00\u6444\u50cf\u5934",
    "clear_img": "\u6e05\u7a7a\u56fe\u7247",
    "prob_label": "\u9898\u76ee\u6587\u5b57\uff08\u53ef\u6539\uff0c\u53ef\u542b\u5df2\u6709\u8fc7\u7a0b\uff09",
    "voice": "\u8bed\u97f3\u8f93\u5165",
    "clear_txt": "\u6e05\u7a7a\u6587\u5b57",
    "ph_prob": "\u5728\u6b64\u8f93\u5165\u6216\u7c98\u8d34\u9898\u76ee\u6587\u5b57\u2026",
    "samples": "\u5feb\u901f\u7ec3\u4e60 \u00b7 \u793a\u4f8b\u9898",
    "chips": [
        "\u7b49\u8fb9+\u5e73\u884c\u7ebf",
        "\u5e73\u884c\u7ebf\u6c42\u89d2",
        "\u76f4\u89d2+\u4e92\u4f59",
        "\u5916\u89d2\u6027\u8d28",
        "\u7acb\u4f53\u00b7\u6b63\u65b9\u4f53",
        "\u7acb\u4f53\u00b7\u5706\u9525",
    ],
    "start": "\u5f00\u59cb AI \u5f15\u5bfc",
    "idle": "\u672a\u5f00\u59cb",
    "notes": "\u6ce8\u91ca",
    "n01": [
        "1 \u591a\u5165\u53e3\u51fa\u9898\uff1a\u62d6\u653e / \u7c98\u8d34 / \u4e0a\u4f20 / \u62cd\u7167 / \u6444\u50cf\u5934\uff0c\u7edf\u4e00\u8d70 OCR+\u8bc6\u56fe\u3002",
        "2 \u8bed\u97f3\uff1aASR \u8ffd\u52a0\u5230\u9898\u5e72\uff08\u7b54\u9898\u533a\u540c\u7406\uff09\u3002",
        "3 \u793a\u4f8b\u82af\u7247\uff1a\u5e73\u9762+\u7acb\u4f53\uff1b\u4e2d\u82f1\u5207\u6362\u6362\u6837\u672c\u5e93\u3002",
        "4 \u5f00\u59cb\u5f15\u5bfc\uff1a\u63d0\u4ea4\u6587\u5b57 + \u53ef\u9009 image/geometry\uff1b\u8fdb\u5165 Screen 04\u3002",
        "\u4fa7\u680f\u300c\u9898/\u804a/\u89e3\u300d\u4e3a\u65b0\u4fe1\u606f\u67b6\u6784\u63d0\u6848\uff0c\u4e0d\u6539\u4f60\u539f Figma \u6587\u4ef6\u3002",
    ],
    "s02": "SCREEN 02 \u00b7 \u8bc6\u56fe\u4e2d / \u9884\u89c8",
    "ocr_url": "\u8bc6\u56fe\u72b6\u6001",
    "preview": "[ \u9898\u76ee\u7167\u7247\u9884\u89c8 ]",
    "ocr_status": "\u6b63\u5728\u8bc6\u522b\u6587\u5b57\u4e0e\u51e0\u4f55\u7ed3\u6784\u2026",
    "ocr_text": "OCR \u56de\u586b\u7684\u9898\u76ee\u6587\u5b57\uff08\u53ef\u7f16\u8f91\uff09\u2026",
    "ocr_hint": "\u90e8\u5206\u6210\u529f / \u5931\u8d25\u65f6\u4ecd\u53ef\u624b\u6539\u6587\u5b57\u540e\u7ee7\u7eed",
    "n02": [
        "1 \u72b6\u6001\u533a\u5206 pending / success / partial / fail\u3002",
        "\u5931\u8d25\u4e0d\u963b\u65ad\u7eaf\u6587\u5b57\u5f15\u5bfc\u3002",
        "\u6709\u51e0\u4f55\u7ed3\u679c\u65f6\u53ef\u9884\u5f00\u753b\u677f\uff0c\u5f00\u5f15\u5bfc\u524d\u5fae\u8c03\u5bf9\u9f50\u3002",
    ],
    "s03": "SCREEN 03 \u00b7 \u6444\u50cf\u5934\u9762\u677f",
    "cam": "\u6444\u50cf\u5934",
    "video": "<video> \u5b9e\u65f6\u9884\u89c8",
    "snap": "\u62cd\u7167\u8bc6\u522b",
    "close_cam": "\u5173\u95ed\u6444\u50cf\u5934",
    "n03": [
        "1 getUserMedia \u2192 \u622a\u5e27 \u2192 \u4e0e\u4e0a\u4f20\u540c\u4e00 OCR \u94fe\u8def\u3002",
        "\u5185\u5d4c\u9762\u677f\uff0c\u975e Modal\uff0c\u4e0d\u6253\u65ad\u8f93\u5165\u4e0a\u4e0b\u6587\u3002",
    ],
    "s04": "SCREEN 04 \u00b7 AI \u5f15\u5bfc \u00b7 \u5e73\u9762\u51e0\u4f55\uff08\u6838\u5fc3\uff09",
    "guiding": "\u5f15\u5bfc\u4e2d",
    "step2": "2. AI \u9010\u6b65\u5f15\u5bfc",
    "wb_plane": "\u51e0\u4f55\u753b\u677f \u00b7 \u5e73\u9762",
    "tools": [
        "\u62d6\u52a8",
        "\u8fd8\u539f",
        "\u753b\u7b14",
        "\u6a61\u76ae",
        "\u6e05\u7a7a",
        "\u793a\u610f\u56fe",
        "\u53e0\u52a0\u539f\u56fe",
        "\u53ea\u770b\u539f\u56fe",
    ],
    "photo_layer": "\u539f\u56fe\u5c42\uff08\u53e0\u52a0\u6a21\u5f0f\uff09",
    "wb_hint": "\u62d6\u52a8\u70b9/\u8fb9 \u00b7 \u53e0\u539f\u56fe\u5bf9\u9f50 \u00b7 \u53ef\u8fd8\u539f\u57fa\u51c6\u56fe",
    "chat_h": "\u5bf9\u8bdd \u00b7 \u9010\u6b65\u63a8\u8fdb",
    "ai1": "\u5148\u770b\u770b\u5df2\u77e5\uff1aDE // BC\uff0c\u89d2 ADE=70\uff0c\u89d2 A=40\u3002\u4f60\u6253\u7b97\u600e\u4e48\u5229\u7528\u5e73\u884c\u7ebf\u627e\u89d2 C\uff1f",
    "me1": "\u540c\u4f4d\u89d2\u76f8\u7b49\uff1f",
    "hint1": "\u63d0\u793a\uff1a\u60f3\u60f3\u54ea\u4e2a\u89d2\u4e0e\u89d2 C \u6709\u5173\u2026",
    "fig": "[ \u9644\u56fe SVG ]",
    "answer": "\u4f60\u7684\u56de\u7b54",
    "ans_ph": "\u5199\u4e0b\u7b54\u6848\u6216\u601d\u8def\u2026",
    "hint_btn": "\u5361\u4f4f\u4e86\uff0c\u63d0\u793a\u4e00\u4e0b",
    "submit": "\u63d0\u4ea4\u56de\u7b54",
    "fb": "\u53cd\u9988\uff1a\u65b9\u5411\u5bf9\uff0c\u518d\u63a8\u8fdb\u4e00\u6b65\u2026",
    "n04": [
        "1 \u5de5\u5177\uff1a\u62d6\u52a8/\u8fd8\u539f/\u753b\u7b14/\u6a61\u76ae/\u6e05\u7a7a\uff1b\u80cc\u666f\u4e09\u6001\uff1a\u793a\u610f\u56fe\u00b7\u53e0\u52a0\u539f\u56fe\u00b7\u53ea\u770b\u539f\u56fe\u3002",
        "2 \u63d0\u793a\u4e3a\u72ec\u7acb hint \u6c14\u6ce1\u3002",
        "3 \u63d0\u4ea4\u65f6 busy \u7981\u7528\uff1b\u53cd\u9988\u8272\u5206 ok/bad/neutral\u3002",
        "\u684c\u9762\u5206\u680f\u5bf9\u9f50\u4f60\u539f Figma \u7684\u300c\u753b\u677f|\u5bf9\u8bdd\u300d\uff1b\u7a84\u5c4f\u6539\u56de\u4e0a\u4e0b\u5806\u53e0\u3002",
    ],
    "s05": "SCREEN 05 \u00b7 AI \u5f15\u5bfc \u00b7 \u7acb\u4f53\u56fe\u5f62",
    "solid_url": "\u7acb\u4f53\u9898",
    "wb_solid": "\u51e0\u4f55\u753b\u677f \u00b7 \u7acb\u4f53",
    "rotate": "\u65cb\u8f6c",
    "pen": "\u753b\u7b14",
    "eraser": "\u6a61\u76ae",
    "clear_marks": "\u6e05\u7a7a\u6807\u6ce8",
    "cube": "\u7acb\u65b9\u4f53 \u00b7 \u62d6\u62fd\u65cb\u8f6c",
    "solid_hint": "\u5f62\u72b6\u9501\u5b9a \u00b7 \u65e0\u53e0\u52a0\u539f\u56fe / \u8fd8\u539f",
    "chat": "\u5bf9\u8bdd",
    "solid_ai": "\u8fd9\u662f\u6b63\u65b9\u4f53\u8868\u9762\u79ef\u9898\u3002\u5148\u6570\u4e00\u6570\u6709\u51e0\u4e2a\u9762\uff1f",
    "hint_short": "\u63d0\u793a",
    "submit_short": "\u63d0\u4ea4",
    "n05": [
        "1 \u5de5\u5177\u4ece\u300c\u62d6\u52a8\u300d\u53d8\u4e3a\u300c\u65cb\u8f6c\u300d\uff1b\u9690\u85cf\u8fd8\u539f/\u53e0\u52a0\u539f\u56fe\u3002",
        "2 \u652f\u6301\u6b63\u65b9\u4f53\u3001\u957f\u65b9\u4f53\u3001\u68f1\u67f1\u3001\u68f1\u9525\u3001\u5706\u67f1\u3001\u5706\u9525\u3002",
        "3 \u7acb\u4f53\u9501\u5b9a\uff1a\u4f1a\u8bdd\u5185\u4e0d\u88ab\u5e73\u9762 figure \u8986\u76d6\u3002",
    ],
    "s06": "SCREEN 06 \u00b7 \u5b8c\u6574\u89e3\u7b54",
    "done": "\u5b8c\u6210",
    "full": "\u5b8c\u6574\u89e3\u7b54",
    "copy": "\u590d\u5236\u5168\u6587",
    "writeup": "\u3010\u9898\u76ee\u3011\u2026\n\u3010\u5206\u6790\u3011\u2026\n\u3010\u89e3\u7b54\u3011\u2026\n\u3010\u7b54\u6848\u3011\u89d2 C = 70\u00b0",
    "footer": "\u7531 DeepSeek \u63d0\u4f9b\u89e3\u9898\u5f15\u5bfc \u00b7 \u6bcf\u6b21\u53ea\u63a8\u8fdb\u4e00\u6b65",
    "n06": [
        "1 Clipboard \u590d\u5236\uff1b\u6309\u94ae\u77ed\u6682\u663e\u793a\u300c\u5df2\u590d\u5236\u300d\u3002",
        "\u5f15\u5bfc\u9762\u677f\u9690\u85cf\uff0c\u4fa7\u680f\u300c\u89e3\u300d\u9ad8\u4eae\u3002",
    ],
    "s07": "SCREEN 07 \u00b7 \u79fb\u52a8\u7aef",
    "mobile_h": "AI \u89e3\u9898",
    "lang_toggle": "\u4e2d/EN",
    "up_photo": "\u4e0a\u4f20 / \u62cd\u7167",
    "upload_s": "\u4e0a\u4f20",
    "prob_s": "\u9898\u76ee\u6587\u5b57\u2026",
    "ex1": "\u793a\u4f8b1",
    "ex2": "\u793a\u4f8b2",
    "drag": "\u62d6\u52a8",
    "overlay": "\u53e0\u52a0",
    "obs": "\u5148\u89c2\u5bdf\u5df2\u77e5\u6761\u4ef6\u2026",
    "mobile_notes": "\u79fb\u52a8\u7aef\u8981\u70b9",
    "n07": [
        "\u9690\u85cf\u4fa7\u680f\uff0c\u8bed\u8a00\u653e\u9876\u680f\u3002",
        "\u62cd\u7167\u4f18\u5148\uff08capture=environment\uff09\u3002",
        "\u5f15\u5bfc\u6001\u7ad6\u5411\uff1a\u753b\u677f \u2192 \u5bf9\u8bdd \u2192 \u4f5c\u7b54\u3002",
        "\u4e3b CTA \u901a\u680f\u3002",
    ],
    "page_name": "Wireframe v2 \u00b7 triangle-guide",
    "notify_ok": "\u5df2\u751f\u6210 Wireframe v2\uff08\u65b0\u9875\u9762\uff0c\u672a\u6539\u5176\u4ed6\u5185\u5bb9\uff09",
    "notify_fail": "\u751f\u6210\u5931\u8d25: ",
}


def js_str(s: str) -> str:
    return json_dumps_unicode(s)


def json_dumps_unicode(s: str) -> str:
    import json

    return json.dumps(s, ensure_ascii=False)


def main() -> None:
    c = C
    chips_js = ", ".join(js_str(x) for x in c["chips"])
    tools_js = ", ".join(js_str(x) for x in c["tools"])
    steps_js = ", ".join(js_str(x) for x in c["steps"])
    nav0, nav1, nav2 = c["nav"]

    def notes_arr(key: str) -> str:
        return "[" + ", ".join(js_str(x) for x in c[key]) + "]"

    out = f'''/**
 * Triangle Guide Wireframe v2
 * Creates a NEW page with wireframes. Does not touch other pages/files.
 */

const GRAY = {{ r: 0.9, g: 0.91, b: 0.92 }};
const GRAY2 = {{ r: 0.95, g: 0.95, b: 0.96 }};
const LINE = {{ r: 0.72, g: 0.72, b: 0.74 }};
const INK = {{ r: 0.1, g: 0.1, b: 0.1 }};
const MUTED = {{ r: 0.42, g: 0.45, b: 0.5 }};
const WHITE = {{ r: 1, g: 1, b: 1 }};
const NOTE_BG = {{ r: 0.94, g: 0.96, b: 1 }};
const NOTE = {{ r: 0.15, g: 0.39, b: 0.92 }};
const HOT = {{ r: 0.86, g: 0.15, b: 0.15 }};
const DARK = {{ r: 0.12, g: 0.14, b: 0.18 }};
const HINT_BG = {{ r: 1, g: 0.98, b: 0.92 }};
const HINT_LINE = {{ r: 0.85, g: 0.55, b: 0.1 }};
const OK = {{ r: 0.1, g: 0.4, b: 0.2 }};
const NOTE_INK = {{ r: 0.12, g: 0.23, b: 0.37 }};
const PRE = {{ r: 0.82, g: 0.84, b: 0.86 }};

let FONT_REG = {{ family: "Inter", style: "Regular" }};
let FONT_BOLD = {{ family: "Inter", style: "Bold" }};

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
  f.fills = opts.fills || solid(WHITE);
  f.strokes = opts.strokes || solid(INK);
  f.strokeWeight = opts.strokeWeight == null ? 2 : opts.strokeWeight;
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
  r.fills = opts.fills || solid(GRAY2);
  r.strokes = opts.strokes || solid(LINE);
  r.strokeWeight = opts.strokeWeight == null ? 1.5 : opts.strokeWeight;
  r.dashPattern = opts.dashed ? [6, 4] : [];
  r.cornerRadius = opts.radius || 0;
  parent.appendChild(r);
  return r;
}}

async function text(parent, name, chars, x, y, size, opts) {{
  opts = opts || {{}};
  const t = figma.createText();
  t.name = name;
  t.fontName = opts.bold ? FONT_BOLD : FONT_REG;
  t.characters = chars;
  t.fontSize = size;
  t.x = x;
  t.y = y;
  t.fills = solid(opts.color || INK);
  if (opts.w) {{
    t.resize(opts.w, t.height);
    t.textAutoResize = "HEIGHT";
  }}
  parent.appendChild(t);
  return t;
}}

async function btn(parent, label, x, y, w, h, primary) {{
  const g = frame("btn/" + label, x, y, w, h, {{
    parent: parent,
    fills: solid(primary ? INK : WHITE),
    strokes: solid(INK),
    strokeWeight: 1.5,
    radius: 2,
  }});
  await text(g, "label", label, 8, Math.max(4, (h - 12) / 2), 11, {{
    color: primary ? WHITE : INK,
    w: w - 16,
  }});
  return g;
}}

async function hotspot(parent, n, x, y) {{
  const c = figma.createEllipse();
  c.name = "hotspot-" + n;
  c.resize(18, 18);
  c.x = x;
  c.y = y;
  c.fills = solid(HOT);
  c.strokes = [];
  parent.appendChild(c);
  await text(parent, "n", String(n), x + 5, y + 2, 10, {{ color: WHITE, bold: true }});
}}

async function noteCard(parent, x, y, w, h, title, lines) {{
  const n = frame("Notes", x, y, w, h, {{
    parent: parent,
    fills: solid(NOTE_BG),
    strokes: solid(NOTE),
    strokeWeight: 1.5,
  }});
  await text(n, "title", title, 14, 12, 12, {{ color: NOTE, bold: true }});
  await text(n, "body", lines.join("\\n\\n"), 14, 36, 11, {{ color: NOTE_INK, w: w - 28 }});
  return n;
}}

async function chromeBar(parent, title) {{
  rect(parent, "chrome", 0, 0, parent.width, 36, {{ fills: solid(GRAY2), strokes: solid(LINE), strokeWeight: 1 }});
  for (let i = 0; i < 3; i++) {{
    const d = figma.createEllipse();
    d.resize(8, 8);
    d.x = 12 + i * 14;
    d.y = 14;
    d.fills = solid(GRAY);
    d.strokes = solid(LINE);
    d.strokeWeight = 1;
    parent.appendChild(d);
  }}
  await text(parent, "url", title, 60, 10, 11, {{ color: MUTED, w: parent.width - 80 }});
}}

async function rail(parent, active) {{
  const r = frame("rail", 0, 36, 56, parent.height - 36, {{
    parent: parent,
    fills: solid(GRAY2),
    strokes: solid(LINE),
    strokeWeight: 1,
  }});
  const items = [{js_str(nav0)}, {js_str(nav1)}, {js_str(nav2)}];
  for (let i = 0; i < items.length; i++) {{
    const label = items[i];
    const on = label === active;
    rect(r, "ico-" + label, 12, 16 + i * 44, 32, 32, {{
      fills: solid(on ? INK : WHITE),
      strokes: solid(INK),
      strokeWeight: 1.5,
    }});
    await text(r, "t", label, 20, 24 + i * 44, 11, {{ color: on ? WHITE : MUTED }});
  }}
  rect(r, "ico-lang", 12, r.height - 48, 32, 32, {{ fills: solid(WHITE), strokes: solid(LINE) }});
  await text(r, "lang", {js_str(c["zh"])}, 20, r.height - 40, 10, {{ color: MUTED }});
  return r;
}}

async function buildCover(page) {{
  const cover = frame("00 Cover", 0, 0, 1400, 420, {{
    parent: page,
    fills: solid(WHITE),
    strokes: solid(INK),
    strokeWeight: 2,
  }});
  await text(cover, "title", {js_str(c["cover_title"])}, 40, 32, 28, {{ bold: true, w: 900 }});
  await text(cover, "sub", {js_str(c["cover_sub"])}, 40, 80, 13, {{ color: MUTED, w: 1000 }});
  const steps = [{steps_js}];
  for (let i = 0; i < steps.length; i++) {{
    const s = frame("step", 40 + i * 180, 180, 160, 56, {{
      parent: cover,
      fills: solid(GRAY2),
      strokes: solid(INK),
      strokeWeight: 1.5,
    }});
    await text(s, "t", steps[i], 16, 18, 13, {{ bold: true, w: 130 }});
    if (i < steps.length - 1) {{
      await text(cover, "arrow", "\\u2192", 200 + i * 180, 196, 18, {{ color: MUTED }});
    }}
  }}
  await text(cover, "legend", {js_str(c["legend"])}, 40, 280, 12, {{ color: MUTED, w: 1100 }});
}}

async function buildScreen01(page, ox, oy) {{
  const board = frame("01 Home Input", ox, oy, 1180, 720, {{
    parent: page, fills: solid(GRAY2), strokes: [], strokeWeight: 0,
  }});
  await text(board, "id", {js_str(c["s01"])}, 0, -36, 16, {{ bold: true }});
  const device = frame("Desktop", 0, 0, 900, 640, {{
    parent: board, fills: solid(WHITE), strokes: solid(INK), strokeWeight: 2,
  }});
  await chromeBar(device, {js_str(c["url_home"])});
  await rail(device, {js_str(nav0)});
  const main = frame("main", 56, 36, 844, 604, {{
    parent: device, fills: solid(WHITE), strokes: [], strokeWeight: 0,
  }});
  await text(main, "h1", {js_str(c["h1"])}, 24, 20, 22, {{ bold: true, w: 520 }});
  await text(main, "sub", {js_str(c["sub"])}, 24, 50, 12, {{ color: MUTED, w: 520 }});
  await btn(main, {js_str(c["lang_zh"])}, 720, 22, 48, 26, true);
  await btn(main, "EN", 774, 22, 40, 26, false);
  const drop = frame("drop-zone", 24, 90, 796, 150, {{
    parent: main, fills: solid(WHITE), strokes: solid(LINE), strokeWeight: 2, radius: 4,
  }});
  drop.dashPattern = [8, 6];
  await text(drop, "t1", {js_str(c["drop1"])}, 220, 36, 14, {{ bold: true, w: 360 }});
  await text(drop, "t2", {js_str(c["drop2"])}, 250, 58, 11, {{ color: MUTED, w: 320 }});
  await btn(drop, {js_str(c["upload"])}, 220, 95, 80, 28, true);
  await btn(drop, {js_str(c["photo"])}, 310, 95, 56, 28, false);
  await btn(drop, {js_str(c["open_cam"])}, 376, 95, 88, 28, false);
  await btn(drop, {js_str(c["clear_img"])}, 474, 95, 72, 28, false);
  await hotspot(main, 1, 800, 84);
  await text(main, "label", {js_str(c["prob_label"])}, 24, 260, 11, {{ color: MUTED, w: 280 }});
  await btn(main, {js_str(c["voice"])}, 640, 254, 72, 24, false);
  await btn(main, {js_str(c["clear_txt"])}, 720, 254, 72, 24, false);
  await hotspot(main, 2, 700, 246);
  rect(main, "textarea", 24, 286, 796, 90, {{ fills: solid(WHITE), strokes: solid(LINE) }});
  await text(main, "ph", {js_str(c["ph_prob"])}, 36, 300, 12, {{ color: MUTED, w: 400 }});
  await text(main, "samples-label", {js_str(c["samples"])}, 24, 394, 11, {{ color: MUTED }});
  const chips = [{chips_js}];
  for (let i = 0; i < chips.length; i++) {{
    const chip = frame("chip", 24 + i * 110, 416, 100, 26, {{
      parent: main, fills: solid(i === 0 ? GRAY : WHITE), strokes: solid(LINE), strokeWeight: 1, radius: 13,
    }});
    await text(chip, "c", chips[i], 8, 6, 10, {{ color: INK, w: 84 }});
  }}
  await hotspot(main, 3, 690, 410);
  await btn(main, {js_str(c["start"])}, 24, 470, 120, 34, true);
  await text(main, "st", {js_str(c["idle"])}, 156, 480, 11, {{ color: MUTED }});
  await hotspot(main, 4, 130, 462);
  await noteCard(board, 920, 0, 240, 420, {js_str(c["notes"])}, {notes_arr("n01")});
}}

async function buildScreen02(page, ox, oy) {{
  const board = frame("02 OCR Preview", ox, oy, 1180, 560, {{
    parent: page, fills: solid(GRAY2), strokes: [], strokeWeight: 0,
  }});
  await text(board, "id", {js_str(c["s02"])}, 0, -36, 16, {{ bold: true }});
  const device = frame("Desktop", 0, 0, 900, 480, {{
    parent: board, fills: solid(WHITE), strokes: solid(INK), strokeWeight: 2,
  }});
  await chromeBar(device, {js_str(c["ocr_url"])});
  const main = frame("main", 0, 36, 900, 444, {{
    parent: device, fills: solid(WHITE), strokes: [], strokeWeight: 0,
  }});
  rect(main, "preview-bg", 40, 30, 820, 180, {{ fills: solid(GRAY2), strokes: solid(INK), strokeWeight: 1.5 }});
  rect(main, "photo", 250, 55, 400, 120, {{ fills: solid(GRAY), strokes: solid(INK) }});
  await text(main, "ph", {js_str(c["preview"])}, 380, 105, 12, {{ color: MUTED }});
  await text(main, "status", {js_str(c["ocr_status"])}, 40, 222, 13, {{ bold: true, w: 400 }});
  await hotspot(main, 1, 300, 214);
  rect(main, "ocr-text", 40, 255, 820, 70, {{ fills: solid(WHITE), strokes: solid(LINE) }});
  await text(main, "ocr", {js_str(c["ocr_text"])}, 52, 278, 12, {{ color: MUTED, w: 500 }});
  await text(main, "hint", {js_str(c["ocr_hint"])}, 40, 340, 11, {{ color: MUTED, w: 400 }});
  await btn(main, {js_str(c["start"])}, 700, 380, 120, 32, true);
  await noteCard(board, 920, 0, 240, 280, {js_str(c["notes"])}, {notes_arr("n02")});
}}

async function buildScreen03(page, ox, oy) {{
  const board = frame("03 Camera", ox, oy, 1180, 520, {{
    parent: page, fills: solid(GRAY2), strokes: [], strokeWeight: 0,
  }});
  await text(board, "id", {js_str(c["s03"])}, 0, -36, 16, {{ bold: true }});
  const device = frame("Desktop", 0, 0, 900, 440, {{
    parent: board, fills: solid(WHITE), strokes: solid(INK), strokeWeight: 2,
  }});
  await chromeBar(device, {js_str(c["cam"])});
  const main = frame("main", 0, 36, 900, 404, {{
    parent: device, fills: solid(WHITE), strokes: [], strokeWeight: 0,
  }});
  rect(main, "video", 40, 24, 820, 260, {{ fills: solid(GRAY), strokes: solid(INK), strokeWeight: 2 }});
  await text(main, "v", {js_str(c["video"])}, 380, 140, 14, {{ color: MUTED }});
  await hotspot(main, 1, 840, 16);
  await btn(main, {js_str(c["snap"])}, 40, 310, 100, 32, true);
  await btn(main, {js_str(c["close_cam"])}, 150, 310, 100, 32, false);
  await noteCard(board, 920, 0, 240, 220, {js_str(c["notes"])}, {notes_arr("n03")});
}}

async function buildScreen04(page, ox, oy) {{
  const board = frame("04 Guide Plane", ox, oy, 1280, 780, {{
    parent: page, fills: solid(GRAY2), strokes: [], strokeWeight: 0,
  }});
  await text(board, "id", {js_str(c["s04"])}, 0, -36, 16, {{ bold: true }});
  const device = frame("Desktop", 0, 0, 1000, 700, {{
    parent: board, fills: solid(WHITE), strokes: solid(INK), strokeWeight: 2,
  }});
  await chromeBar(device, {js_str(c["guiding"])});
  await rail(device, {js_str(nav1)});
  const main = frame("main", 56, 36, 944, 664, {{
    parent: device, fills: solid(WHITE), strokes: [], strokeWeight: 0,
  }});
  await text(main, "step", {js_str(c["step2"])}, 16, 12, 13, {{ bold: true }});
  await text(main, "tag", "session active", 140, 14, 10, {{ color: MUTED }});
  const boardP = frame("workbench", 12, 40, 460, 600, {{
    parent: main, fills: solid(WHITE), strokes: solid(LINE), strokeWeight: 1.5,
  }});
  rect(boardP, "head", 0, 0, 460, 32, {{ fills: solid(GRAY2), strokes: solid(LINE), strokeWeight: 1 }});
  await text(boardP, "ht", {js_str(c["wb_plane"])}, 12, 8, 11, {{ bold: true }});
  await hotspot(main, 1, 450, 34);
  const tools = [{tools_js}];
  for (let i = 0; i < tools.length; i++) {{
    const primary = i === 0 || i === 5;
    await btn(boardP, tools[i], 8 + (i % 4) * 110, 40 + Math.floor(i / 4) * 32, 100, 26, primary);
  }}
  const stage = frame("stage", 12, 120, 436, 420, {{
    parent: boardP, fills: solid(GRAY2), strokes: solid(LINE), strokeWeight: 1.5,
  }});
  stage.dashPattern = [6, 4];
  rect(stage, "photo-ghost", 40, 40, 356, 340, {{
    fills: solid(GRAY, 0.35), strokes: solid(MUTED), strokeWeight: 1.5, dashed: true,
  }});
  await text(stage, "pg", {js_str(c["photo_layer"])}, 140, 60, 11, {{ color: MUTED }});
  const poly = figma.createPolygon();
  poly.name = "triangle";
  poly.pointCount = 3;
  poly.resize(140, 120);
  poly.x = 158;
  poly.y = 160;
  poly.fills = solid(GRAY);
  poly.strokes = solid(INK);
  poly.strokeWeight = 2;
  stage.appendChild(poly);
  await text(stage, "tn", "ABC", 210, 210, 12, {{ bold: true }});
  await text(boardP, "hint", {js_str(c["wb_hint"])}, 12, 555, 10, {{ color: MUTED, w: 420 }});
  const chatP = frame("chat", 484, 40, 448, 600, {{
    parent: main, fills: solid(WHITE), strokes: solid(LINE), strokeWeight: 1.5,
  }});
  rect(chatP, "head", 0, 0, 448, 32, {{ fills: solid(GRAY2), strokes: solid(LINE), strokeWeight: 1 }});
  await text(chatP, "ht", {js_str(c["chat_h"])}, 12, 8, 11, {{ bold: true }});
  const b1 = frame("bubble-ai", 12, 48, 360, 70, {{
    parent: chatP, fills: solid(GRAY2), strokes: solid(LINE), strokeWeight: 1,
  }});
  await text(b1, "t", {js_str(c["ai1"])}, 10, 8, 11, {{ w: 340 }});
  const b2 = frame("bubble-me", 80, 130, 356, 36, {{
    parent: chatP, fills: solid(WHITE), strokes: solid(INK), strokeWeight: 1.5,
  }});
  await text(b2, "t", {js_str(c["me1"])}, 10, 10, 11, {{ w: 330 }});
  const b3 = frame("bubble-hint", 12, 180, 360, 48, {{
    parent: chatP, fills: solid(HINT_BG), strokes: solid(HINT_LINE), strokeWeight: 1.5,
  }});
  b3.dashPattern = [4, 3];
  await text(b3, "t", {js_str(c["hint1"])}, 10, 14, 11, {{ w: 340 }});
  rect(chatP, "fig", 12, 244, 280, 56, {{ fills: solid(GRAY2), strokes: solid(LINE), dashed: true }});
  await text(chatP, "figt", {js_str(c["fig"])}, 100, 264, 11, {{ color: MUTED }});
  await text(chatP, "al", {js_str(c["answer"])}, 12, 320, 11, {{ color: MUTED }});
  await btn(chatP, {js_str(c["voice"])}, 340, 316, 72, 22, false);
  rect(chatP, "answer", 12, 348, 424, 70, {{ fills: solid(WHITE), strokes: solid(LINE) }});
  await text(chatP, "aph", {js_str(c["ans_ph"])}, 24, 370, 12, {{ color: MUTED }});
  await btn(chatP, {js_str(c["hint_btn"])}, 12, 440, 140, 30, false);
  await btn(chatP, {js_str(c["submit"])}, 162, 440, 90, 30, true);
  await hotspot(chatP, 2, 140, 432);
  await hotspot(chatP, 3, 240, 432);
  await text(chatP, "fb", {js_str(c["fb"])}, 12, 490, 11, {{ color: OK }});
  await noteCard(board, 1020, 0, 240, 420, {js_str(c["notes"])}, {notes_arr("n04")});
}}

async function buildScreen05(page, ox, oy) {{
  const board = frame("05 Guide Solid", ox, oy, 1180, 640, {{
    parent: page, fills: solid(GRAY2), strokes: [], strokeWeight: 0,
  }});
  await text(board, "id", {js_str(c["s05"])}, 0, -36, 16, {{ bold: true }});
  const device = frame("Desktop", 0, 0, 900, 560, {{
    parent: board, fills: solid(WHITE), strokes: solid(INK), strokeWeight: 2,
  }});
  await chromeBar(device, {js_str(c["solid_url"])});
  await rail(device, {js_str(nav1)});
  const main = frame("main", 56, 36, 844, 524, {{
    parent: device, fills: solid(WHITE), strokes: [], strokeWeight: 0,
  }});
  const left = frame("solid-board", 12, 16, 400, 480, {{
    parent: main, fills: solid(WHITE), strokes: solid(LINE), strokeWeight: 1.5,
  }});
  rect(left, "head", 0, 0, 400, 32, {{ fills: solid(GRAY2), strokes: solid(LINE), strokeWeight: 1 }});
  await text(left, "ht", {js_str(c["wb_solid"])}, 12, 8, 11, {{ bold: true }});
  await btn(left, {js_str(c["rotate"])}, 8, 44, 56, 26, true);
  await btn(left, {js_str(c["pen"])}, 72, 44, 56, 26, false);
  await btn(left, {js_str(c["eraser"])}, 136, 44, 56, 26, false);
  await btn(left, {js_str(c["clear_marks"])}, 200, 44, 80, 26, false);
  const stage = frame("stage", 12, 84, 376, 340, {{
    parent: left, fills: solid(GRAY2), strokes: solid(LINE), strokeWeight: 1.5,
  }});
  rect(stage, "cube", 130, 100, 110, 110, {{ fills: solid(GRAY, 0.4), strokes: solid(INK), strokeWeight: 2 }});
  await text(stage, "ct", {js_str(c["cube"])}, 120, 230, 11, {{ color: MUTED }});
  await hotspot(left, 1, 360, 76);
  await text(left, "h", {js_str(c["solid_hint"])}, 12, 440, 10, {{ color: MUTED, w: 360 }});
  const right = frame("chat", 428, 16, 400, 480, {{
    parent: main, fills: solid(WHITE), strokes: solid(LINE), strokeWeight: 1.5,
  }});
  rect(right, "head", 0, 0, 400, 32, {{ fills: solid(GRAY2), strokes: solid(LINE), strokeWeight: 1 }});
  await text(right, "ht", {js_str(c["chat"])}, 12, 8, 11, {{ bold: true }});
  const b = frame("bubble", 12, 48, 360, 50, {{
    parent: right, fills: solid(GRAY2), strokes: solid(LINE),
  }});
  await text(b, "t", {js_str(c["solid_ai"])}, 10, 14, 11, {{ w: 340 }});
  rect(right, "ans", 12, 120, 376, 60, {{ fills: solid(WHITE), strokes: solid(LINE) }});
  await btn(right, {js_str(c["hint_short"])}, 12, 200, 64, 28, false);
  await btn(right, {js_str(c["submit_short"])}, 84, 200, 64, 28, true);
  await noteCard(board, 920, 0, 240, 300, {js_str(c["notes"])}, {notes_arr("n05")});
}}

async function buildScreen06(page, ox, oy) {{
  const board = frame("06 Done", ox, oy, 1180, 520, {{
    parent: page, fills: solid(GRAY2), strokes: [], strokeWeight: 0,
  }});
  await text(board, "id", {js_str(c["s06"])}, 0, -36, 16, {{ bold: true }});
  const device = frame("Desktop", 0, 0, 900, 440, {{
    parent: board, fills: solid(WHITE), strokes: solid(INK), strokeWeight: 2,
  }});
  await chromeBar(device, {js_str(c["done"])});
  await rail(device, {js_str(nav2)});
  const main = frame("main", 56, 36, 844, 404, {{
    parent: device, fills: solid(WHITE), strokes: [], strokeWeight: 0,
  }});
  await text(main, "h", {js_str(c["full"])}, 24, 20, 18, {{ bold: true }});
  await btn(main, {js_str(c["copy"])}, 700, 18, 100, 30, true);
  await hotspot(main, 1, 788, 10);
  const pre = frame("writeup", 24, 64, 796, 260, {{
    parent: main, fills: solid(DARK), strokes: [], strokeWeight: 0,
  }});
  await text(pre, "body", {js_str(c["writeup"])}, 20, 20, 13, {{ color: PRE, w: 750 }});
  await text(main, "foot", {js_str(c["footer"])}, 24, 350, 11, {{ color: MUTED, w: 500 }});
  await noteCard(board, 920, 0, 240, 200, {js_str(c["notes"])}, {notes_arr("n06")});
}}

async function buildScreen07(page, ox, oy) {{
  const board = frame("07 Mobile", ox, oy, 1060, 780, {{
    parent: page, fills: solid(GRAY2), strokes: [], strokeWeight: 0,
  }});
  await text(board, "id", {js_str(c["s07"])}, 0, -36, 16, {{ bold: true }});
  const phoneA = frame("Phone Input", 0, 0, 360, 700, {{
    parent: board, fills: solid(WHITE), strokes: solid(INK), strokeWeight: 2, radius: 24,
  }});
  rect(phoneA, "status", 0, 0, 360, 32, {{ fills: solid(GRAY2), strokes: solid(LINE), strokeWeight: 1 }});
  await text(phoneA, "time", "9:41", 160, 8, 11, {{ color: MUTED }});
  await text(phoneA, "h", {js_str(c["mobile_h"])}, 20, 48, 18, {{ bold: true }});
  await btn(phoneA, {js_str(c["lang_toggle"])}, 280, 48, 56, 24, false);
  const drop = frame("drop", 16, 90, 328, 120, {{
    parent: phoneA, fills: solid(WHITE), strokes: solid(LINE), strokeWeight: 2,
  }});
  drop.dashPattern = [6, 4];
  await text(drop, "t", {js_str(c["up_photo"])}, 120, 30, 12, {{ color: MUTED }});
  await btn(drop, {js_str(c["upload_s"])}, 90, 70, 64, 28, true);
  await btn(drop, {js_str(c["photo"])}, 166, 70, 64, 28, false);
  rect(phoneA, "ta", 16, 230, 328, 80, {{ fills: solid(WHITE), strokes: solid(LINE) }});
  await text(phoneA, "ph", {js_str(c["prob_s"])}, 28, 258, 12, {{ color: MUTED }});
  await btn(phoneA, {js_str(c["ex1"])}, 16, 328, 64, 24, false);
  await btn(phoneA, {js_str(c["ex2"])}, 88, 328, 64, 24, false);
  const cta = frame("cta", 16, 380, 328, 40, {{
    parent: phoneA, fills: solid(INK), strokes: solid(INK),
  }});
  await text(cta, "t", {js_str(c["start"])}, 110, 12, 13, {{ color: WHITE, bold: true }});
  const phoneB = frame("Phone Guide", 400, 0, 360, 700, {{
    parent: board, fills: solid(WHITE), strokes: solid(INK), strokeWeight: 2, radius: 24,
  }});
  rect(phoneB, "status", 0, 0, 360, 32, {{ fills: solid(GRAY2), strokes: solid(LINE), strokeWeight: 1 }});
  await text(phoneB, "time", "9:41", 160, 8, 11, {{ color: MUTED }});
  const wb = frame("board", 12, 44, 336, 220, {{
    parent: phoneB, fills: solid(WHITE), strokes: solid(LINE), strokeWeight: 1.5,
  }});
  await btn(wb, {js_str(c["drag"])}, 8, 8, 48, 22, true);
  await btn(wb, {js_str(c["pen"])}, 62, 8, 48, 22, false);
  await btn(wb, {js_str(c["overlay"])}, 116, 8, 48, 22, false);
  const st = frame("stage", 8, 40, 320, 160, {{
    parent: wb, fills: solid(GRAY2), strokes: solid(LINE),
  }});
  const poly = figma.createPolygon();
  poly.pointCount = 3;
  poly.resize(100, 80);
  poly.x = 110;
  poly.y = 40;
  poly.fills = solid(GRAY);
  poly.strokes = solid(INK);
  poly.strokeWeight = 2;
  st.appendChild(poly);
  const bubble = frame("ai", 12, 280, 300, 50, {{
    parent: phoneB, fills: solid(GRAY2), strokes: solid(LINE),
  }});
  await text(bubble, "t", {js_str(c["obs"])}, 10, 16, 11, {{ w: 280 }});
  rect(phoneB, "ans", 12, 348, 336, 60, {{ fills: solid(WHITE), strokes: solid(LINE) }});
  await btn(phoneB, {js_str(c["hint_short"])}, 12, 428, 160, 34, false);
  await btn(phoneB, {js_str(c["submit_short"])}, 184, 428, 164, 34, true);
  await noteCard(board, 780, 0, 240, 280, {js_str(c["mobile_notes"])}, {notes_arr("n07")});
}}

async function main() {{
  try {{
    await figma.loadFontAsync({{ family: "Inter", style: "Regular" }});
    await figma.loadFontAsync({{ family: "Inter", style: "Bold" }});
  }} catch (e) {{
    FONT_REG = {{ family: "Roboto", style: "Regular" }};
    FONT_BOLD = {{ family: "Roboto", style: "Bold" }};
    await figma.loadFontAsync(FONT_REG);
    await figma.loadFontAsync(FONT_BOLD);
  }}
  const page = figma.createPage();
  page.name = {js_str(c["page_name"])};
  await figma.setCurrentPageAsync(page);
  await buildCover(page);
  await buildScreen01(page, 0, 520);
  await buildScreen02(page, 0, 1360);
  await buildScreen03(page, 0, 2060);
  await buildScreen04(page, 0, 2720);
  await buildScreen05(page, 0, 3660);
  await buildScreen06(page, 0, 4460);
  await buildScreen07(page, 0, 5140);
  figma.viewport.scrollAndZoomIntoView(page.children);
  figma.notify({js_str(c["notify_ok"])});
  figma.closePlugin();
}}

main().catch(function (err) {{
  figma.notify({js_str(c["notify_fail"])} + String(err));
  figma.closePlugin();
}});
'''

    dest = Path(__file__).with_name("code.js")
    dest.write_text(out, encoding="utf-8")
    sample = dest.read_text(encoding="utf-8")
    assert "打开摄像头" in sample or "\u6253\u5f00\u6444\u50cf\u5934" in open(__file__, encoding="utf-8").read()
    # verify decoded chinese present
    assert "打开摄像头" in sample
    assert "开始 AI 引导" in sample
    print("Wrote", dest, "bytes", dest.stat().st_size)


if __name__ == "__main__":
    main()
