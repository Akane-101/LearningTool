/**
 * Triangle Guide Wireframe v2
 * Creates a NEW page with wireframes. Does not touch other pages/files.
 */

const GRAY = { r: 0.9, g: 0.91, b: 0.92 };
const GRAY2 = { r: 0.95, g: 0.95, b: 0.96 };
const LINE = { r: 0.72, g: 0.72, b: 0.74 };
const INK = { r: 0.1, g: 0.1, b: 0.1 };
const MUTED = { r: 0.42, g: 0.45, b: 0.5 };
const WHITE = { r: 1, g: 1, b: 1 };
const NOTE_BG = { r: 0.94, g: 0.96, b: 1 };
const NOTE = { r: 0.15, g: 0.39, b: 0.92 };
const HOT = { r: 0.86, g: 0.15, b: 0.15 };
const DARK = { r: 0.12, g: 0.14, b: 0.18 };
const HINT_BG = { r: 1, g: 0.98, b: 0.92 };
const HINT_LINE = { r: 0.85, g: 0.55, b: 0.1 };
const OK = { r: 0.1, g: 0.4, b: 0.2 };
const NOTE_INK = { r: 0.12, g: 0.23, b: 0.37 };
const PRE = { r: 0.82, g: 0.84, b: 0.86 };

let FONT_REG = { family: "Inter", style: "Regular" };
let FONT_BOLD = { family: "Inter", style: "Bold" };

function solid(color, opacity) {
  return [{ type: "SOLID", color: color, opacity: opacity == null ? 1 : opacity }];
}

function frame(name, x, y, w, h, opts) {
  opts = opts || {};
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
}

function rect(parent, name, x, y, w, h, opts) {
  opts = opts || {};
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
}

async function text(parent, name, chars, x, y, size, opts) {
  opts = opts || {};
  const t = figma.createText();
  t.name = name;
  t.fontName = opts.bold ? FONT_BOLD : FONT_REG;
  t.characters = chars;
  t.fontSize = size;
  t.x = x;
  t.y = y;
  t.fills = solid(opts.color || INK);
  if (opts.w) {
    t.resize(opts.w, t.height);
    t.textAutoResize = "HEIGHT";
  }
  parent.appendChild(t);
  return t;
}

async function btn(parent, label, x, y, w, h, primary) {
  const g = frame("btn/" + label, x, y, w, h, {
    parent: parent,
    fills: solid(primary ? INK : WHITE),
    strokes: solid(INK),
    strokeWeight: 1.5,
    radius: 2,
  });
  await text(g, "label", label, 8, Math.max(4, (h - 12) / 2), 11, {
    color: primary ? WHITE : INK,
    w: w - 16,
  });
  return g;
}

async function hotspot(parent, n, x, y) {
  const c = figma.createEllipse();
  c.name = "hotspot-" + n;
  c.resize(18, 18);
  c.x = x;
  c.y = y;
  c.fills = solid(HOT);
  c.strokes = [];
  parent.appendChild(c);
  await text(parent, "n", String(n), x + 5, y + 2, 10, { color: WHITE, bold: true });
}

async function noteCard(parent, x, y, w, h, title, lines) {
  const n = frame("Notes", x, y, w, h, {
    parent: parent,
    fills: solid(NOTE_BG),
    strokes: solid(NOTE),
    strokeWeight: 1.5,
  });
  await text(n, "title", title, 14, 12, 12, { color: NOTE, bold: true });
  await text(n, "body", lines.join("\n\n"), 14, 36, 11, { color: NOTE_INK, w: w - 28 });
  return n;
}

async function chromeBar(parent, title) {
  rect(parent, "chrome", 0, 0, parent.width, 36, { fills: solid(GRAY2), strokes: solid(LINE), strokeWeight: 1 });
  for (let i = 0; i < 3; i++) {
    const d = figma.createEllipse();
    d.resize(8, 8);
    d.x = 12 + i * 14;
    d.y = 14;
    d.fills = solid(GRAY);
    d.strokes = solid(LINE);
    d.strokeWeight = 1;
    parent.appendChild(d);
  }
  await text(parent, "url", title, 60, 10, 11, { color: MUTED, w: parent.width - 80 });
}

async function rail(parent, active) {
  const r = frame("rail", 0, 36, 56, parent.height - 36, {
    parent: parent,
    fills: solid(GRAY2),
    strokes: solid(LINE),
    strokeWeight: 1,
  });
  const items = ["题", "聊", "解"];
  for (let i = 0; i < items.length; i++) {
    const label = items[i];
    const on = label === active;
    rect(r, "ico-" + label, 12, 16 + i * 44, 32, 32, {
      fills: solid(on ? INK : WHITE),
      strokes: solid(INK),
      strokeWeight: 1.5,
    });
    await text(r, "t", label, 20, 24 + i * 44, 11, { color: on ? WHITE : MUTED });
  }
  rect(r, "ico-lang", 12, r.height - 48, 32, 32, { fills: solid(WHITE), strokes: solid(LINE) });
  await text(r, "lang", "中", 20, r.height - 40, 10, { color: MUTED });
  return r;
}

async function buildCover(page) {
  const cover = frame("00 Cover", 0, 0, 1400, 420, {
    parent: page,
    fills: solid(WHITE),
    strokes: solid(INK),
    strokeWeight: 2,
  });
  await text(cover, "title", "解三角形 AI 引导 · UI Wireframe v2", 40, 32, 28, { bold: true, w: 900 });
  await text(cover, "sub", "基于现有功能 + 线上 UI 重绘 · 独立新页，未改动原 Untitled Figma\n覆盖：多入口出题 · OCR · 语音 · 示例 · AI 对话 · 平面叠图 · 立体旋转 · 完整解答 · 中英 · 移动端", 40, 80, 13, { color: MUTED, w: 1000 });
  const steps = ["01 输入", "02 识图", "03 摄像头", "04 引导·平面", "05 引导·立体", "06 完成", "07 移动端"];
  for (let i = 0; i < steps.length; i++) {
    const s = frame("step", 40 + i * 180, 180, 160, 56, {
      parent: cover,
      fills: solid(GRAY2),
      strokes: solid(INK),
      strokeWeight: 1.5,
    });
    await text(s, "t", steps[i], 16, 18, 13, { bold: true, w: 130 });
    if (i < steps.length - 1) {
      await text(cover, "arrow", "\u2192", 200 + i * 180, 196, 18, { color: MUTED });
    }
  }
  await text(cover, "legend", "图例：实线框=内容区 · 虚线框=投放区 · 红点=关键交互 · 蓝卡片=注释\n生成方式：本地插件 Triangle Guide Wireframe v2（仓库 figma-wireframe-plugin/）", 40, 280, 12, { color: MUTED, w: 1100 });
}

async function buildScreen01(page, ox, oy) {
  const board = frame("01 Home Input", ox, oy, 1180, 720, {
    parent: page, fills: solid(GRAY2), strokes: [], strokeWeight: 0,
  });
  await text(board, "id", "SCREEN 01 · 首页输入", 0, -36, 16, { bold: true });
  const device = frame("Desktop", 0, 0, 900, 640, {
    parent: board, fills: solid(WHITE), strokes: solid(INK), strokeWeight: 2,
  });
  await chromeBar(device, "127.0.0.1:8001 — AI 解题引导");
  await rail(device, "题");
  const main = frame("main", 56, 36, 844, 604, {
    parent: device, fills: solid(WHITE), strokes: [], strokeWeight: 0,
  });
  await text(main, "h1", "AI 带你一步一步解题", 24, 20, 22, { bold: true, w: 520 });
  await text(main, "sub", "拍照看图 + 文字 → 识几何图 · 逐步引导", 24, 50, 12, { color: MUTED, w: 520 });
  await btn(main, "中文", 720, 22, 48, 26, true);
  await btn(main, "EN", 774, 22, 40, 26, false);
  const drop = frame("drop-zone", 24, 90, 796, 150, {
    parent: main, fills: solid(WHITE), strokes: solid(LINE), strokeWeight: 2, radius: 4,
  });
  drop.dashPattern = [8, 6];
  await text(drop, "t1", "拖入题目图片 / Ctrl+V 粘贴", 220, 36, 14, { bold: true, w: 360 });
  await text(drop, "t2", "也支持相册、拍照、打开摄像头", 250, 58, 11, { color: MUTED, w: 320 });
  await btn(drop, "上传图片", 220, 95, 80, 28, true);
  await btn(drop, "拍照", 310, 95, 56, 28, false);
  await btn(drop, "打开摄像头", 376, 95, 88, 28, false);
  await btn(drop, "清空图片", 474, 95, 72, 28, false);
  await hotspot(main, 1, 800, 84);
  await text(main, "label", "题目文字（可改，可含已有过程）", 24, 260, 11, { color: MUTED, w: 280 });
  await btn(main, "语音输入", 640, 254, 72, 24, false);
  await btn(main, "清空文字", 720, 254, 72, 24, false);
  await hotspot(main, 2, 700, 246);
  rect(main, "textarea", 24, 286, 796, 90, { fills: solid(WHITE), strokes: solid(LINE) });
  await text(main, "ph", "在此输入或粘贴题目文字…", 36, 300, 12, { color: MUTED, w: 400 });
  await text(main, "samples-label", "快速练习 · 示例题", 24, 394, 11, { color: MUTED });
  const chips = ["等边+平行线", "平行线求角", "直角+互余", "外角性质", "立体·正方体", "立体·圆锥"];
  for (let i = 0; i < chips.length; i++) {
    const chip = frame("chip", 24 + i * 110, 416, 100, 26, {
      parent: main, fills: solid(i === 0 ? GRAY : WHITE), strokes: solid(LINE), strokeWeight: 1, radius: 13,
    });
    await text(chip, "c", chips[i], 8, 6, 10, { color: INK, w: 84 });
  }
  await hotspot(main, 3, 690, 410);
  await btn(main, "开始 AI 引导", 24, 470, 120, 34, true);
  await text(main, "st", "未开始", 156, 480, 11, { color: MUTED });
  await hotspot(main, 4, 130, 462);
  await noteCard(board, 920, 0, 240, 420, "注释", ["1 多入口出题：拖放 / 粘贴 / 上传 / 拍照 / 摄像头，统一走 OCR+识图。", "2 语音：ASR 追加到题干（答题区同理）。", "3 示例芯片：平面+立体；中英切换换样本库。", "4 开始引导：提交文字 + 可选 image/geometry；进入 Screen 04。", "侧栏「题/聊/解」为新信息架构提案，不改你原 Figma 文件。"]);
}

async function buildScreen02(page, ox, oy) {
  const board = frame("02 OCR Preview", ox, oy, 1180, 560, {
    parent: page, fills: solid(GRAY2), strokes: [], strokeWeight: 0,
  });
  await text(board, "id", "SCREEN 02 · 识图中 / 预览", 0, -36, 16, { bold: true });
  const device = frame("Desktop", 0, 0, 900, 480, {
    parent: board, fills: solid(WHITE), strokes: solid(INK), strokeWeight: 2,
  });
  await chromeBar(device, "识图状态");
  const main = frame("main", 0, 36, 900, 444, {
    parent: device, fills: solid(WHITE), strokes: [], strokeWeight: 0,
  });
  rect(main, "preview-bg", 40, 30, 820, 180, { fills: solid(GRAY2), strokes: solid(INK), strokeWeight: 1.5 });
  rect(main, "photo", 250, 55, 400, 120, { fills: solid(GRAY), strokes: solid(INK) });
  await text(main, "ph", "[ 题目照片预览 ]", 380, 105, 12, { color: MUTED });
  await text(main, "status", "正在识别文字与几何结构…", 40, 222, 13, { bold: true, w: 400 });
  await hotspot(main, 1, 300, 214);
  rect(main, "ocr-text", 40, 255, 820, 70, { fills: solid(WHITE), strokes: solid(LINE) });
  await text(main, "ocr", "OCR 回填的题目文字（可编辑）…", 52, 278, 12, { color: MUTED, w: 500 });
  await text(main, "hint", "部分成功 / 失败时仍可手改文字后继续", 40, 340, 11, { color: MUTED, w: 400 });
  await btn(main, "开始 AI 引导", 700, 380, 120, 32, true);
  await noteCard(board, 920, 0, 240, 280, "注释", ["1 状态区分 pending / success / partial / fail。", "失败不阻断纯文字引导。", "有几何结果时可预开画板，开引导前微调对齐。"]);
}

async function buildScreen03(page, ox, oy) {
  const board = frame("03 Camera", ox, oy, 1180, 520, {
    parent: page, fills: solid(GRAY2), strokes: [], strokeWeight: 0,
  });
  await text(board, "id", "SCREEN 03 · 摄像头面板", 0, -36, 16, { bold: true });
  const device = frame("Desktop", 0, 0, 900, 440, {
    parent: board, fills: solid(WHITE), strokes: solid(INK), strokeWeight: 2,
  });
  await chromeBar(device, "摄像头");
  const main = frame("main", 0, 36, 900, 404, {
    parent: device, fills: solid(WHITE), strokes: [], strokeWeight: 0,
  });
  rect(main, "video", 40, 24, 820, 260, { fills: solid(GRAY), strokes: solid(INK), strokeWeight: 2 });
  await text(main, "v", "<video> 实时预览", 380, 140, 14, { color: MUTED });
  await hotspot(main, 1, 840, 16);
  await btn(main, "拍照识别", 40, 310, 100, 32, true);
  await btn(main, "关闭摄像头", 150, 310, 100, 32, false);
  await noteCard(board, 920, 0, 240, 220, "注释", ["1 getUserMedia → 截帧 → 与上传同一 OCR 链路。", "内嵌面板，非 Modal，不打断输入上下文。"]);
}

async function buildScreen04(page, ox, oy) {
  const board = frame("04 Guide Plane", ox, oy, 1280, 780, {
    parent: page, fills: solid(GRAY2), strokes: [], strokeWeight: 0,
  });
  await text(board, "id", "SCREEN 04 · AI 引导 · 平面几何（核心）", 0, -36, 16, { bold: true });
  const device = frame("Desktop", 0, 0, 1000, 700, {
    parent: board, fills: solid(WHITE), strokes: solid(INK), strokeWeight: 2,
  });
  await chromeBar(device, "引导中");
  await rail(device, "聊");
  const main = frame("main", 56, 36, 944, 664, {
    parent: device, fills: solid(WHITE), strokes: [], strokeWeight: 0,
  });
  await text(main, "step", "2. AI 逐步引导", 16, 12, 13, { bold: true });
  await text(main, "tag", "session active", 140, 14, 10, { color: MUTED });
  const boardP = frame("workbench", 12, 40, 460, 600, {
    parent: main, fills: solid(WHITE), strokes: solid(LINE), strokeWeight: 1.5,
  });
  rect(boardP, "head", 0, 0, 460, 32, { fills: solid(GRAY2), strokes: solid(LINE), strokeWeight: 1 });
  await text(boardP, "ht", "几何画板 · 平面", 12, 8, 11, { bold: true });
  await hotspot(main, 1, 450, 34);
  const tools = ["拖动", "还原", "画笔", "橡皮", "清空", "示意图", "叠加原图", "只看原图"];
  for (let i = 0; i < tools.length; i++) {
    const primary = i === 0 || i === 5;
    await btn(boardP, tools[i], 8 + (i % 4) * 110, 40 + Math.floor(i / 4) * 32, 100, 26, primary);
  }
  const stage = frame("stage", 12, 120, 436, 420, {
    parent: boardP, fills: solid(GRAY2), strokes: solid(LINE), strokeWeight: 1.5,
  });
  stage.dashPattern = [6, 4];
  rect(stage, "photo-ghost", 40, 40, 356, 340, {
    fills: solid(GRAY, 0.35), strokes: solid(MUTED), strokeWeight: 1.5, dashed: true,
  });
  await text(stage, "pg", "原图层（叠加模式）", 140, 60, 11, { color: MUTED });
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
  await text(stage, "tn", "ABC", 210, 210, 12, { bold: true });
  await text(boardP, "hint", "拖动点/边 · 叠原图对齐 · 可还原基准图", 12, 555, 10, { color: MUTED, w: 420 });
  const chatP = frame("chat", 484, 40, 448, 600, {
    parent: main, fills: solid(WHITE), strokes: solid(LINE), strokeWeight: 1.5,
  });
  rect(chatP, "head", 0, 0, 448, 32, { fills: solid(GRAY2), strokes: solid(LINE), strokeWeight: 1 });
  await text(chatP, "ht", "对话 · 逐步推进", 12, 8, 11, { bold: true });
  const b1 = frame("bubble-ai", 12, 48, 360, 70, {
    parent: chatP, fills: solid(GRAY2), strokes: solid(LINE), strokeWeight: 1,
  });
  await text(b1, "t", "先看看已知：DE // BC，角 ADE=70，角 A=40。你打算怎么利用平行线找角 C？", 10, 8, 11, { w: 340 });
  const b2 = frame("bubble-me", 80, 130, 356, 36, {
    parent: chatP, fills: solid(WHITE), strokes: solid(INK), strokeWeight: 1.5,
  });
  await text(b2, "t", "同位角相等？", 10, 10, 11, { w: 330 });
  const b3 = frame("bubble-hint", 12, 180, 360, 48, {
    parent: chatP, fills: solid(HINT_BG), strokes: solid(HINT_LINE), strokeWeight: 1.5,
  });
  b3.dashPattern = [4, 3];
  await text(b3, "t", "提示：想想哪个角与角 C 有关…", 10, 14, 11, { w: 340 });
  rect(chatP, "fig", 12, 244, 280, 56, { fills: solid(GRAY2), strokes: solid(LINE), dashed: true });
  await text(chatP, "figt", "[ 附图 SVG ]", 100, 264, 11, { color: MUTED });
  await text(chatP, "al", "你的回答", 12, 320, 11, { color: MUTED });
  await btn(chatP, "语音输入", 340, 316, 72, 22, false);
  rect(chatP, "answer", 12, 348, 424, 70, { fills: solid(WHITE), strokes: solid(LINE) });
  await text(chatP, "aph", "写下答案或思路…", 24, 370, 12, { color: MUTED });
  await btn(chatP, "卡住了，提示一下", 12, 440, 140, 30, false);
  await btn(chatP, "提交回答", 162, 440, 90, 30, true);
  await hotspot(chatP, 2, 140, 432);
  await hotspot(chatP, 3, 240, 432);
  await text(chatP, "fb", "反馈：方向对，再推进一步…", 12, 490, 11, { color: OK });
  await noteCard(board, 1020, 0, 240, 420, "注释", ["1 工具：拖动/还原/画笔/橡皮/清空；背景三态：示意图·叠加原图·只看原图。", "2 提示为独立 hint 气泡。", "3 提交时 busy 禁用；反馈色分 ok/bad/neutral。", "桌面分栏对齐你原 Figma 的「画板|对话」；窄屏改回上下堆叠。"]);
}

async function buildScreen05(page, ox, oy) {
  const board = frame("05 Guide Solid", ox, oy, 1180, 640, {
    parent: page, fills: solid(GRAY2), strokes: [], strokeWeight: 0,
  });
  await text(board, "id", "SCREEN 05 · AI 引导 · 立体图形", 0, -36, 16, { bold: true });
  const device = frame("Desktop", 0, 0, 900, 560, {
    parent: board, fills: solid(WHITE), strokes: solid(INK), strokeWeight: 2,
  });
  await chromeBar(device, "立体题");
  await rail(device, "聊");
  const main = frame("main", 56, 36, 844, 524, {
    parent: device, fills: solid(WHITE), strokes: [], strokeWeight: 0,
  });
  const left = frame("solid-board", 12, 16, 400, 480, {
    parent: main, fills: solid(WHITE), strokes: solid(LINE), strokeWeight: 1.5,
  });
  rect(left, "head", 0, 0, 400, 32, { fills: solid(GRAY2), strokes: solid(LINE), strokeWeight: 1 });
  await text(left, "ht", "几何画板 · 立体", 12, 8, 11, { bold: true });
  await btn(left, "旋转", 8, 44, 56, 26, true);
  await btn(left, "画笔", 72, 44, 56, 26, false);
  await btn(left, "橡皮", 136, 44, 56, 26, false);
  await btn(left, "清空标注", 200, 44, 80, 26, false);
  const stage = frame("stage", 12, 84, 376, 340, {
    parent: left, fills: solid(GRAY2), strokes: solid(LINE), strokeWeight: 1.5,
  });
  rect(stage, "cube", 130, 100, 110, 110, { fills: solid(GRAY, 0.4), strokes: solid(INK), strokeWeight: 2 });
  await text(stage, "ct", "立方体 · 拖拽旋转", 120, 230, 11, { color: MUTED });
  await hotspot(left, 1, 360, 76);
  await text(left, "h", "形状锁定 · 无叠加原图 / 还原", 12, 440, 10, { color: MUTED, w: 360 });
  const right = frame("chat", 428, 16, 400, 480, {
    parent: main, fills: solid(WHITE), strokes: solid(LINE), strokeWeight: 1.5,
  });
  rect(right, "head", 0, 0, 400, 32, { fills: solid(GRAY2), strokes: solid(LINE), strokeWeight: 1 });
  await text(right, "ht", "对话", 12, 8, 11, { bold: true });
  const b = frame("bubble", 12, 48, 360, 50, {
    parent: right, fills: solid(GRAY2), strokes: solid(LINE),
  });
  await text(b, "t", "这是正方体表面积题。先数一数有几个面？", 10, 14, 11, { w: 340 });
  rect(right, "ans", 12, 120, 376, 60, { fills: solid(WHITE), strokes: solid(LINE) });
  await btn(right, "提示", 12, 200, 64, 28, false);
  await btn(right, "提交", 84, 200, 64, 28, true);
  await noteCard(board, 920, 0, 240, 300, "注释", ["1 工具从「拖动」变为「旋转」；隐藏还原/叠加原图。", "2 支持正方体、长方体、棱柱、棱锥、圆柱、圆锥。", "3 立体锁定：会话内不被平面 figure 覆盖。"]);
}

async function buildScreen06(page, ox, oy) {
  const board = frame("06 Done", ox, oy, 1180, 520, {
    parent: page, fills: solid(GRAY2), strokes: [], strokeWeight: 0,
  });
  await text(board, "id", "SCREEN 06 · 完整解答", 0, -36, 16, { bold: true });
  const device = frame("Desktop", 0, 0, 900, 440, {
    parent: board, fills: solid(WHITE), strokes: solid(INK), strokeWeight: 2,
  });
  await chromeBar(device, "完成");
  await rail(device, "解");
  const main = frame("main", 56, 36, 844, 404, {
    parent: device, fills: solid(WHITE), strokes: [], strokeWeight: 0,
  });
  await text(main, "h", "完整解答", 24, 20, 18, { bold: true });
  await btn(main, "复制全文", 700, 18, 100, 30, true);
  await hotspot(main, 1, 788, 10);
  const pre = frame("writeup", 24, 64, 796, 260, {
    parent: main, fills: solid(DARK), strokes: [], strokeWeight: 0,
  });
  await text(pre, "body", "【题目】…\n【分析】…\n【解答】…\n【答案】角 C = 70°", 20, 20, 13, { color: PRE, w: 750 });
  await text(main, "foot", "由 DeepSeek 提供解题引导 · 每次只推进一步", 24, 350, 11, { color: MUTED, w: 500 });
  await noteCard(board, 920, 0, 240, 200, "注释", ["1 Clipboard 复制；按钮短暂显示「已复制」。", "引导面板隐藏，侧栏「解」高亮。"]);
}

async function buildScreen07(page, ox, oy) {
  const board = frame("07 Mobile", ox, oy, 1060, 780, {
    parent: page, fills: solid(GRAY2), strokes: [], strokeWeight: 0,
  });
  await text(board, "id", "SCREEN 07 · 移动端", 0, -36, 16, { bold: true });
  const phoneA = frame("Phone Input", 0, 0, 360, 700, {
    parent: board, fills: solid(WHITE), strokes: solid(INK), strokeWeight: 2, radius: 24,
  });
  rect(phoneA, "status", 0, 0, 360, 32, { fills: solid(GRAY2), strokes: solid(LINE), strokeWeight: 1 });
  await text(phoneA, "time", "9:41", 160, 8, 11, { color: MUTED });
  await text(phoneA, "h", "AI 解题", 20, 48, 18, { bold: true });
  await btn(phoneA, "中/EN", 280, 48, 56, 24, false);
  const drop = frame("drop", 16, 90, 328, 120, {
    parent: phoneA, fills: solid(WHITE), strokes: solid(LINE), strokeWeight: 2,
  });
  drop.dashPattern = [6, 4];
  await text(drop, "t", "上传 / 拍照", 120, 30, 12, { color: MUTED });
  await btn(drop, "上传", 90, 70, 64, 28, true);
  await btn(drop, "拍照", 166, 70, 64, 28, false);
  rect(phoneA, "ta", 16, 230, 328, 80, { fills: solid(WHITE), strokes: solid(LINE) });
  await text(phoneA, "ph", "题目文字…", 28, 258, 12, { color: MUTED });
  await btn(phoneA, "示例1", 16, 328, 64, 24, false);
  await btn(phoneA, "示例2", 88, 328, 64, 24, false);
  const cta = frame("cta", 16, 380, 328, 40, {
    parent: phoneA, fills: solid(INK), strokes: solid(INK),
  });
  await text(cta, "t", "开始 AI 引导", 110, 12, 13, { color: WHITE, bold: true });
  const phoneB = frame("Phone Guide", 400, 0, 360, 700, {
    parent: board, fills: solid(WHITE), strokes: solid(INK), strokeWeight: 2, radius: 24,
  });
  rect(phoneB, "status", 0, 0, 360, 32, { fills: solid(GRAY2), strokes: solid(LINE), strokeWeight: 1 });
  await text(phoneB, "time", "9:41", 160, 8, 11, { color: MUTED });
  const wb = frame("board", 12, 44, 336, 220, {
    parent: phoneB, fills: solid(WHITE), strokes: solid(LINE), strokeWeight: 1.5,
  });
  await btn(wb, "拖动", 8, 8, 48, 22, true);
  await btn(wb, "画笔", 62, 8, 48, 22, false);
  await btn(wb, "叠加", 116, 8, 48, 22, false);
  const st = frame("stage", 8, 40, 320, 160, {
    parent: wb, fills: solid(GRAY2), strokes: solid(LINE),
  });
  const poly = figma.createPolygon();
  poly.pointCount = 3;
  poly.resize(100, 80);
  poly.x = 110;
  poly.y = 40;
  poly.fills = solid(GRAY);
  poly.strokes = solid(INK);
  poly.strokeWeight = 2;
  st.appendChild(poly);
  const bubble = frame("ai", 12, 280, 300, 50, {
    parent: phoneB, fills: solid(GRAY2), strokes: solid(LINE),
  });
  await text(bubble, "t", "先观察已知条件…", 10, 16, 11, { w: 280 });
  rect(phoneB, "ans", 12, 348, 336, 60, { fills: solid(WHITE), strokes: solid(LINE) });
  await btn(phoneB, "提示", 12, 428, 160, 34, false);
  await btn(phoneB, "提交", 184, 428, 164, 34, true);
  await noteCard(board, 780, 0, 240, 280, "移动端要点", ["隐藏侧栏，语言放顶栏。", "拍照优先（capture=environment）。", "引导态竖向：画板 → 对话 → 作答。", "主 CTA 通栏。"]);
}

async function main() {
  try {
    await figma.loadFontAsync({ family: "Inter", style: "Regular" });
    await figma.loadFontAsync({ family: "Inter", style: "Bold" });
  } catch (e) {
    FONT_REG = { family: "Roboto", style: "Regular" };
    FONT_BOLD = { family: "Roboto", style: "Bold" };
    await figma.loadFontAsync(FONT_REG);
    await figma.loadFontAsync(FONT_BOLD);
  }
  const page = figma.createPage();
  page.name = "Wireframe v2 · triangle-guide";
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
  figma.notify("已生成 Wireframe v2（新页面，未改其他内容）");
  figma.closePlugin();
}

main().catch(function (err) {
  figma.notify("生成失败: " + String(err));
  figma.closePlugin();
});
