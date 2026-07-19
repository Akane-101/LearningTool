/**
 * Triangle Guide Hi-Fi UI — Figma plugin
 * Creates a NEW page. Does not modify other pages.
 */

function hex(h) {
  const n = h.replace("#", "");
  return {
    r: parseInt(n.slice(0, 2), 16) / 255,
    g: parseInt(n.slice(2, 4), 16) / 255,
    b: parseInt(n.slice(4, 6), 16) / 255,
  };
}

const C = {
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
};

let FONT = { family: "Inter", style: "Regular" };
let FONT_B = { family: "Inter", style: "Bold" };
let FONT_M = { family: "Inter", style: "Medium" };

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
  f.fills = opts.fills !== undefined ? opts.fills : solid(C.white);
  f.strokes = opts.strokes || [];
  f.strokeWeight = opts.strokeWeight == null ? 1 : opts.strokeWeight;
  if (opts.stroke) {
    f.strokes = solid(opts.stroke);
    f.strokeWeight = opts.strokeWeight == null ? 1 : opts.strokeWeight;
  }
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
  r.fills = opts.fills !== undefined ? opts.fills : solid(C.soft);
  r.strokes = opts.stroke ? solid(opts.stroke) : [];
  r.strokeWeight = opts.strokeWeight == null ? 1 : opts.strokeWeight;
  r.dashPattern = opts.dashed ? [5, 4] : [];
  r.cornerRadius = opts.radius || 0;
  parent.appendChild(r);
  return r;
}

async function txt(parent, name, chars, x, y, size, opts) {
  opts = opts || {};
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
  if (opts.w) {
    t.resize(opts.w, t.height);
    t.textAutoResize = "HEIGHT";
  }
  parent.appendChild(t);
  return t;
}

async function btn(parent, label, x, y, w, h, kind) {
  // kind: primary | navy | secondary | ghost | tool | toolOn | chip | chipOn
  let fill = C.white;
  let stroke = C.line;
  let color = C.ink;
  let sw = 1;
  let radius = 10;
  if (kind === "primary") {
    fill = C.orange; stroke = C.orange; color = C.white; sw = 0;
  } else if (kind === "navy") {
    fill = C.navy; stroke = C.navy; color = C.white; sw = 0;
  } else if (kind === "secondary") {
    fill = C.white; stroke = C.line; color = C.navy;
  } else if (kind === "ghost") {
    fill = C.white; stroke = C.line; color = C.muted;
  } else if (kind === "tool") {
    fill = C.white; stroke = C.line; color = C.ink; radius = 8;
  } else if (kind === "toolOn") {
    fill = C.navy; stroke = C.navy; color = C.white; radius = 8; sw = 0;
  } else if (kind === "chip") {
    fill = C.white; stroke = C.line; color = C.muted; radius = 999;
  } else if (kind === "chipOn") {
    fill = C.softBlue; stroke = hex("#b7d0f0"); color = C.navy; radius = 999;
  } else if (kind === "langOn") {
    fill = C.navy; stroke = C.navy; color = C.white; radius = 8; sw = 0;
  } else if (kind === "lang") {
    fill = C.white; stroke = C.line; color = C.muted; radius = 8;
  }
  const g = frame("btn/" + label, x, y, w, h, {
    parent: parent,
    fills: solid(fill),
    stroke: stroke,
    strokeWeight: sw,
    radius: radius,
  });
  const fs = kind === "tool" || kind === "toolOn" || kind === "chip" || kind === "chipOn" ? 11 : 12;
  await txt(g, "l", label, 8, Math.max(3, (h - fs) / 2 - 1), fs, {
    color: color,
    bold: kind === "primary" || kind === "navy" || kind === "chipOn",
    w: w - 16,
  });
  return g;
}

async function sidebar(parent, active) {
  const s = frame("sidebar", 0, 0, 72, parent.height, {
    parent: parent,
    fills: solid(C.white),
    stroke: C.line,
    strokeWeight: 1,
  });
  // logo
  const logo = frame("logo", 16, 18, 40, 40, {
    parent: s,
    fills: solid(C.navy),
    strokeWeight: 0,
    radius: 12,
  });
  await txt(logo, "t", "\u25b3", 12, 8, 16, { color: C.white, bold: true });

  const items = [
    { k: "home", label: "首", y: 78 },
    { k: "prac", label: "练", y: 130 },
    { k: "done", label: "解", y: 182 },
  ];
  for (let i = 0; i < items.length; i++) {
    const it = items[i];
    const on = it.k === active;
    const b = frame("nav-" + it.k, 15, it.y, 42, 42, {
      parent: s,
      fills: solid(on ? C.softBlue : C.white),
      strokeWeight: 0,
      radius: 12,
    });
    await txt(b, "t", it.label, 13, 12, 13, { color: on ? C.navy : C.muted, bold: on });
  }

  const av = frame("avatar", 16, s.height - 56, 40, 40, {
    parent: s,
    fills: solid(C.soft),
    stroke: C.line,
    strokeWeight: 2,
    radius: 999,
  });
  await txt(av, "t", "学", 11, 10, 13, { color: C.navy, bold: true });
  const badge = figma.createEllipse();
  badge.resize(12, 12);
  badge.x = 42;
  badge.y = s.height - 28;
  badge.fills = solid(C.orange);
  badge.strokes = solid(C.white);
  badge.strokeWeight = 2;
  s.appendChild(badge);
  return s;
}

async function deviceShell(page, name, x, y, activeNav) {
  const outer = frame(name, x, y, 1180, 720, {
    parent: page,
    fills: solid(C.stageBg),
    strokeWeight: 0,
    radius: 0,
  });
  const device = frame("Device", 0, 40, 1180, 680, {
    parent: outer,
    fills: solid(C.white),
    stroke: hex("#d0d7e4"),
    strokeWeight: 1,
    radius: 28,
  });
  await sidebar(device, activeNav);
  const main = frame("main", 72, 0, 1108, 680, {
    parent: device,
    fills: solid(C.soft),
    strokeWeight: 0,
  });
  return { outer, device, main };
}

function triangle(parent, x, y) {
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
}

async function buildCover(page) {
  const c = frame("00 Cover", 0, 0, 1180, 200, {
    parent: page,
    fills: solid(C.white),
    stroke: C.line,
    strokeWeight: 1,
    radius: 16,
  });
  await txt(c, "t", "解三角形 · 高保真 UI", 36, 40, 28, { bold: true, w: 900 });
  await txt(c, "s", "配色/侧栏/首页双入口/画板分栏 对齐你的 Figma · 独立新页，不改原文件", 36, 90, 13, { color: C.muted, w: 1000 });
  const swatches = [
    ["navy", C.navy],
    ["orange", C.orange],
    ["softBlue", C.softBlue],
    ["line", C.line],
  ];
  for (let i = 0; i < swatches.length; i++) {
    rect(c, swatches[i][0], 36 + i * 56, 140, 40, 40, {
      fills: solid(swatches[i][1]),
      radius: 10,
      stroke: C.line,
    });
  }
}

async function buildHome(page, ox, oy) {
  await txt(page, "label-01", "01 Home · 首页", ox, oy - 28, 14, { bold: true, color: C.ink });
  const { main } = await deviceShell(page, "01 Home", ox, oy, "home");

  // lang
  await btn(main, "中文", 980, 20, 52, 28, "langOn");
  await btn(main, "EN", 1038, 20, 40, 28, "lang");

  await txt(main, "g1", "早上好，", 280, 180, 36, { bold: true, w: 560 });
  await txt(main, "g2", "今天想学点什么？", 280, 228, 36, { bold: true, color: C.navy, w: 560 });

  const card1 = frame("entry-search", 200, 320, 320, 200, {
    parent: main,
    fills: solid(C.white),
    stroke: C.line,
    strokeWeight: 1,
    radius: 20,
  });
  const ico1 = frame("ico", 28, 28, 52, 52, {
    parent: card1,
    fills: solid(C.softBlue),
    strokeWeight: 0,
    radius: 14,
  });
  await txt(ico1, "i", "\u0950", 14, 12, 18, { color: C.navy });
  await txt(ico1, "cam", "CAM", 10, 16, 11, { color: C.navy, bold: true });
  await txt(card1, "h", "搜索题目", 28, 100, 18, { bold: true });
  await txt(card1, "d", "拍照 / 上传 / 粘贴截图，自动识字与描摩几何图", 28, 132, 12, { color: C.muted, w: 260 });

  const card2 = frame("entry-practice", 560, 320, 320, 200, {
    parent: main,
    fills: solid(C.white),
    stroke: C.line,
    strokeWeight: 1,
    radius: 20,
  });
  const ico2 = frame("ico", 28, 28, 52, 52, {
    parent: card2,
    fills: solid(C.softBlue),
    strokeWeight: 0,
    radius: 14,
  });
  await txt(ico2, "i", "DOC", 10, 16, 11, { color: C.navy, bold: true });
  await txt(card2, "h", "快速练习", 28, 100, 18, { bold: true });
  await txt(card2, "d", "选示例题，AI 逐步引导；支持平面与立体图形", 28, 132, 12, { color: C.muted, w: 260 });
}

async function buildSearch(page, ox, oy) {
  await txt(page, "label-02", "02 Search · 搜索题目", ox, oy - 28, 14, { bold: true });
  const { main } = await deviceShell(page, "02 Search", ox, oy, "prac");

  await txt(main, "title", "搜索题目", 24, 18, 18, { bold: true });
  const pill = frame("pill", 880, 18, 180, 28, {
    parent: main,
    fills: solid(C.white),
    stroke: C.line,
    strokeWeight: 1,
    radius: 999,
  });
  const dot = figma.createEllipse();
  dot.resize(7, 7);
  dot.x = 12;
  dot.y = 10;
  dot.fills = solid(hex("#22c55e"));
  pill.appendChild(dot);
  await txt(pill, "t", "已识别几何结构", 28, 6, 11, { color: C.muted, w: 140 });

  // left panel
  const left = frame("board-panel", 20, 60, 620, 580, {
    parent: main,
    fills: solid(C.white),
    stroke: C.line,
    strokeWeight: 1,
    radius: 20,
  });
  const strip = frame("upload", 0, 0, 620, 64, {
    parent: left,
    fills: solid(C.soft),
    stroke: C.line,
    strokeWeight: 1,
  });
  rect(strip, "thumb", 16, 10, 64, 44, { fills: solid(C.softBlue), radius: 8, stroke: C.line });
  await txt(strip, "ph", "题目照片", 96, 12, 13, { bold: true });
  await txt(strip, "pm", "可叠加原图对齐 · 支持清空重拍", 96, 34, 11, { color: C.muted, w: 300 });
  await btn(strip, "清空", 460, 18, 56, 28, "ghost");
  await btn(strip, "重拍", 524, 18, 56, 28, "ghost");

  await txt(left, "bh", "画板", 16, 78, 14, { bold: true });
  await txt(left, "bm", "平面", 70, 80, 11, { color: C.muted });

  const tools = ["拖动", "还原图形", "画笔", "橡皮", "清空标注", "示意图", "叠加原图", "只看原图"];
  for (let i = 0; i < tools.length; i++) {
    const on = i === 0 || i === 5;
    await btn(left, tools[i], 12 + (i % 4) * 148, 108 + Math.floor(i / 4) * 34, 140, 28, on ? "toolOn" : "tool");
  }

  const stage = frame("stage", 16, 190, 588, 360, {
    parent: left,
    fills: solid(C.soft),
    stroke: C.line,
    strokeWeight: 1,
    radius: 14,
  });
  stage.dashPattern = [5, 4];
  rect(stage, "photo-ghost", 24, 24, 540, 312, {
    fills: solid(C.softBlue, 0.35),
    stroke: C.muted,
    strokeWeight: 1,
    dashed: true,
    radius: 10,
  });
  triangle(stage, 194, 100);

  // right
  const right = frame("prob-panel", 656, 60, 420, 580, {
    parent: main,
    fills: solid(C.white),
    stroke: C.line,
    strokeWeight: 1,
    radius: 20,
  });
  await txt(right, "h", "题目文字", 16, 16, 14, { bold: true });
  await txt(right, "m", "可编辑", 100, 18, 11, { color: C.muted });
  const box = frame("prob", 16, 48, 388, 420, {
    parent: right,
    fills: solid(C.soft),
    stroke: C.line,
    strokeWeight: 1,
    radius: 12,
  });
  await txt(box, "p", "如图，在△ABC中，D、E分别是AB、AC上的点，DE∥BC，∠ADE=70°，∠A=40°，求∠C的度数。", 14, 14, 13, { w: 360 });
  await btn(right, "语音输入", 16, 490, 80, 32, "ghost");
  await btn(right, "打开摄像头", 104, 490, 100, 32, "secondary");
  await btn(right, "开始 AI 引导", 240, 490, 164, 36, "primary");
}

async function buildGuide(page, ox, oy) {
  await txt(page, "label-03", "03 Guide · AI 引导", ox, oy - 28, 14, { bold: true });
  const { main } = await deviceShell(page, "03 Guide", ox, oy, "prac");

  await txt(main, "title", "快速练习", 24, 16, 18, { bold: true });
  const pill = frame("pill", 820, 16, 250, 28, {
    parent: main,
    fills: solid(C.white),
    stroke: C.line,
    strokeWeight: 1,
    radius: 999,
  });
  const dot = figma.createEllipse();
  dot.resize(7, 7);
  dot.x = 10;
  dot.y = 10;
  dot.fills = solid(hex("#22c55e"));
  pill.appendChild(dot);
  await txt(pill, "t", "已开始引导，请在下方按步骤作答", 24, 6, 10, { color: C.muted, w: 210 });

  const chips = ["2024·等边三角形+平行线", "2022·平行线求角度", "2023·三角形外角性质", "立体·正方体表面积"];
  for (let i = 0; i < chips.length; i++) {
    await btn(main, chips[i], 20 + i * 200, 56, 190, 28, i === 0 ? "chipOn" : "chip");
  }

  const left = frame("board", 20, 100, 560, 540, {
    parent: main,
    fills: solid(C.white),
    stroke: C.line,
    strokeWeight: 1,
    radius: 20,
  });
  await txt(left, "h", "画板", 16, 14, 14, { bold: true });
  await txt(left, "m", "示意图 · 可叠原图", 70, 16, 11, { color: C.muted });
  const t2 = ["拖动", "画笔", "橡皮", "清空标注", "示意图", "叠加原图", "只看原图"];
  for (let i = 0; i < t2.length; i++) {
    const on = i === 0 || i === 4;
    await btn(left, t2[i], 12 + i * 76, 44, 72, 26, on ? "toolOn" : "tool");
  }
  const stage = frame("stage", 16, 86, 528, 420, {
    parent: left,
    fills: solid(C.soft),
    stroke: C.line,
    strokeWeight: 1,
    radius: 14,
  });
  triangle(stage, 164, 120);

  const right = frame("chat", 600, 100, 480, 540, {
    parent: main,
    fills: solid(C.white),
    stroke: C.line,
    strokeWeight: 1,
    radius: 20,
  });
  await txt(right, "h", "AI 引导", 16, 14, 14, { bold: true });
  await txt(right, "m", "逐步推进", 100, 16, 11, { color: C.muted });

  const b1 = frame("ai1", 16, 48, 400, 78, {
    parent: right,
    fills: solid(C.soft),
    stroke: C.line,
    strokeWeight: 1,
    radius: 14,
  });
  await txt(b1, "w", "AI", 12, 8, 10, { color: C.muted, bold: true });
  await txt(b1, "t", "先看看已知条件：DE∥BC，∠ADE=70°，∠A=40°。你打算怎么利用平行线来找∠C？", 12, 26, 12, { w: 376 });

  const b2 = frame("me1", 64, 140, 400, 44, {
    parent: right,
    fills: solid(C.navy),
    strokeWeight: 0,
    radius: 14,
  });
  await txt(b2, "w", "你", 12, 6, 10, { color: C.white });
  await txt(b2, "t", "同位角相等？", 12, 22, 12, { color: C.white, w: 376 });

  const b3 = frame("hint", 16, 200, 400, 64, {
    parent: right,
    fills: solid(C.hintBg),
    stroke: C.hintLine,
    strokeWeight: 1,
    radius: 14,
  });
  b3.dashPattern = [4, 3];
  await txt(b3, "w", "提示", 12, 8, 10, { color: C.hintInk, bold: true });
  await txt(b3, "t", "平行线会产生同位角、内错角或同旁内角，想想哪个和∠C有关？", 12, 26, 12, { color: C.hintInk, w: 376 });

  const b4 = frame("ai2", 16, 280, 400, 50, {
    parent: right,
    fills: solid(C.soft),
    stroke: C.line,
    strokeWeight: 1,
    radius: 14,
  });
  await txt(b4, "t", "方向对。再想一步：∠ADE 与哪个角是同位角？", 12, 14, 12, { w: 376 });

  const ta = frame("input", 16, 360, 448, 70, {
    parent: right,
    fills: solid(C.soft),
    stroke: C.line,
    strokeWeight: 1,
    radius: 12,
  });
  await txt(ta, "ph", "写下你的答案或思路", 12, 12, 12, { color: C.muted, w: 420 });
  await btn(right, "语音输入", 16, 448, 80, 32, "ghost");
  await btn(right, "卡住了，提示一下", 104, 448, 140, 32, "secondary");
  await btn(right, "确认", 360, 448, 88, 34, "primary");
  await txt(right, "fb", "反馈：思路正确，继续往下推。", 16, 500, 12, { color: C.ok, w: 400 });
}

async function buildSolid(page, ox, oy) {
  await txt(page, "label-04", "04 Solid · 立体", ox, oy - 28, 14, { bold: true });
  const { main } = await deviceShell(page, "04 Solid", ox, oy, "prac");
  await txt(main, "title", "立体 · 正方体表面积", 24, 18, 18, { bold: true });
  const pill = frame("pill", 920, 18, 140, 28, {
    parent: main,
    fills: solid(C.white),
    stroke: C.line,
    strokeWeight: 1,
    radius: 999,
  });
  await txt(pill, "t", "3D 旋转模式", 14, 6, 11, { color: C.muted, w: 120 });

  const left = frame("board", 20, 60, 560, 580, {
    parent: main,
    fills: solid(C.white),
    stroke: C.line,
    strokeWeight: 1,
    radius: 20,
  });
  await txt(left, "h", "画板", 16, 14, 14, { bold: true });
  await txt(left, "m", "立体 · 形状锁定", 70, 16, 11, { color: C.muted });
  await btn(left, "旋转", 12, 48, 64, 28, "toolOn");
  await btn(left, "画笔", 84, 48, 56, 28, "tool");
  await btn(left, "橡皮", 148, 48, 56, 28, "tool");
  await btn(left, "清空标注", 212, 48, 88, 28, "tool");
  const stage = frame("stage", 16, 96, 528, 440, {
    parent: left,
    fills: solid(C.soft),
    stroke: C.line,
    strokeWeight: 1,
    radius: 14,
  });
  rect(stage, "cube", 204, 150, 120, 120, {
    fills: solid(C.softBlue, 0.8),
    stroke: C.navy,
    strokeWeight: 2,
    radius: 4,
  });

  const right = frame("chat", 600, 60, 480, 580, {
    parent: main,
    fills: solid(C.white),
    stroke: C.line,
    strokeWeight: 1,
    radius: 20,
  });
  await txt(right, "h", "AI 引导", 16, 14, 14, { bold: true });
  const b = frame("ai", 16, 48, 448, 70, {
    parent: right,
    fills: solid(C.soft),
    stroke: C.line,
    strokeWeight: 1,
    radius: 14,
  });
  await txt(b, "t", "这是正方体表面积题。先数一数：正方体一共有几个面？每个面是什么形状？", 12, 14, 12, { w: 420 });
  const ta = frame("ans", 16, 140, 448, 70, {
    parent: right,
    fills: solid(C.soft),
    stroke: C.line,
    strokeWeight: 1,
    radius: 12,
  });
  await txt(ta, "t", "6 个正方形面", 12, 14, 13, { w: 420 });
  await btn(right, "卡住了，提示一下", 16, 230, 140, 34, "secondary");
  await btn(right, "确认", 360, 230, 88, 34, "primary");
}

async function buildDone(page, ox, oy) {
  await txt(page, "label-05", "05 Done · 完整解答", ox, oy - 28, 14, { bold: true });
  const { main } = await deviceShell(page, "05 Done", ox, oy, "done");
  await txt(main, "title", "完整解答", 24, 18, 18, { bold: true });
  await btn(main, "复制全文", 960, 14, 110, 36, "primary");

  const pre = frame("writeup", 24, 70, 1050, 520, {
    parent: main,
    fills: solid(C.dark),
    strokeWeight: 0,
    radius: 20,
  });
  await txt(pre, "body", "【题目】\n如图，在△ABC中，D、E分别是AB、AC上的点，DE∥BC，∠ADE=70°，∠A=40°，求∠C的度数。\n\n【分析】\n由 DE∥BC，可得同位角相等；结合三角形内角和求 ∠C。\n\n【解答】\n∵ DE∥BC\n∴ ∠ADE = ∠ABC = 70°（同位角）\n∵ ∠A = 40°\n∴ ∠C = 180° − 40° − 70° = 70°\n\n【答案】 ∠C = 70°", 28, 28, 13, { color: C.pre, w: 990 });
  await txt(main, "foot", "由 DeepSeek 提供解题引导 · 每次只推进一步", 24, 610, 11, { color: C.muted, w: 600 });
}

async function main() {
  try {
    await figma.loadFontAsync({ family: "Inter", style: "Regular" });
    await figma.loadFontAsync({ family: "Inter", style: "Bold" });
    try {
      await figma.loadFontAsync({ family: "Inter", style: "Medium" });
    } catch (e) {
      FONT_M = FONT_B;
    }
  } catch (e) {
    FONT = { family: "Roboto", style: "Regular" };
    FONT_B = { family: "Roboto", style: "Bold" };
    FONT_M = FONT_B;
    await figma.loadFontAsync(FONT);
    await figma.loadFontAsync(FONT_B);
  }

  const page = figma.createPage();
  page.name = "Hi-Fi UI · triangle-guide";
  await figma.setCurrentPageAsync(page);

  await buildCover(page);
  await buildHome(page, 0, 260);
  await buildSearch(page, 0, 1100);
  await buildGuide(page, 0, 1960);
  await buildSolid(page, 0, 2820);
  await buildDone(page, 0, 3680);

  figma.viewport.scrollAndZoomIntoView(page.children);
  figma.notify("已生成高保真 UI（新页面）");
  figma.closePlugin();
}

main().catch(function (err) {
  figma.notify("生成失败: " + String(err));
  figma.closePlugin();
});
