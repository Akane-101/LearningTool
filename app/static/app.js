let sessionId = null;
let cameraStream = null;
let busy = false;
let abortCtrl = null;
let currentLang = "zh";
let currentImageBase64 = null;
let currentImageMime = null;
let currentGeometryDescription = "";
let currentVisionFigure = null;
let drawMode = "move"; // move | pen | eraser
let drawing = false;
let bgMode = "figure"; // figure | overlay | photo
let latestFigureSvg = null;
let latestFigureData = null;
let geoBaseline = null; // 首次描摹的图形快照，用于「还原」
let geoState = null;
let geoDrag = null;
const GEO_W = 360;
const GEO_H = 280;

const I18N = {
  zh: {
    brandName: "PathSolve 向解",
    title: "渐进引导，向解而生",
    subtitle: "平面/立体几何 · 拍照看图 · 根据题目生成示意图 · DeepSeek 逐步引导",
    homeTitle: "首页",
    searchTitle: "搜索题目",
    guideTitle: "快速练习",
    doneTitle: "完整解答",
    homeGreet: "<span class=\"greet-line\">早上好，</span><br /><span class=\"greet-line\">今天想学点什么？</span>",
    logoReplayTip: "点击重播开场",
    entrySearch: "搜索题目",
    entrySearchDesc: "拍照 / 上传 / 粘贴截图，自动识字与描摹几何图",
    entryPractice: "快速练习",
    entryPracticeDesc: "选示例题，AI 逐步引导；支持平面与立体图形",
    problemEditable: "可编辑",
    guideMeta: "逐步推进",
    boardEmpty: "选一道题开始后，画板会出现在这里",
    boardEmptySearch: "上传题目后，几何示意图会出现在这里",
    dropHintShort: "图片预览会出现在这里",
    previewZoomTip: "点击查看大图",
    closePreview: "关闭",
    confirm: "确认",
    reviewTitleShort: "做题反馈",
    back: "返回",
    backHome: "回首页",
    step1: "1. 输入题目",
    dropTitle: "把题目图片拖到这里，或按 Ctrl+V 粘贴截图",
    dropHint: "也支持手机拍照、相册选图",
    upload: "上传",
    uploadLocal: "本地图片",
    uploadHelp: "支持拖拽或点击上传题目图片，也可粘贴截图",
    uploadFormats: "当前支持的图片格式",
    uploadFormatsTip: "JPG、PNG、WEBP、GIF",
    takePhoto: "拍照",
    openCamera: "打开摄像头",
    snap: "拍照识别",
    closeCamera: "关闭摄像头",
    problemLabel: "题目文字",
    problemPlaceholder: "拍照或粘贴图片后这里会自动填入文字；也可以直接打字/粘贴。\n如果你已经写了一部分解题过程，直接贴在这里，AI 会接着你的思路继续。",
    startGuide: "确认",
    step2: "AI 引导",
    answerPlaceholder: "写下你的答案或思路（Enter 发送，Ctrl+Enter 换行）",
    hint: "卡住了，提示一下",
    hintAsked: "（我卡住了，想要一个提示）",
    hintLoading: "正在想提示…",
    hintReady: "已给出提示，试试下一步。",
    submit: "提交回答",
    fullSolution: "完整解答",
    doneBanner: "本题已完成 · 下面是反馈建议，以及完整解答",
    reviewTitle: "做题反馈与建议",
    reviewStrengths: "做得好的地方",
    reviewImprovements: "可以改进",
    reviewSuggestions: "建议与下一步",
    reviewLoading: "正在生成更详细的反馈…",
    reviewReady: "",
    copy: "复制全文（含反馈）",
    copied: "已复制",
    footer: "由 DeepSeek 提供解题引导 · 每次只推进一步，鼓励你自己思考",
    thinking: "AI 思考中…",
    grading: "AI 批改中…",
    connecting: "向解正在思考中，马上给你第一步提示…",
    started: "已开始引导，请在下方按步骤作答。",
    enterProblem: "请先输入或识别题目（也可点上方示例题）",
    startFailed: "启动失败",
    timeoutStart: "等待超时了，请再点一次「开始 AI 引导」。",
    reqFailed: "请求失败，请检查网络、服务是否启动，以及账户余额。",
    startGuideFirst: "请先开始 AI 引导",
    writeSomething: "先写一点你的想法，或点「提示一下」",
    submitFailed: "提交失败",
    gradingMsg: "AI 正在批改…",
    timeoutReply: "等待超时，请再试一次。",
    reqFailedRetry: "请求失败，请稍后重试。",
    ocrProcessing: "正在识别文字并看懂图中的几何图形…",
    ocrFailed: "识别失败",
    ocrDone: "识别完成，请检查错字",
    imageAttached: "已附上原题图片",
    visionOk: "已按原图描摹，可叠加拖动",
    visionNeedKey: "看图需要百炼 Key（.env 里 DASHSCOPE_API_KEY）",
    netError: "网络异常，请确认服务已启动。",
    cameraUnsupported: "当前浏览器不支持摄像头，请用「拍照」或上传图片。",
    cameraFailed: "无法打开摄像头，请检查权限。",
    cameraNotReady: "摄像头还没准备好",
    copyFailed: "复制失败，请手动选择文本复制",
    hintPrefix: "提示：",
    aiStart: "开始吧！",
    defaultFeedback: "请按 AI 的引导写你的第一步。",
    noCamera: "当前浏览器不支持摄像头，请用「拍照」或上传图片。",
    workbenchTitle: "几何画板",
    workbenchHint: "拖动可平移/缩放（题干已知角保持不变）· 可叠原图 · 可还原",
    workbenchHintSolid: "拖动可旋转查看 · 形状固定不可拖边 · 画笔可标注",
    toolMove: "拖动",
    toolRotate: "旋转",
    toolPen: "画笔",
    toolEraser: "橡皮",
    toolClear: "清空标注",
    toolBgFigure: "示意图",
    toolBgPhoto: "叠加原图",
    toolBgPhotoOnly: "只看原图",
    toolResetGeo: "还原图形",
    resetGeoDone: "已还原为刚描摹的图形",
    noBaseline: "当前没有可还原的图形",
    noPhoto: "还没有原题照片，请先拍照或上传图片。",
    clearImage: "清空图片",
    clearText: "清空文字",
    imageCleared: "已清空图片",
    needStartFirst: "请先开始一道题的 AI 引导",
    noDoneYet: "还没有完成的解答",
    textCleared: "已清空题目文字",
    voiceInput: "语音输入",
    voiceStop: "停止录音",
    voiceListening: "正在录音…再说完点一次结束",
    voiceRecognizing: "正在识别…",
    voiceDone: "已写入文字，可继续改",
    voiceUnsupported: "无法使用麦克风。请用 Chrome / Edge，并允许麦克风权限。",
    voiceError: "语音识别失败，请检查麦克风权限后重试。",
    voiceNoKey: "未配置百炼 API Key（DASHSCOPE_API_KEY），语音识别不可用。",
    voiceEmpty: "没有识别出文字，请再试一次。",
    answerLabel: "你的回答",
    sfxMute: "关闭音效",
    sfxUnmute: "打开音效",
  },
  en: {
    brandName: "PathSolve",
    title: "Guided step by step, made to solve",
    subtitle: "Plane & solid geometry · photo · auto figure · DeepSeek guides",
    homeTitle: "Home",
    searchTitle: "Search Problems",
    guideTitle: "Quick Practice",
    doneTitle: "Full Solution",
    homeGreet: "<span class=\"greet-line\">Good morning,</span><br /><span class=\"greet-line\">What would you like to learn today?</span>",
    logoReplayTip: "Click to replay intro",
    entrySearch: "Search Problems",
    entrySearchDesc: "Photo / upload / paste a screenshot — OCR and geometry tracing",
    entryPractice: "Quick Practice",
    entryPracticeDesc: "Pick a sample; AI guides step by step for plane & solid figures",
    problemEditable: "Editable",
    guideMeta: "Step by step",
    boardEmpty: "Pick a sample to start — the board appears here",
    boardEmptySearch: "Upload a problem — the diagram appears here",
    dropHintShort: "Image preview will appear here",
    previewZoomTip: "Click to enlarge",
    closePreview: "Close",
    confirm: "Confirm",
    reviewTitleShort: "Feedback",
    back: "Back",
    backHome: "Back home",
    needStartFirst: "Please start AI guidance on a problem first",
    noDoneYet: "No completed solution yet",
    step1: "1. Enter the Problem",
    dropTitle: "Drag an image here, or press Ctrl+V to paste a screenshot",
    dropHint: "Also supports phone camera and photo gallery",
    upload: "Upload",
    uploadLocal: "From device",
    uploadHelp: "Drag & drop or click to upload a problem image. You can also paste a screenshot.",
    uploadFormats: "Supported image formats",
    uploadFormatsTip: "JPG, PNG, WEBP, GIF",
    takePhoto: "Take Photo",
    openCamera: "Open Camera",
    snap: "Snap & Recognize",
    closeCamera: "Close Camera",
    problemLabel: "Problem text",
    problemPlaceholder: "After photo/paste, text appears here; you can also type directly.\nIf you've already written part of the solution, paste it here and AI will continue from your reasoning.",
    startGuide: "Confirm",
    step2: "AI Guidance",
    answerPlaceholder: "Write your answer (Enter send, Ctrl+Enter newline)",
    hint: "I'm stuck, give me a hint",
    hintAsked: "(I'm stuck — please give a hint)",
    hintLoading: "Thinking of a hint…",
    hintReady: "Hint ready — try the next step.",
    submit: "Submit Answer",
    fullSolution: "Full Solution",
    doneBanner: "Done · Feedback first, then the full solution",
    reviewTitle: "Feedback & Suggestions",
    reviewStrengths: "What went well",
    reviewImprovements: "What to improve",
    reviewSuggestions: "Tips & next steps",
    reviewLoading: "Generating a more detailed review…",
    reviewReady: "",
    copy: "Copy all (with feedback)",
    copied: "Copied",
    footer: "Powered by DeepSeek · One step at a time, encouraging you to think",
    thinking: "AI thinking…",
    grading: "AI grading…",
    connecting: "PathSolve is thinking — first tip coming right up…",
    started: "Guidance started. Answer step by step below.",
    enterProblem: "Please enter or recognize a problem first (or pick an example above)",
    startFailed: "Start failed",
    timeoutStart: "Timed out. Please click \"Start AI Guidance\" again.",
    reqFailed: "Request failed. Check your network, server, and account balance.",
    startGuideFirst: "Please start AI guidance first",
    writeSomething: "Write something, or click \"hint\"",
    submitFailed: "Submit failed",
    gradingMsg: "AI is grading…",
    timeoutReply: "Timed out. Please try again.",
    reqFailedRetry: "Request failed. Please try again later.",
    ocrProcessing: "Reading text and geometry from the image…",
    ocrFailed: "Recognition failed",
    ocrDone: "Recognition done. Please check for errors.",
    imageAttached: "Original photo attached",
    visionOk: "Traced from photo — drag to adjust",
    visionNeedKey: "Vision needs a Bailian key (DASHSCOPE_API_KEY in .env)",
    netError: "Network error. Make sure the server is running.",
    cameraUnsupported: "Camera not supported. Use \"Take Photo\" or upload.",
    cameraFailed: "Cannot open camera. Please check permissions.",
    cameraNotReady: "Camera not ready yet",
    copyFailed: "Copy failed. Please select text manually.",
    hintPrefix: "Hint: ",
    aiStart: "Let's start!",
    defaultFeedback: "Follow the AI's guidance and write your first step.",
    noCamera: "Camera not supported by this browser.",
    workbenchTitle: "Geometry Board",
    workbenchHint: "Drag to move/scale (given angles stay fixed) · overlay · reset",
    workbenchHintSolid: "Drag to rotate view · shape is locked · pen for notes",
    toolMove: "Move",
    toolRotate: "Rotate",
    toolPen: "Pen",
    toolEraser: "Eraser",
    toolClear: "Clear marks",
    toolBgFigure: "Diagram",
    toolBgPhoto: "Overlay photo",
    toolBgPhotoOnly: "Photo only",
    toolResetGeo: "Reset figure",
    resetGeoDone: "Restored to the traced figure",
    noBaseline: "Nothing to restore yet",
    noPhoto: "No problem photo yet. Please take or upload one first.",
    clearImage: "Clear image",
    clearText: "Clear text",
    imageCleared: "Image cleared",
    textCleared: "Problem text cleared",
    voiceInput: "Voice input",
    voiceStop: "Stop",
    voiceListening: "Recording… tap again when done",
    voiceRecognizing: "Recognizing…",
    voiceDone: "Text inserted. You can edit it.",
    voiceUnsupported: "Microphone unavailable. Use Chrome/Edge and allow mic access.",
    voiceError: "Speech recognition failed. Check mic permission and try again.",
    voiceNoKey: "DASHSCOPE_API_KEY is not configured. Voice input unavailable.",
    voiceEmpty: "No speech detected. Please try again.",
    answerLabel: "Your answer",
    sfxMute: "Mute sounds",
    sfxUnmute: "Unmute sounds",
  },
};

// ===== Apple 风格轻 UI 音效（WebAudio 预解码；pointerdown 触发以降低延迟）=====
const SFX_VER = "20260720m";
const SFX_FILES = {
  click: `/static/vfx/click.wav?v=${SFX_VER}`,
  pop: `/static/vfx/pop.wav?v=${SFX_VER}`,
  send: `/static/vfx/send.wav?v=${SFX_VER}`,
  ok: `/static/vfx/ok.wav?v=${SFX_VER}`,
  bad: `/static/vfx/bad.wav?v=${SFX_VER}`,
  splash: `/static/vfx/splash.wav?v=${SFX_VER}`,
  done: `/static/vfx/done.wav?v=${SFX_VER}`,
  nav: `/static/vfx/nav.wav?v=${SFX_VER}`,
  hint: `/static/vfx/hint.wav?v=${SFX_VER}`,
  copy: `/static/vfx/copy.wav?v=${SFX_VER}`,
  toggle: `/static/vfx/toggle.wav?v=${SFX_VER}`,
  think: `/static/vfx/think.wav?v=${SFX_VER}`,
};
const SFX_VOLUME = {
  click: 0.28,
  pop: 0.42,
  send: 0.45,
  ok: 0.48,
  bad: 0.42,
  splash: 0.36,
  done: 0.52,
  nav: 0.36,
  hint: 0.44,
  copy: 0.42,
  toggle: 0.4,
  think: 0.28,
};
const SFX_THROTTLE_MS = 45;
const SFX_MUTE_KEY = "pathsolve-sfx-muted";
const SFX_CLICK_SEL = [
  "button",
  "a[href]",
  "[role='button']",
  "summary",
  ".chip",
  ".tab",
  ".tool-icon",
  ".icon-btn",
  ".side-btn",
  ".side-logo",
  ".home-entry",
  ".btn-coral",
  ".btn-back",
  ".linkish",
  "label[for]",
  "input[type='file']",
  "input[type='checkbox']",
  "input[type='radio']",
].join(",");
let sfxMuted = false;
try { sfxMuted = localStorage.getItem(SFX_MUTE_KEY) === "1"; } catch (_) { /* ignore */ }
let sfxCtx = null;
let sfxMaster = null;
const sfxBuffers = {};
const sfxRawCache = {}; // arrayBuffer 预取，不依赖 AudioContext 解锁
let sfxLoadPromise = null;
const sfxLastPlay = {};

function syncMuteBtn() {
  const btn = $("btnSfxMute");
  if (!btn) return;
  btn.classList.toggle("is-muted", sfxMuted);
  const tip = sfxMuted ? t("sfxUnmute") : t("sfxMute");
  btn.title = tip;
  btn.setAttribute("aria-label", tip);
  btn.setAttribute("aria-pressed", sfxMuted ? "true" : "false");
}

function getSfxCtx() {
  const AC = window.AudioContext || window.webkitAudioContext;
  if (!AC) return null;
  if (!sfxCtx) {
    sfxCtx = new AC();
    sfxMaster = sfxCtx.createGain();
    sfxMaster.gain.value = 1;
    sfxMaster.connect(sfxCtx.destination);
  }
  if (sfxCtx.state === "suspended") {
    sfxCtx.resume().catch(() => {});
  }
  return sfxCtx;
}

async function ensureSfxBuffer(name) {
  if (sfxBuffers[name]) return sfxBuffers[name];
  const ctx = getSfxCtx();
  if (!ctx || !SFX_FILES[name]) return null;
  try {
    let raw = sfxRawCache[name];
    if (!raw) {
      const res = await fetch(SFX_FILES[name]);
      raw = await res.arrayBuffer();
      sfxRawCache[name] = raw;
    }
    sfxBuffers[name] = await ctx.decodeAudioData(raw.slice(0));
    return sfxBuffers[name];
  } catch (_) {
    return null;
  }
}

function preloadSfx() {
  if (sfxLoadPromise) return sfxLoadPromise;
  // 先并行 fetch，再解码；click / splash 优先
  const order = ["click", "splash", ...Object.keys(SFX_FILES).filter((k) => k !== "click" && k !== "splash")];
  sfxLoadPromise = (async () => {
    await Promise.all(order.map(async (name) => {
      if (sfxRawCache[name]) return;
      try {
        const res = await fetch(SFX_FILES[name]);
        sfxRawCache[name] = await res.arrayBuffer();
      } catch (_) { /* ignore */ }
    }));
    getSfxCtx();
    for (const name of order) {
      await ensureSfxBuffer(name);
    }
    return true;
  })();
  return sfxLoadPromise;
}

function setSfxMuted(muted) {
  const next = !!muted;
  const changed = next !== sfxMuted;
  sfxMuted = next;
  try { localStorage.setItem(SFX_MUTE_KEY, sfxMuted ? "1" : "0"); } catch (_) { /* ignore */ }
  syncMuteBtn();
  if (changed && !sfxMuted) {
    unlockSfx();
    playSfx("toggle");
  }
}

function unlockSfx() {
  const ctx = getSfxCtx();
  if (!ctx) return;
  // 空缓冲暖机，减少首次可闻音的管线延迟
  try {
    if (ctx.state === "suspended") ctx.resume();
    const silent = ctx.createBuffer(1, 1, ctx.sampleRate);
    const src = ctx.createBufferSource();
    src.buffer = silent;
    src.connect(sfxMaster || ctx.destination);
    src.start(0);
  } catch (_) { /* ignore */ }
  preloadSfx();
}

function playSfx(name) {
  if (sfxMuted || !SFX_FILES[name]) return;
  const now = performance.now();
  if (sfxLastPlay[name] && now - sfxLastPlay[name] < SFX_THROTTLE_MS) return;
  const ctx = getSfxCtx();
  if (!ctx) return;
  const buf = sfxBuffers[name];
  if (!buf) {
    // 未就绪：后台补齐，本次不延迟补播（避免“晚半拍”）
    ensureSfxBuffer(name);
    return;
  }
  const start = () => {
    if (sfxMuted || !sfxBuffers[name]) return;
    const t = performance.now();
    if (sfxLastPlay[name] && t - sfxLastPlay[name] < SFX_THROTTLE_MS) return;
    sfxLastPlay[name] = t;
    try {
      const src = ctx.createBufferSource();
      const gain = ctx.createGain();
      src.buffer = sfxBuffers[name];
      gain.gain.value = SFX_VOLUME[name] != null ? SFX_VOLUME[name] : 0.4;
      src.connect(gain);
      gain.connect(sfxMaster || ctx.destination);
      src.start(0);
    } catch (_) { /* ignore */ }
  };
  if (ctx.state === "suspended") {
    ctx.resume().then(start).catch(() => {});
    return;
  }
  start();
}

function playClickSfx() {
  playSfx("click");
}

function sfxTargetFromEvent(e) {
  const el = e.target && e.target.closest ? e.target.closest(SFX_CLICK_SEL + ",[data-sfx]") : null;
  if (!el) return null;
  if (el.disabled || el.getAttribute("aria-disabled") === "true") return null;
  if (el.classList.contains("visually-hidden") || el.closest(".visually-hidden")) return null;
  if (el.id === "btnSfxMute") return null;
  return el;
}

function triggerUiSfx(el) {
  if (!el || sfxMuted) return;
  const custom = el.getAttribute("data-sfx");
  if (custom) playSfx(custom);
  else playClickSfx();
}

// 按下即播（比 click 早一整段），并顺带解锁音频
document.addEventListener("pointerdown", (e) => {
  if (e.button != null && e.button !== 0) return;
  unlockSfx();
  if (sfxMuted) return;
  triggerUiSfx(sfxTargetFromEvent(e));
}, true);

document.addEventListener("keydown", (e) => {
  if (e.key !== "Enter" && e.key !== " ") return;
  unlockSfx();
  if (sfxMuted) return;
  const el = sfxTargetFromEvent(e);
  if (!el || (el.tagName === "INPUT" || el.tagName === "TEXTAREA" || el.isContentEditable)) return;
  triggerUiSfx(el);
}, true);

// 页面一进来就预取 WAV（不播放），后续点击即可即时出声
preloadSfx();

const SAMPLES = {
  zh: [
    { title: "2023·三角形内角和", text: "在△ABC中，∠A=50°，∠B=60°，求∠C的度数。" },
    { title: "2022·平行线求角度", text: "如图，在△ABC中，D、E分别是AB、AC上的点，DE∥BC，∠ADE=70°，∠A=40°，求∠C的度数。" },
    { title: "2021·角平分线", text: "在△ABC中，∠A=80°，∠B=60°，AD是∠BAC的角平分线，交BC于点D，求∠ADC的度数。" },
    { title: "2022·等腰三角形求角", text: "在等腰△ABC中，AB=AC，∠A=40°，D是BC边上的中点，连接AD，求∠BAD的度数。" },
    { title: "2023·平行线+角平分线综合", text: "如图，AB∥CD，EF平分∠AEC，∠A=50°，∠C=30°，求∠AEF的度数。" },
    { title: "2024·直角三角形+互余", text: "在Rt△ABC中，∠C=90°，∠A=2∠B，求∠A和∠B的度数。" },
    { title: "2023·三角形外角性质", text: "如图，在△ABC中，∠A=30°，∠B=50°，延长BC至点D，求∠ACD的度数。" },
    { title: "2024·等边三角形+平行线", text: "在等边△ABC中，D是AC边上一点，过D作DE∥AB交BC于E，若∠EDC=20°，求∠BDE的度数。" },
    { title: "立体·正方体表面积", text: "一个正方体的棱长为 6cm，求它的表面积。" },
    { title: "立体·长方体体积", text: "一个长方体的长、宽、高分别是 5cm、3cm、4cm，求它的体积和表面积。" },
    { title: "立体·圆柱侧面积", text: "一个圆柱的底面半径是 3cm，高是 8cm，求它的侧面积和体积。（π 取 3.14）" },
    { title: "立体·圆锥体积", text: "一个圆锥的底面半径为 4cm，高为 9cm，求它的体积。（π 取 3.14）" },
  ],
  en: [
    { title: "Triangle Angle Sum", text: "In triangle ABC, angle A = 50°, angle B = 60°. Find angle C." },
    { title: "Parallel Lines + Angle Sum", text: "In triangle ABC, D and E are on AB and AC respectively, DE ∥ BC, angle ADE = 70°, angle A = 40°. Find angle C." },
    { title: "Angle Bisector", text: "In triangle ABC, angle A = 80°, angle B = 60°. AD bisects angle BAC and meets BC at D. Find angle ADC." },
    { title: "Isosceles Triangle", text: "In isosceles triangle ABC, AB = AC, angle A = 40°. D is the midpoint of BC. Find angle BAD." },
    { title: "Parallel + Bisector", text: "AB ∥ CD, EF bisects angle AEC, angle A = 50°, angle C = 30°. Find angle AEF." },
    { title: "Right Triangle", text: "In right triangle ABC, angle C = 90°, angle A = 2 × angle B. Find angles A and B." },
    { title: "Exterior Angle", text: "In triangle ABC, angle A = 30°, angle B = 50°. Extend BC to point D. Find angle ACD." },
    { title: "Equilateral + Parallel", text: "In equilateral triangle ABC, D is on AC. DE ∥ AB meets BC at E. If angle EDC = 20°, find angle BDE." },
    { title: "Solid · Cube surface", text: "A cube has edge length 6 cm. Find its surface area." },
    { title: "Solid · Cuboid volume", text: "A rectangular prism has length 5 cm, width 3 cm, height 4 cm. Find its volume and surface area." },
    { title: "Solid · Cylinder", text: "A cylinder has base radius 3 cm and height 8 cm. Find its lateral area and volume. (Use π = 3.14)" },
    { title: "Solid · Cone volume", text: "A cone has base radius 4 cm and height 9 cm. Find its volume. (Use π = 3.14)" },
  ],
};

const $ = (id) => document.getElementById(id);
const t = (key) => (I18N[currentLang] && I18N[currentLang][key]) || I18N.zh[key] || key;

const problemText = $("problemText");
const guidePanel = $("guidePanel");
const donePanel = $("donePanel");
const dropZone = $("dropZone");
const preview = $("preview");
const ocrStatus = $("ocrStatus");
const chatLog = $("chatLog");
const startStatus = $("startStatus");
let currentScreen = "home";
let hasDoneSolution = false;
let screenHistory = [];

const SCREEN_TITLE = {
  home: "homeTitle",
  search: "searchTitle",
  guide: "guideTitle",
  done: "doneTitle",
};

function goBack() {
  const fallback = {
    search: "home",
    guide: "home",
    done: "guide",
  };
  let prev = screenHistory.length ? screenHistory.pop() : (fallback[currentScreen] || "home");
  if (prev === currentScreen) prev = fallback[currentScreen] || "home";
  if (prev === "done" && !hasDoneSolution) prev = "guide";
  if (prev === "guide" && currentScreen === "guide") prev = "home";
  showScreen(prev, { force: true, replace: true });
}

function showScreen(name, opts) {
  const options = opts || {};
  if (name === "done" && !hasDoneSolution && !options.force) {
    alert(t("noDoneYet"));
    name = sessionId ? "guide" : "home";
  }

  const prevScreen = currentScreen;
  if (!options.replace && currentScreen && currentScreen !== name) {
    screenHistory.push(currentScreen);
    if (screenHistory.length > 12) screenHistory.shift();
  }
  if (name === "home") screenHistory = [];

  currentScreen = name;
  const screens = {
    home: $("screen-home"),
    search: $("screen-search"),
    guide: guidePanel,
    done: donePanel,
  };
  Object.entries(screens).forEach(([key, el]) => {
    if (!el) return;
    const on = key === name;
    el.classList.toggle("active", on);
    el.hidden = !on;
  });

  const body = document.querySelector(".body");
  const rail = $("rightRail");
  if (body) body.classList.toggle("home-mode", name === "home");
  if (rail) rail.hidden = name === "home";

  const pillText = $("statusPillText");
  if (pillText) {
    if (sessionId && (name === "guide" || name === "search" || name === "done")) {
      pillText.textContent = t("started");
    } else if (name === "search" && (ocrStatus.textContent || "").trim()) {
      pillText.textContent = ocrStatus.textContent;
    } else {
      pillText.textContent = "";
    }
  }

  if (name === "search" || name === "guide") {
    placeWorkbenchForScreen(name);
  }

  if (name === "guide") {
    requestAnimationFrame(() => {
      try { resizeCanvas(); } catch (_) { /* not ready */ }
      playBoardAppear();
    });
  }

  // 搜题 / 引导 / 完成：面板轻入场
  if (name !== "home" && prevScreen !== name) {
    const target = screens[name];
    if (target) requestAnimationFrame(() => playScreenEnter(target));
  }
  if (name === "search" && prevScreen !== "search") {
    requestAnimationFrame(playBoardAppear);
  }
  if (name === "done" && prevScreen !== "done") {
    requestAnimationFrame(playDoneEnter);
  } else if (prevScreen && prevScreen !== name) {
    // 完成页用 done 音；其它切屏用轻导航音
    playSfx("nav");
  }

  // 回到首页且开场已结束时，重播首页入场
  if (name === "home" && prevScreen !== "home") {
    const splash = $("splash");
    if (!splash || splash.classList.contains("is-done")) {
      requestAnimationFrame(playHomeEnter);
    }
  }
}

function syncWorkbenchEmpty() {
  const empty = $("workbenchEmpty");
  if (!empty) return;
  const fig = $("figureLayer");
  const hasSvg = !!(fig && fig.querySelector("svg"));
  const solid = $("solidCanvas");
  const hasSolid = !!(solid && !solid.hidden);
  const photo = $("photoLayer");
  const hasPhoto = !!(photo && !photo.hidden && photo.getAttribute("src"));
  empty.hidden = hasSvg || hasSolid || hasPhoto;
  // 搜索页 / 练习页空态文案不同
  const key = currentScreen === "guide" ? "boardEmpty" : "boardEmptySearch";
  empty.setAttribute("data-i18n", key);
  empty.textContent = t(key);
}

/** 画板在搜索页与练习页之间共用同一套 DOM */
function placeWorkbenchForScreen(name) {
  const bundle = $("workbenchBundle");
  if (!bundle) return;
  const mountId = name === "guide" ? "workbenchMountGuide" : "workbenchMountSearch";
  const mount = $(mountId);
  if (!mount) return;
  if (bundle.parentElement !== mount) mount.appendChild(bundle);
  syncWorkbenchEmpty();
  requestAnimationFrame(() => {
    resizeCanvas();
    syncBgMode();
    if (window.Solid3D && typeof Solid3D.resize === "function") Solid3D.resize();
  });
}

function syncSearchBoardPreview() {
  // 兼容旧调用：搜索页已改用共享画板，不再用原图冒充示意图
  placeWorkbenchForScreen(currentScreen === "guide" ? "guide" : "search");
  syncWorkbenchEmpty();
}

// ===== Language switcher =====
function applyLang() {
  stopVoiceInput(false);
  document.querySelectorAll("[data-i18n]").forEach((el) => {
    const key = el.getAttribute("data-i18n");
    const val = t(key);
    const input = el.querySelector("input");
    el.textContent = val;
    if (input) el.appendChild(input);
  });
  document.querySelectorAll("[data-i18n-html]").forEach((el) => {
    el.innerHTML = t(el.getAttribute("data-i18n-html"));
  });
  problemText.placeholder = t("problemPlaceholder");
  answerBox.placeholder = t("answerPlaceholder");
  document.documentElement.lang = currentLang === "zh" ? "zh-CN" : "en";
  renderSamples();
  btnLangZh.classList.toggle("active", currentLang === "zh");
  btnLangEn.classList.toggle("active", currentLang === "en");
  const langBtn = $("btnLangToggle");
  if (langBtn) {
    langBtn.classList.toggle("is-zh", currentLang === "zh");
    langBtn.classList.toggle("is-en", currentLang === "en");
    langBtn.title = currentLang === "zh" ? "Switch to English" : "切换到中文";
  }
  if (!busy) btnStart.textContent = t("confirm");
  document.querySelectorAll("[data-i18n-title]").forEach((el) => {
    const tip = t(el.getAttribute("data-i18n-title"));
    el.title = tip;
    if (el.id === "btnReplaySplash") el.setAttribute("aria-label", tip);
  });
  syncMuteBtn();
}

function renderSamples() {
  const container = samples;
  container.innerHTML = "";
  SAMPLES[currentLang].forEach((s) => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "chip";
    btn.textContent = s.title;
    btn.dataset.text = s.text;
    btn.addEventListener("click", () => {
      problemText.value = s.text;
      container.querySelectorAll(".chip").forEach((c) => c.classList.remove("on"));
      btn.classList.add("on");
    });
    container.appendChild(btn);
  });
}

btnLangZh.addEventListener("click", () => { currentLang = "zh"; applyLang(); });
btnLangEn.addEventListener("click", () => { currentLang = "en"; applyLang(); });

function pickLocalImage() {
  const input = $("fileInput");
  if (input) input.click();
}

if (fileInput) {
  fileInput.addEventListener("change", (e) => {
    const file = e.target.files && e.target.files[0];
    if (file) handleImageFile(file);
    e.target.value = "";
  });
}

function bindImageDropTarget(el) {
  if (!el) return;
  el.addEventListener("dragover", (e) => {
    e.preventDefault();
    el.classList.add("dragover");
  });
  el.addEventListener("dragleave", (e) => {
    if (e.relatedTarget && el.contains(e.relatedTarget)) return;
    el.classList.remove("dragover");
  });
  el.addEventListener("drop", (e) => {
    e.preventDefault();
    el.classList.remove("dragover");
    const file = e.dataTransfer.files && e.dataTransfer.files[0];
    if (file && file.type.startsWith("image/")) handleImageFile(file);
  });
}

bindImageDropTarget(dropZone);
bindImageDropTarget($("previewCard"));

document.addEventListener("paste", (e) => {
  const items = e.clipboardData && e.clipboardData.items;
  if (!items) return;
  for (const item of items) {
    if (item.type.startsWith("image/")) {
      e.preventDefault();
      const file = item.getAsFile();
      if (file) handleImageFile(file);
      break;
    }
  }
});

const btnUploadMain = $("btnUploadMain");
const btnTakePhoto = $("btnTakePhoto");
if (btnUploadMain) btnUploadMain.addEventListener("click", pickLocalImage);
if (btnTakePhoto) btnTakePhoto.addEventListener("click", openCamera);
btnCloseCamera.addEventListener("click", closeCamera);
btnSnap.addEventListener("click", snapFromCamera);
$("btnClearImage").addEventListener("click", (e) => {
  e.stopPropagation();
  clearCurrentImage();
});
const btnOpenPreview = $("btnOpenPreview");
if (btnOpenPreview) btnOpenPreview.addEventListener("click", openPreviewLightbox);
const btnCloseLightbox = $("btnCloseLightbox");
const btnCloseLightboxX = $("btnCloseLightboxX");
if (btnCloseLightbox) btnCloseLightbox.addEventListener("click", closePreviewLightbox);
if (btnCloseLightboxX) btnCloseLightboxX.addEventListener("click", closePreviewLightbox);
document.addEventListener("keydown", (e) => {
  if (e.key !== "Escape") return;
  const box = $("imgLightbox");
  if (box && !box.hidden) closePreviewLightbox();
});
$("btnClearText").addEventListener("click", clearProblemText);
if ($("btnVoiceProblem")) {
  $("btnVoiceProblem").addEventListener("click", () => toggleVoiceInput("problem"));
}
if ($("btnVoiceAnswer")) {
  $("btnVoiceAnswer").addEventListener("click", () => toggleVoiceInput("answer"));
}
btnStart.addEventListener("click", startAiGuide);
btnSubmit.addEventListener("click", () => sendReply(false));
btnHint.addEventListener("click", () => sendReply(true));

const ANSWER_BOX_MIN_PX = 36;
const ANSWER_BOX_MAX_PX = 148;
function resizeAnswerBox() {
  const box = answerBox;
  if (!box) return;
  const bar = box.closest(".answer-bar");
  box.style.height = "auto";
  const next = Math.min(Math.max(box.scrollHeight, ANSWER_BOX_MIN_PX), ANSWER_BOX_MAX_PX);
  box.style.height = `${next}px`;
  if (bar) bar.classList.toggle("is-tall", next > ANSWER_BOX_MIN_PX + 4);
}

if (answerBox) {
  // Enter 发送；Ctrl+Enter（或 Cmd+Enter）换行并增高
  answerBox.addEventListener("keydown", (e) => {
    if (e.key !== "Enter") return;
    if (e.isComposing || e.keyCode === 229) return; // 中文输入法组字中
    if (e.ctrlKey || e.metaKey) {
      e.preventDefault();
      const start = answerBox.selectionStart;
      const end = answerBox.selectionEnd;
      const val = answerBox.value;
      answerBox.value = `${val.slice(0, start)}\n${val.slice(end)}`;
      const pos = start + 1;
      answerBox.selectionStart = pos;
      answerBox.selectionEnd = pos;
      resizeAnswerBox();
      return;
    }
    e.preventDefault();
    if (!btnSubmit.disabled) sendReply(false);
  });
  answerBox.addEventListener("input", resizeAnswerBox);
  resizeAnswerBox();
}

btnCopy.addEventListener("click", async () => {
  const parts = [finalWriteup.textContent || ""];
  const reviewCard = $("reviewCard");
  if (reviewCard && !reviewCard.hidden) {
    const summary = ($("reviewSummary") && $("reviewSummary").textContent) || "";
    const listText = (id, titleKey) => {
      const items = [...($(id)?.querySelectorAll("li") || [])].map((li) => `- ${li.textContent}`);
      if (!items.length) return "";
      return `${t(titleKey)}\n${items.join("\n")}`;
    };
    const body = [
      t("reviewTitle"),
      summary,
      listText("reviewStrengths", "reviewStrengths"),
      listText("reviewImprovements", "reviewImprovements"),
      listText("reviewSuggestions", "reviewSuggestions"),
    ].filter(Boolean).join("\n\n");
    if (body) parts.push(body);
  }
  const text = parts.join("\n\n").trim();
  try {
    await navigator.clipboard.writeText(text);
    playSfx("copy");
    btnCopy.textContent = t("copied");
    setTimeout(() => (btnCopy.textContent = t("copy")), 1200);
  } catch { alert(t("copyFailed")); }
});

function fillReviewList(ul, items) {
  if (!ul) return;
  ul.innerHTML = "";
  (items || []).forEach((item) => {
    const li = document.createElement("li");
    li.textContent = item;
    ul.appendChild(li);
  });
}

function showReview(review, statusText) {
  const card = $("reviewCard");
  if (!card) return;
  const statusEl = $("reviewStatus");
  // 完成页始终显示反馈区；没有数据时用兜底文案，不再 hidden 整块
  const fallback = {
    summary: currentLang === "en"
      ? "You finished the problem. Here is quick feedback."
      : "这道题你已经做完了。下面是针对过程的反馈与建议。",
    strengths: [currentLang === "en" ? "You completed the guided problem." : "能跟着引导把整道题做完。"],
    improvements: [currentLang === "en" ? "Try stating the key property before calculating." : "关键步骤可以先说出用到的性质/定理。"],
    suggestions: [currentLang === "en" ? "Practice a similar problem next." : "可以再练一道同类题巩固。"],
  };
  const data = review && typeof review === "object" ? review : fallback;
  const summary = (data.summary || fallback.summary).trim();
  const strengths = (data.strengths && data.strengths.length) ? data.strengths : fallback.strengths;
  const improvements = (data.improvements && data.improvements.length) ? data.improvements : fallback.improvements;
  const suggestions = (data.suggestions && data.suggestions.length) ? data.suggestions : fallback.suggestions;

  $("reviewSummary").textContent = summary;
  fillReviewList($("reviewStrengths"), strengths);
  fillReviewList($("reviewImprovements"), improvements);
  fillReviewList($("reviewSuggestions"), suggestions);
  card.hidden = false;
  if (statusEl) {
    if (statusText) {
      statusEl.textContent = statusText;
      statusEl.hidden = false;
    } else {
      statusEl.textContent = "";
      statusEl.hidden = true;
    }
  }
}

async function enrichReviewIfNeeded(review) {
  if (!sessionId) return;
  const needsEnrich = !review || review.source === "local" || !review.summary;
  if (!needsEnrich) return;
  const statusEl = $("reviewStatus");
  if (statusEl) {
    statusEl.textContent = t("reviewLoading");
    statusEl.hidden = false;
  }
  try {
    const data = await fetchJson(`/api/ai/${sessionId}/review`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
    }, 60000);
    if (data && data.ok && data.review) {
      showReview(data.review);
    } else if (statusEl) {
      statusEl.hidden = true;
    }
  } catch {
    if (statusEl) statusEl.hidden = true;
  }
}

async function openCamera() {
  if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) { alert(t("noCamera")); return; }
  try {
    cameraStream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: { ideal: "environment" } }, audio: false,
    });
    cameraPanel.hidden = false;
    cameraVideo.srcObject = cameraStream;
  } catch { alert(t("cameraFailed")); }
}

function closeCamera() {
  if (cameraStream) { cameraStream.getTracks().forEach((tr) => tr.stop()); cameraStream = null; }
  cameraVideo.srcObject = null;
  cameraPanel.hidden = true;
}

async function snapFromCamera() {
  const video = cameraVideo;
  if (!video.videoWidth) return alert(t("cameraNotReady"));
  const canvas = document.createElement("canvas");
  canvas.width = video.videoWidth; canvas.height = video.videoHeight;
  canvas.getContext("2d").drawImage(video, 0, 0);
  const blob = await new Promise((res) => canvas.toBlob(res, "image/jpeg", 0.92));
  if (!blob) return;
  await handleImageFile(new File([blob], "camera.jpg", { type: "image/jpeg" }));
}

let previewObjectUrl = null;

function showPreview(file) {
  if (previewObjectUrl) {
    URL.revokeObjectURL(previewObjectUrl);
    previewObjectUrl = null;
  }
  const url = URL.createObjectURL(file);
  previewObjectUrl = url;
  preview.src = url;
  const openBtn = $("btnOpenPreview");
  if (openBtn) openBtn.hidden = false;
  const dropHint = $("dropHintText");
  if (dropHint) dropHint.hidden = true;
}

function getPreviewSrc() {
  if (currentImageBase64) {
    return `data:${currentImageMime || "image/jpeg"};base64,${currentImageBase64}`;
  }
  return (preview && preview.src) || "";
}

function openPreviewLightbox() {
  const src = getPreviewSrc();
  if (!src) return;
  const box = $("imgLightbox");
  const img = $("lightboxImg");
  if (!box || !img) return;
  img.src = src;
  box.hidden = false;
  document.body.style.overflow = "hidden";
}

function closePreviewLightbox() {
  const box = $("imgLightbox");
  const img = $("lightboxImg");
  if (box) box.hidden = true;
  if (img) img.removeAttribute("src");
  document.body.style.overflow = "";
}

// ===== 语音输入（Web Speech API，Chrome / Edge）=====
let voiceRecorder = null;
let voiceStream = null;
let voiceChunks = [];
let voiceTarget = null; // "problem" | "answer"
let voiceBusy = false;

function pickRecorderMime() {
  const candidates = [
    "audio/webm;codecs=opus",
    "audio/webm",
    "audio/mp4",
    "audio/ogg;codecs=opus",
    "audio/ogg",
  ];
  if (!window.MediaRecorder) return "";
  for (const type of candidates) {
    if (MediaRecorder.isTypeSupported(type)) return type;
  }
  return "";
}

function voiceUi(target, listening, statusText) {
  const btn = $(target === "answer" ? "btnVoiceAnswer" : "btnVoiceProblem");
  const status = $(target === "answer" ? "voiceAnswerStatus" : "voiceProblemStatus");
  if (btn) {
    btn.classList.toggle("listening", !!listening);
    // 答题区语音按钮用图标切换（麦克风 ↔ 停止方块），不要用文字盖掉 SVG
    if (btn.id === "btnVoiceAnswer") {
      const tip = listening ? t("voiceStop") : t("voiceInput");
      btn.title = tip;
      btn.setAttribute("aria-label", tip);
    } else {
      btn.textContent = listening ? t("voiceStop") : t("voiceInput");
    }
    btn.disabled = !!voiceBusy && !listening;
  }
  if (status) {
    status.classList.remove("bad");
    if (statusText != null) status.textContent = statusText;
    else status.textContent = listening ? t("voiceListening") : "";
  }
}

function cleanupVoiceStream() {
  if (voiceStream) {
    try { voiceStream.getTracks().forEach((tr) => tr.stop()); } catch (_) {}
    voiceStream = null;
  }
  voiceRecorder = null;
  voiceChunks = [];
}

function stopVoiceInput(finalize) {
  const rec = voiceRecorder;
  if (rec && rec.state !== "inactive") {
    try { rec.stop(); } catch (_) {}
    // onstop handles upload when finalize !== false
    if (finalize === false) {
      rec.onstop = null;
      cleanupVoiceStream();
      if (voiceTarget) voiceUi(voiceTarget, false, "");
      voiceTarget = null;
    }
    return;
  }
  cleanupVoiceStream();
  if (voiceTarget) voiceUi(voiceTarget, false, "");
  voiceTarget = null;
}

async function uploadVoiceBlob(blob, target) {
  const box = target === "answer" ? answerBox : problemText;
  const status = $(target === "answer" ? "voiceAnswerStatus" : "voiceProblemStatus");
  voiceBusy = true;
  voiceUi(target, false, t("voiceRecognizing"));

  const form = new FormData();
  const ext = (blob.type || "").includes("mp4") ? "m4a"
    : (blob.type || "").includes("ogg") ? "ogg"
    : "webm";
  form.append("file", blob, `voice.${ext}`);

  try {
    const res = await fetch(`/api/asr?lang=${encodeURIComponent(currentLang === "en" ? "en" : "zh")}`, {
      method: "POST",
      body: form,
    });
    const data = await res.json();
    if (!data.ok) {
      if (status) {
        status.textContent = data.message || t("voiceError");
        status.classList.add("bad");
      }
      return;
    }
    const text = (data.text || "").trim();
    if (!text) {
      if (status) {
        status.textContent = t("voiceEmpty");
        status.classList.add("bad");
      }
      return;
    }
    const base = (box.value || "").replace(/\s+$/, "");
    box.value = base ? `${base}${base.endsWith("\n") ? "" : " "}${text}` : text;
    box.dispatchEvent(new Event("input", { bubbles: true }));
    if (status) {
      status.classList.remove("bad");
      status.textContent = t("voiceDone");
    }
  } catch (_) {
    if (status) {
      status.textContent = t("voiceError");
      status.classList.add("bad");
    }
  } finally {
    voiceBusy = false;
    voiceUi(target, false, status ? status.textContent : "");
    voiceTarget = null;
  }
}

async function toggleVoiceInput(target) {
  if (voiceBusy) return;

  if (!window.MediaRecorder || !navigator.mediaDevices?.getUserMedia) {
    alert(t("voiceUnsupported"));
    return;
  }

  // 再点一次：结束录音并识别
  if (voiceRecorder && voiceTarget === target) {
    voiceUi(target, false, t("voiceRecognizing"));
    try { voiceRecorder.stop(); } catch (_) {}
    return;
  }

  // 切换目标：丢掉当前录音
  if (voiceRecorder) stopVoiceInput(false);

  const status = $(target === "answer" ? "voiceAnswerStatus" : "voiceProblemStatus");
  const mime = pickRecorderMime();

  try {
    voiceStream = await navigator.mediaDevices.getUserMedia({ audio: true });
  } catch (_) {
    if (status) {
      status.textContent = t("voiceError");
      status.classList.add("bad");
    }
    return;
  }

  try {
    voiceChunks = [];
    voiceRecorder = mime
      ? new MediaRecorder(voiceStream, { mimeType: mime })
      : new MediaRecorder(voiceStream);
    const usedType = voiceRecorder.mimeType || mime || "audio/webm";

    voiceRecorder.ondataavailable = (ev) => {
      if (ev.data && ev.data.size > 0) voiceChunks.push(ev.data);
    };
    voiceRecorder.onstop = async () => {
      const chunks = voiceChunks.slice();
      const blobType = usedType.split(";")[0] || "audio/webm";
      cleanupVoiceStream();
      const blob = new Blob(chunks, { type: blobType });
      if (!blob.size) {
        if (status) {
          status.textContent = t("voiceEmpty");
          status.classList.add("bad");
        }
        voiceTarget = null;
        voiceUi(target, false, status ? status.textContent : "");
        return;
      }
      await uploadVoiceBlob(blob, target);
    };

    voiceTarget = target;
    voiceUi(target, true);
    voiceRecorder.start();
  } catch (_) {
    cleanupVoiceStream();
    if (status) {
      status.textContent = t("voiceError");
      status.classList.add("bad");
    }
  }
}

function clearCurrentImage() {
  currentImageBase64 = null;
  currentImageMime = null;
  currentGeometryDescription = "";
  currentVisionFigure = null;
  closePreviewLightbox();
  if (previewObjectUrl) {
    URL.revokeObjectURL(previewObjectUrl);
    previewObjectUrl = null;
  }
  preview.removeAttribute("src");
  const openBtn = $("btnOpenPreview");
  if (openBtn) openBtn.hidden = true;
  const dropHint = $("dropHintText");
  if (dropHint) dropHint.hidden = false;
  ocrStatus.textContent = t("imageCleared");
  ocrStatus.classList.remove("bad");
  if ($("fileInput")) $("fileInput").value = "";
  const photo = $("photoLayer");
  if (photo) {
    photo.removeAttribute("src");
    photo.hidden = true;
  }
  const fig = $("figureLayer");
  if (fig) fig.innerHTML = "";
  latestFigureData = null;
  latestFigureSvg = null;
  geoBaseline = null;
  geoState = null;
  currentVisionFigure = null;
  currentGeometryDescription = "";
  unmountSolidWorkbench();
  if (bgMode === "overlay" || bgMode === "photo") bgMode = "figure";
  syncPhotoToolsVisibility();
  syncBgMode();
  syncSearchBoardPreview();
  syncWorkbenchEmpty();
}

/** 无原图时隐藏「叠加原图 / 只看原图」 */
function syncPhotoToolsVisibility() {
  const hasPhoto = Boolean(currentImageBase64);
  const btnOverlay = $("toolBgPhoto");
  const btnPhoto = $("toolBgPhotoOnly");
  if (btnOverlay) btnOverlay.hidden = !hasPhoto;
  if (btnPhoto) btnPhoto.hidden = !hasPhoto;
  if (!hasPhoto && (bgMode === "overlay" || bgMode === "photo")) {
    bgMode = "figure";
  }
}

function clearProblemText() {
  problemText.value = "";
  ocrStatus.textContent = t("textCleared");
  ocrStatus.classList.remove("bad");
}

async function handleImageFile(file) {
  showPreview(file);
  ocrStatus.textContent = t("ocrProcessing");
  ocrStatus.classList.remove("bad");

  // 保存图片 base64，用于后续发送给 AI 视觉模型
  try {
    const reader = new FileReader();
    const dataUrl = await new Promise((resolve, reject) => {
      reader.onload = () => resolve(reader.result);
      reader.onerror = reject;
      reader.readAsDataURL(file);
    });
    const base64 = dataUrl.split(",")[1] || "";
    currentImageBase64 = base64;
    currentImageMime = file.type || "image/jpeg";
  } catch {
    currentImageBase64 = null;
    currentImageMime = null;
  }
  syncPhotoToolsVisibility();
  syncSearchBoardPreview();

  const form = new FormData();
  form.append("file", file, file.name || "problem.png");
  try {
    const res = await fetch("/api/ocr", { method: "POST", body: form });
    let data;
    try {
      data = await res.json();
    } catch {
      ocrStatus.textContent = t("ocrFailed") + `（HTTP ${res.status}）`;
      ocrStatus.classList.add("bad");
      return;
    }
    if (!data.ok) { ocrStatus.textContent = data.message || t("ocrFailed"); ocrStatus.classList.add("bad"); return; }
    problemText.value = data.text || "";
    currentGeometryDescription = data.geometry_description || "";
    currentVisionFigure = data.figure || null;
    let status = data.message || t("ocrDone");
    if (data.vision_ok && currentVisionFigure) {
      status += " · " + t("visionOk");
      placeWorkbenchForScreen("search");
      bgMode = "figure"; // 搜索页默认显示示意图，而不是原图
      showWorkbench(null, currentVisionFigure);
    } else if (!data.vision_ok) {
      ocrStatus.classList.add("bad");
      // 看图失败时仍可在画板看原图
      if (currentImageBase64) {
        placeWorkbenchForScreen("search");
        bgMode = "photo";
        showWorkbench(null, null);
      }
    }
    ocrStatus.textContent = status;
    playSfx("ok");
  } catch { ocrStatus.textContent = t("netError"); ocrStatus.classList.add("bad"); }
}

function sanitizeDisplayText(text, limit) {
  let s = String(text || "").trim();
  if (!s) return "";
  // 后端偶发把整段 JSON 原样返回时，尽量抠出 message/hint
  if (s.startsWith("{") && (s.includes('"message"') || s.includes('"hint"'))) {
    try {
      const obj = JSON.parse(s);
      s = String(obj.hint || obj.message || obj.feedback || "").trim() || s;
    } catch {
      const m = s.match(/"(?:message|hint)"\s*:\s*"((?:[^"\\]|\\.)*)"/);
      if (m) {
        s = m[1].replace(/\\n/g, "\n").replace(/\\"/g, '"').replace(/\\\\/g, "\\");
      }
    }
  }
  const cot = s.search(
    /(?:^|\n)\s*(?:Wait[,.\s]|Actually[,.\s]|Let me think|不过等等|让我想想|不对[，,])/i
  );
  if (cot >= 12) s = s.slice(0, cot).trim();
  const max = limit || 800;
  if (s.length > max) s = s.slice(0, max).trim() + "…";
  return s;
}

function addBubble(role, text) {
  const clean = sanitizeDisplayText(text, role === "hint" ? 400 : 600);
  if (!clean) return;
  const div = document.createElement("div");
  div.className = "bubble " + role;
  div.textContent = clean;
  chatLog.appendChild(div);
  if (role === "hint") playSfx("hint");
  else if (role === "ai") playSfx("pop");
  requestAnimationFrame(() => { chatLog.scrollTop = chatLog.scrollHeight; });
}

function addFigureBubble(svg, caption, figureData) {
  if (svg) {
    const wrap = document.createElement("div");
    wrap.className = "bubble figure";
    if (caption) {
      const cap = document.createElement("p");
      cap.className = "figure-caption";
      cap.textContent = caption;
      wrap.appendChild(cap);
    }
    const box = document.createElement("div");
    box.className = "figure-svg";
    box.innerHTML = svg;
    wrap.appendChild(box);
    chatLog.appendChild(wrap);
    requestAnimationFrame(() => { chatLog.scrollTop = chatLog.scrollHeight; });
  }
  showWorkbench(svg, figureData);
}

function prefersReducedMotion() {
  return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}

function replayAnimClass(el, cls, clearMs) {
  if (!el) return;
  el.classList.remove(cls);
  if (prefersReducedMotion()) return;
  void el.offsetWidth;
  el.classList.add(cls);
  if (clearMs) {
    clearTimeout(el._animClear);
    el._animClear = setTimeout(() => el.classList.remove(cls), clearMs);
  }
}

function playHomeEnter() {
  const home = $("screen-home");
  if (!home) return;
  home.classList.remove("home-enter");
  void home.offsetWidth;
  home.classList.add("home-enter");
}

function playScreenEnter(el) {
  replayAnimClass(el, "screen-enter", 450);
}

function playBoardAppear() {
  ["boardGuide", "boardSearch"].forEach((id) => {
    const el = $(id);
    if (!el) return;
    const host = el.closest(".screen") || el;
    if (host.hidden) return;
    replayAnimClass(el, "board-appear", 550);
  });
}

function pulseHintBtn() {
  replayAnimClass($("btnHint"), "hint-pulse", 600);
}

function popFeedback(tag) {
  replayAnimClass($("feedback"), "pop", 400);
  if (tag === "ok") playSfx("ok");
  else if (tag === "bad") playSfx("bad");
}

function playDoneEnter() {
  // 保留 done-enter，避免庆祝对勾在动画结束后又被藏掉
  replayAnimClass(donePanel, "done-enter");
  playSfx("done");
}

function cloneFigure(fig) {
  return fig ? JSON.parse(JSON.stringify(fig)) : null;
}

function isSolidFigure(fig) {
  return !!(fig && (fig.type === "solid" || fig.solid));
}

function setWorkbenchHint(solid) {
  const hint = document.querySelector("#workbench [data-i18n='workbenchHint']");
  if (!hint) return;
  hint.textContent = solid ? t("workbenchHintSolid") : t("workbenchHint");
}

const MOVE_ICON_SVG =
  '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 3.2v17.2l5-4.5 3.6 7.1 2.6-1.3-3.6-7.1H19.5Z"/></svg>';

function setToolTip(btn, tip) {
  if (!btn) return;
  btn.title = tip;
  btn.setAttribute("aria-label", tip);
  // 绝不改 textContent，否则会冲掉 SVG 图标
  if (btn.id === "toolMove" && !btn.querySelector("svg")) {
    btn.innerHTML = MOVE_ICON_SVG;
  }
}

function syncSolidTools(solid) {
  const solidCanvas = $("solidCanvas");
  const fig = $("figureLayer");
  const moveBtn = $("toolMove");
  const resetBtn = $("toolResetGeo");
  const bgFig = $("toolBgFigure");
  if (solid) {
    if (resetBtn) resetBtn.hidden = true;
    if (bgFig) bgFig.hidden = true;
    if (moveBtn) {
      moveBtn.hidden = false;
      setToolTip(moveBtn, t("toolRotate"));
    }
    ["toolBgPhoto", "toolBgPhotoOnly"].forEach((id) => {
      const el = $(id);
      if (el) el.hidden = true;
    });
  } else {
    if (bgFig) bgFig.hidden = false;
    if (moveBtn) {
      moveBtn.hidden = false;
      setToolTip(moveBtn, t("toolMove"));
    }
    if (resetBtn) resetBtn.hidden = !(geoBaseline && drawMode === "move");
    syncPhotoToolsVisibility();
  }
  if (solidCanvas) solidCanvas.hidden = !solid;
  if (fig) {
    fig.style.visibility = solid ? "hidden" : "";
    if (solid) fig.innerHTML = "";
  }
  setWorkbenchHint(solid);
}

function mountSolidWorkbench(figureData) {
  const solidCanvas = $("solidCanvas");
  if (!solidCanvas || !window.Solid3D) return;
  syncSolidTools(true);
  if (solidCanvas.dataset.mounted === "1") {
    Solid3D.setFigure(figureData);
  } else {
    Solid3D.mount(solidCanvas, figureData);
    solidCanvas.dataset.mounted = "1";
  }
  Solid3D.resize();
  // 默认旋转视角；形状仍锁定，不会变成可拖边
  setInteractionMode("move");
}

function unmountSolidWorkbench() {
  const solidCanvas = $("solidCanvas");
  if (window.Solid3D) {
    try { Solid3D.destroy(); } catch (_) {}
  }
  if (solidCanvas) {
    solidCanvas.hidden = true;
    delete solidCanvas.dataset.mounted;
  }
  syncSolidTools(false);
}

function showWorkbench(svg, figureData) {
  if (svg) latestFigureSvg = svg;
  // 立体题锁定：后续若 AI 返回平面三角形，也不替换已有立体图（避免又能拖边）
  if (figureData) {
    if (isSolidFigure(latestFigureData) && !isSolidFigure(figureData)) {
      figureData = null;
    } else {
      latestFigureData = figureData;
      geoBaseline = cloneFigure(figureData);
    }
  }
  const wb = $("workbench");
  if (!wb) return;
  const wasHidden = wb.hidden;
  wb.hidden = false;
  syncWorkbenchEmpty();
  if (wasHidden) playBoardAppear();

  if (isSolidFigure(latestFigureData)) {
    bgMode = "figure";
    syncPhotoToolsVisibility();
    mountSolidWorkbench(latestFigureData);
    resizeCanvas();
    syncBgMode();
    syncWorkbenchEmpty();
    return;
  }

  unmountSolidWorkbench();

  // 搜索页优先示意图；练习页有原图时默认叠加描摹
  if (currentImageBase64 && bgMode !== "photo" && bgMode !== "figure") {
    bgMode = currentScreen === "search" ? "figure" : "overlay";
  }
  syncPhotoToolsVisibility();

  if (latestFigureData || latestFigureSvg) {
    initGeoState(latestFigureData);
    renderInteractiveGeo();
  }
  setInteractionMode(drawMode);
  resizeCanvas();
  syncBgMode();
  syncWorkbenchEmpty();
  if (currentImageBase64) {
    const photo = $("photoLayer");
    photo.onload = () => {
      if (latestFigureData && bgMode !== "photo" && !isSolidFigure(latestFigureData)) {
        initGeoState(latestFigureData);
        renderInteractiveGeo();
      }
      syncWorkbenchEmpty();
    };
    const want = `data:${currentImageMime || "image/jpeg"};base64,${currentImageBase64}`;
    if (photo.getAttribute("src") !== want) photo.src = want;
  }
}

function resetGeoToBaseline() {
  if (!geoBaseline) {
    alert(t("noBaseline"));
    return;
  }
  latestFigureData = cloneFigure(geoBaseline);
  currentVisionFigure = latestFigureData;
  initGeoState(latestFigureData);
  if (bgMode === "photo") bgMode = "overlay";
  syncBgMode();
  renderInteractiveGeo();
  const status = $("startStatus");
  if (status) status.textContent = t("resetGeoDone");
}

/** 照片在画板中 object-fit:contain 后的内容区（SVG viewBox 坐标） */
function getPhotoContentBox() {
  const photo = $("photoLayer");
  const nw = (photo && photo.naturalWidth) || 0;
  const nh = (photo && photo.naturalHeight) || 0;
  if (nw < 1 || nh < 1) {
    return { ox: 0, oy: 0, w: GEO_W, h: GEO_H, ready: false };
  }
  const imgAspect = nw / nh;
  const stageAspect = GEO_W / GEO_H;
  let w, h, ox, oy;
  if (imgAspect > stageAspect) {
    w = GEO_W;
    h = GEO_W / imgAspect;
    ox = 0;
    oy = (GEO_H - h) / 2;
  } else {
    h = GEO_H;
    w = GEO_H * imgAspect;
    ox = (GEO_W - w) / 2;
    oy = 0;
  }
  return { ox, oy, w, h, ready: true };
}

function mapNormToSvg(nx, ny, box) {
  return { x: box.ox + nx * box.w, y: box.oy + ny * box.h };
}

function mapSvgToNorm(x, y, box) {
  if (!box.w || !box.h) return { x: 0.5, y: 0.5 };
  return {
    x: Math.min(1, Math.max(0, (x - box.ox) / box.w)),
    y: Math.min(1, Math.max(0, (y - box.oy) / box.h)),
  };
}

function initGeoState(figure) {
  const f = figure || {};
  const verts = (f.vertices && f.vertices.length >= 3) ? f.vertices.slice(0, 3) : ["A", "B", "C"];
  const [a, b, c] = verts;
  const src = f.points || {};
  const normPts = {};
  if (src[a] && src[b] && src[c]) {
    for (const n of Object.keys(src)) {
      if (src[n]) normPts[n] = { x: +src[n].x, y: +src[n].y };
    }
  } else {
    normPts[a] = { x: 0.15, y: 0.78 };
    normPts[b] = { x: 0.50, y: 0.18 };
    normPts[c] = { x: 0.85, y: 0.78 };
  }

  const angleLabels = f.angle_labels || {};
  geoState = {
    verts,
    normPts,
    pts: {},
    angle_labels: angleLabels,
    lockAngles: hasFixedAngleLabels(angleLabels),
    highlight: f.highlight || null,
    extra_points: (f.extra_points || []).map((ep) => ({ ...ep })),
    segments: f.segments || [],
    caption: f.caption || "",
  };
  remapGeoPoints();
}

/** 按当前模式把整图归一化坐标映射到 SVG；叠加时与原图对齐 */
function remapGeoPoints() {
  if (!geoState || !geoState.normPts) return;
  const pts = {};
  const overlay = bgMode === "overlay" && currentImageBase64;
  if (overlay) {
    const box = getPhotoContentBox();
    geoState.view = { mode: "overlay", box };
    for (const n of Object.keys(geoState.normPts)) {
      const p = geoState.normPts[n];
      pts[n] = mapNormToSvg(p.x, p.y, box);
    }
  } else {
    // 纯示意图：把点集居中放大，方便拖动查看
    const pad = 28;
    const names = Object.keys(geoState.normPts);
    let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
    for (const n of names) {
      const p = geoState.normPts[n];
      minX = Math.min(minX, p.x); maxX = Math.max(maxX, p.x);
      minY = Math.min(minY, p.y); maxY = Math.max(maxY, p.y);
    }
    const spanX = Math.max(maxX - minX, 0.08);
    const spanY = Math.max(maxY - minY, 0.08);
    const usableW = GEO_W - 2 * pad;
    const usableH = GEO_H - 2 * pad;
    const scale = Math.min(usableW / spanX, usableH / spanY);
    const ox = pad + (usableW - spanX * scale) / 2;
    const oy = pad + (usableH - spanY * scale) / 2;
    geoState.view = { mode: "fit", minX, minY, scale, ox, oy };
    for (const n of names) {
      const p = geoState.normPts[n];
      pts[n] = { x: ox + (p.x - minX) * scale, y: oy + (p.y - minY) * scale };
    }
  }
  geoState.pts = pts;
  recomputeExtraPoints();
}

function syncNormFromPts() {
  if (!geoState || !geoState.pts) return;
  const view = geoState.view;
  for (const n of Object.keys(geoState.pts)) {
    const ep = findExtraPoint(n);
    if (ep && ep.on) continue; // 边上点由 ratio 决定，不写死坐标
    const p = geoState.pts[n];
    if (view && view.mode === "overlay" && view.box) {
      geoState.normPts[n] = mapSvgToNorm(p.x, p.y, view.box);
    } else if (view && view.mode === "fit" && view.scale) {
      geoState.normPts[n] = {
        x: view.minX + (p.x - view.ox) / view.scale,
        y: view.minY + (p.y - view.oy) / view.scale,
      };
    }
  }
  // 边上辅助点：用当前 ratio 反推像素后也可不写 norm；保留主点即可
  if (latestFigureData) {
    latestFigureData.points = { ...geoState.normPts };
    currentVisionFigure = latestFigureData;
  }
}

function recomputeExtraPoints() {
  if (!geoState) return;
  for (const ep of geoState.extra_points) {
    const on = (ep.on || "").toUpperCase();
    if (on.length < 2) continue;
    const p1 = geoState.pts[on[0]];
    const p2 = geoState.pts[on[1]];
    if (!p1 || !p2) continue;
    const t = typeof ep.ratio === "number" ? ep.ratio : 0.5;
    geoState.pts[ep.name] = {
      x: p1.x + (p2.x - p1.x) * t,
      y: p1.y + (p2.y - p1.y) * t,
    };
  }
}

function findExtraPoint(name) {
  if (!geoState) return null;
  return geoState.extra_points.find((ep) => ep.name === name) || null;
}

function isMainVertex(name) {
  return Boolean(geoState && geoState.verts.includes(name));
}

/** 把点投影到线段 p1-p2，返回 0~1 的 ratio */
function projectRatio(pt, p1, p2) {
  const dx = p2.x - p1.x;
  const dy = p2.y - p1.y;
  const len2 = dx * dx + dy * dy;
  if (len2 < 1e-6) return 0.5;
  let t = ((pt.x - p1.x) * dx + (pt.y - p1.y) * dy) / len2;
  return Math.max(0.08, Math.min(0.92, t));
}

function parseEdgeEnds(attr) {
  if (!attr) return null;
  if (attr.includes(",")) {
    const parts = attr.split(",");
    if (parts.length >= 2) return [parts[0], parts[1]];
  }
  // 兼容旧格式 "AB"
  if (attr.length >= 2) return [attr[0], attr[1]];
  return null;
}

function clampPt(p) {
  return {
    x: Math.max(16, Math.min(GEO_W - 16, p.x)),
    y: Math.max(16, Math.min(GEO_H - 16, p.y)),
  };
}

function anglePair(v, prev, next) {
  let a1 = Math.atan2(prev.y - v.y, prev.x - v.x);
  let a2 = Math.atan2(next.y - v.y, next.x - v.x);
  let diff = (a2 - a1) % (Math.PI * 2);
  if (diff < 0) diff += Math.PI * 2;
  if (diff > Math.PI) {
    const tmp = a1; a1 = a2; a2 = tmp;
    diff = (a2 - a1) % (Math.PI * 2);
    if (diff < 0) diff += Math.PI * 2;
  }
  return { a1, a2, diff };
}

/** 题干给出的数值角（非 ?）→ 拖动时锁定形状，避免角度被改掉 */
function hasFixedAngleLabels(labels) {
  return Object.values(labels || {}).some((v) => {
    const s = String(v || "");
    return s && !s.includes("?") && /\d/.test(s);
  });
}

function triangleCentroid(pts, verts) {
  const [a, b, c] = verts;
  return {
    x: (pts[a].x + pts[b].x + pts[c].x) / 3,
    y: (pts[a].y + pts[b].y + pts[c].y) / 3,
  };
}

/** 以中心做相似变换，把 from 点映射到 to，整体角度不变 */
function applySimilarMap(origPts, center, from, to) {
  const v0x = from.x - center.x;
  const v0y = from.y - center.y;
  const v1x = to.x - center.x;
  const v1y = to.y - center.y;
  const len0 = Math.hypot(v0x, v0y);
  if (len0 < 1e-6) return null;
  const len1 = Math.hypot(v1x, v1y);
  const scale = Math.max(0.25, Math.min(4, len1 / len0));
  const ang0 = Math.atan2(v0y, v0x);
  const ang1 = Math.atan2(v1y, v1x);
  const da = ang1 - ang0;
  const cos = Math.cos(da);
  const sin = Math.sin(da);
  const next = {};
  for (const name of Object.keys(origPts)) {
    const p = origPts[name];
    if (!p) continue;
    const rx = p.x - center.x;
    const ry = p.y - center.y;
    next[name] = clampPt({
      x: center.x + (rx * cos - ry * sin) * scale,
      y: center.y + (rx * sin + ry * cos) * scale,
    });
  }
  return next;
}

function translateAllPoints(origPts, dx, dy) {
  const next = {};
  for (const name of Object.keys(origPts)) {
    const p = origPts[name];
    if (!p) continue;
    next[name] = clampPt({ x: p.x + dx, y: p.y + dy });
  }
  return next;
}

function renderInteractiveGeo() {
  if (!geoState) return;
  const [a, b, c] = geoState.verts;
  const pts = geoState.pts;
  const overlay = bgMode === "overlay";
  const lineColor = overlay ? "#1ee0a0" : "#1c2a24";
  const dashColor = overlay ? "#5cffc0" : "#0f6b4c";
  const arcColor = overlay ? "#ffb36b" : "#5a6b62";
  const hiColor = overlay ? "#ff8a3d" : "#c45c26";
  const layers = [];
  layers.push(`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${GEO_W} ${GEO_H}" width="100%" height="100%">`);
  if (!overlay) {
    layers.push('<rect width="100%" height="100%" fill="#fffdf8"/>');
    layers.push(
      `<polygon id="geoPoly" points="${pts[a].x},${pts[a].y} ${pts[b].x},${pts[b].y} ${pts[c].x},${pts[c].y}" ` +
      `fill="#eef7f2" stroke="none" pointer-events="none"/>`
    );
  } else {
    layers.push(
      `<polygon id="geoPoly" points="${pts[a].x},${pts[a].y} ${pts[b].x},${pts[b].y} ${pts[c].x},${pts[c].y}" ` +
      `fill="rgba(30,224,160,0.12)" stroke="none" pointer-events="none"/>`
    );
  }

  // 可拖动的边（透明宽线）
  const edges = [[a, b], [b, c], [c, a]];
  for (const [u, v] of edges) {
    layers.push(
      `<line class="geo-edge" data-edge="${u},${v}" ` +
      `x1="${pts[u].x}" y1="${pts[u].y}" x2="${pts[v].x}" y2="${pts[v].y}" />`
    );
    layers.push(
      `<line data-edge-vis="${u}${v}" x1="${pts[u].x}" y1="${pts[u].y}" x2="${pts[v].x}" y2="${pts[v].y}" ` +
      `stroke="${lineColor}" stroke-width="${overlay ? 3 : 2.5}" pointer-events="none"/>`
    );
  }

  // 虚线可见层（不可点）
  for (const s of geoState.segments || []) {
    if (pts[s[0]] && pts[s[1]]) {
      layers.push(
        `<line data-seg-vis="1" x1="${pts[s[0]].x}" y1="${pts[s[0]].y}" x2="${pts[s[1]].x}" y2="${pts[s[1]].y}" ` +
        `stroke="${dashColor}" stroke-width="${overlay ? 2.5 : 2}" stroke-dasharray="6 4" pointer-events="none"/>`
      );
    }
  }

  // 角弧 + 角度数字（若有）
  const order = [a, b, c];
  const cx = (pts[a].x + pts[b].x + pts[c].x) / 3;
  const cy = (pts[a].y + pts[b].y + pts[c].y) / 3;
  for (let i = 0; i < 3; i++) {
    const name = order[i];
    const prev = pts[order[(i + 2) % 3]];
    const next = pts[order[(i + 1) % 3]];
    const v = pts[name];
    const { a1, a2, diff } = anglePair(v, prev, next);
    const r = 28;
    const x1 = v.x + r * Math.cos(a1);
    const y1 = v.y + r * Math.sin(a1);
    const x2 = v.x + r * Math.cos(a2);
    const y2 = v.y + r * Math.sin(a2);
    const color = geoState.highlight === name ? hiColor : arcColor;
    const sw = geoState.highlight === name ? 2.5 : 1.5;
    layers.push(
      `<path d="M ${x1.toFixed(1)} ${y1.toFixed(1)} A ${r} ${r} 0 0 1 ${x2.toFixed(1)} ${y2.toFixed(1)}" ` +
      `fill="none" stroke="${color}" stroke-width="${sw}" pointer-events="none"/>`
    );
    const deg = (geoState.angle_labels || {})[name];
    if (deg) {
      const mid = a1 + diff / 2;
      const lx = v.x + (r + 14) * Math.cos(mid);
      const ly = v.y + (r + 14) * Math.sin(mid);
      layers.push(
        `<text class="geo-label" x="${lx.toFixed(1)}" y="${ly.toFixed(1)}" text-anchor="middle" ` +
        `dominant-baseline="middle" font-size="13" font-weight="700" fill="${color}" ` +
        `pointer-events="none">${deg}</text>`
      );
    }
  }

  // 顶点字母 A/B/C 及辅助点字母（放在外侧）
  const labelColor = overlay ? "#ffffff" : "#1c2a24";
  const labelStroke = overlay ? "rgba(0,0,0,0.55)" : "none";
  for (const name of Object.keys(pts)) {
    const p = pts[name];
    if (!p) continue;
    let dx = p.x - cx;
    let dy = p.y - cy;
    const len = Math.hypot(dx, dy) || 1;
    const ox = (dx / len) * 18;
    const oy = (dy / len) * 18;
    layers.push(
      `<text class="geo-label geo-vertex-label" x="${(p.x + ox).toFixed(1)}" y="${(p.y + oy).toFixed(1)}" ` +
      `text-anchor="middle" dominant-baseline="middle" font-size="16" font-weight="700" ` +
      `fill="${labelColor}" stroke="${labelStroke}" stroke-width="3" paint-order="stroke" ` +
      `pointer-events="none">${name}</text>`
    );
  }

  // 虚线宽命中层放上面，保证能拖到
  for (const s of geoState.segments || []) {
    if (pts[s[0]] && pts[s[1]]) {
      layers.push(
        `<line class="geo-edge geo-seg" data-edge="${s[0]},${s[1]}" data-seg="1" ` +
        `x1="${pts[s[0]].x}" y1="${pts[s[0]].y}" x2="${pts[s[1]].x}" y2="${pts[s[1]].y}" />`
      );
    }
  }

  // 主顶点可拖
  for (const name of [a, b, c]) {
    const p = pts[name];
    if (!p) continue;
    layers.push(
      `<circle class="geo-vertex" data-vertex="${name}" cx="${p.x}" cy="${p.y}" r="9"/>`
    );
  }

  // 虚线端点 / 辅助点可拖（在最上层）
  const drawn = new Set([a, b, c]);
  for (const ep of geoState.extra_points || []) {
    const p = pts[ep.name];
    if (!p || drawn.has(ep.name)) continue;
    drawn.add(ep.name);
    layers.push(
      `<circle class="geo-vertex geo-extra" data-vertex="${ep.name}" data-extra="1" ` +
      `cx="${p.x}" cy="${p.y}" r="9"/>`
    );
  }
  // 写在 points/segments 里但不在 extra_points 的端点也给手柄
  for (const s of geoState.segments || []) {
    for (const name of s) {
      const p = pts[name];
      if (!p || drawn.has(name)) continue;
      drawn.add(name);
      layers.push(
        `<circle class="geo-vertex geo-extra" data-vertex="${name}" ` +
        `cx="${p.x}" cy="${p.y}" r="9"/>`
      );
    }
  }

  layers.push("</svg>");
  $("figureLayer").innerHTML = layers.join("");
  setupGeoDrag();
}

function svgPointFromEvent(e) {
  const layer = $("figureLayer");
  const svg = layer.querySelector("svg");
  if (!svg) return null;
  const rect = svg.getBoundingClientRect();
  const src = e.touches ? e.touches[0] : e;
  const x = ((src.clientX - rect.left) / rect.width) * GEO_W;
  const y = ((src.clientY - rect.top) / rect.height) * GEO_H;
  return { x, y };
}

function setupGeoDrag() {
  const layer = $("figureLayer");
  if (layer.dataset.dragReady) return;
  layer.dataset.dragReady = "1";

  const onDown = (e) => {
    if (drawMode !== "move") return;
    const t = e.target;
    if (!t) return;
    const vertex = t.getAttribute && t.getAttribute("data-vertex");
    const edgeAttr = t.getAttribute && t.getAttribute("data-edge");
    const p = svgPointFromEvent(e);
    if (!p || !geoState) return;
    if (vertex) {
      geoDrag = {
        type: "vertex",
        name: vertex,
        isExtra: Boolean(t.getAttribute("data-extra")),
        start: p,
        orig: JSON.parse(JSON.stringify(geoState.pts)),
        extraSnap: JSON.parse(JSON.stringify(geoState.extra_points)),
      };
    } else if (edgeAttr) {
      const ends = parseEdgeEnds(edgeAttr);
      if (!ends) return;
      geoDrag = {
        type: "edge",
        ends,
        start: p,
        orig: JSON.parse(JSON.stringify(geoState.pts)),
        extraSnap: JSON.parse(JSON.stringify(geoState.extra_points)),
      };
    } else {
      return;
    }
    layer.classList.add("dragging");
    e.preventDefault();
  };

  const onMove = (e) => {
    if (!geoDrag || !geoState) return;
    const p = svgPointFromEvent(e);
    if (!p) return;
    const dx = p.x - geoDrag.start.x;
    const dy = p.y - geoDrag.start.y;

    // 题干有固定角度时：只做整体平移/旋转/缩放，不改角度
    if (geoState.lockAngles && !(geoDrag.type === "vertex" && geoDrag.isExtra)) {
      if (geoDrag.type === "vertex" && geoDrag.orig[geoDrag.name]) {
        const center = triangleCentroid(geoDrag.orig, geoState.verts);
        const target = clampPt({
          x: geoDrag.orig[geoDrag.name].x + dx,
          y: geoDrag.orig[geoDrag.name].y + dy,
        });
        const mapped = applySimilarMap(
          geoDrag.orig,
          center,
          geoDrag.orig[geoDrag.name],
          target
        );
        if (mapped) geoState.pts = mapped;
      } else if (geoDrag.type === "edge") {
        geoState.pts = translateAllPoints(geoDrag.orig, dx, dy);
      }
      // 辅助点 ratio 不变，按新顶点重算位置
      if (geoDrag.extraSnap) {
        geoState.extra_points = geoDrag.extraSnap.map((ep) => ({ ...ep }));
      }
      recomputeExtraPoints();
      syncNormFromPts();
      renderInteractiveGeo();
      layer.classList.add("dragging");
      e.preventDefault();
      return;
    }

    if (geoDrag.type === "vertex") {
      const ep = findExtraPoint(geoDrag.name);
      if (ep && geoDrag.isExtra) {
        // 辅助点：沿所在边滑动，更新 ratio
        const on = (ep.on || "").toUpperCase();
        const p1 = geoState.pts[on[0]];
        const p2 = geoState.pts[on[1]];
        if (p1 && p2) {
          ep.ratio = projectRatio(p, p1, p2);
        }
      } else {
        geoState.pts[geoDrag.name] = clampPt({
          x: geoDrag.orig[geoDrag.name].x + dx,
          y: geoDrag.orig[geoDrag.name].y + dy,
        });
      }
    } else if (geoDrag.type === "edge") {
      const [u, v] = geoDrag.ends;
      // 先平移所有「自由端点」（主顶点或未约束的辅助点）
      for (const name of [u, v]) {
        if (!geoDrag.orig[name]) continue;
        const ep = findExtraPoint(name);
        if (ep && ep.on) continue; // 边上约束点稍后按 ratio 更新
        geoState.pts[name] = clampPt({
          x: geoDrag.orig[name].x + dx,
          y: geoDrag.orig[name].y + dy,
        });
      }
      // 边上的辅助点：投影回所在边
      for (const name of [u, v]) {
        const ep = findExtraPoint(name);
        if (!ep || !ep.on || !geoDrag.orig[name]) continue;
        const on = String(ep.on || "").toUpperCase();
        const p1 = geoState.pts[on[0]];
        const p2 = geoState.pts[on[1]];
        if (!p1 || !p2) continue;
        const target = {
          x: geoDrag.orig[name].x + dx,
          y: geoDrag.orig[name].y + dy,
        };
        ep.ratio = projectRatio(target, p1, p2);
      }
    }
    recomputeExtraPoints();
    syncNormFromPts();
    renderInteractiveGeo();
    // keep drag state after re-render
    layer.classList.add("dragging");
    e.preventDefault();
  };

  const onUp = () => {
    if (geoState) syncNormFromPts();
    geoDrag = null;
    $("figureLayer").classList.remove("dragging");
  };

  layer.addEventListener("mousedown", onDown);
  window.addEventListener("mousemove", onMove);
  window.addEventListener("mouseup", onUp);
  layer.addEventListener("touchstart", onDown, { passive: false });
  window.addEventListener("touchmove", onMove, { passive: false });
  window.addEventListener("touchend", onUp);
}

function setInteractionMode(mode) {
  drawMode = mode;
  const canvas = $("drawCanvas");
  const moveBtn = $("toolMove");
  const penBtn = $("toolPen");
  const eraserBtn = $("toolEraser");
  const resetBtn = $("toolResetGeo");
  const solid = isSolidFigure(latestFigureData);
  if (moveBtn) {
    moveBtn.classList.toggle("active", mode === "move");
    setToolTip(moveBtn, solid ? t("toolRotate") : t("toolMove"));
  }
  if (penBtn) penBtn.classList.toggle("active", mode === "pen");
  if (eraserBtn) eraserBtn.classList.toggle("active", mode === "eraser");
  if (resetBtn) resetBtn.hidden = solid || mode !== "move" || !geoBaseline;
  if (canvas) {
    // 立体旋转 / 平面拖动 / 只看原图：画笔层穿透
    const pass = mode === "move" || bgMode === "photo";
    canvas.classList.toggle("passthrough", pass);
    canvas.style.cursor = pass ? "default" : "crosshair";
  }
  if (solid && window.Solid3D && typeof Solid3D.setRotateEnabled === "function") {
    Solid3D.setRotateEnabled(mode === "move");
  }
}

function clearDrawings() {
  const canvas = $("drawCanvas");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");
  ctx.save();
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.restore();
}

function syncBgMode() {
  syncPhotoToolsVisibility();
  const fig = $("figureLayer");
  const photo = $("photoLayer");
  const solidCanvas = $("solidCanvas");
  const solid = isSolidFigure(latestFigureData);
  const hasPhoto = Boolean(currentImageBase64);
  const btnFig = $("toolBgFigure");
  const btnOverlay = $("toolBgPhoto");
  const btnPhoto = $("toolBgPhotoOnly");
  if (btnFig) btnFig.classList.remove("active");
  if (btnOverlay) btnOverlay.classList.remove("active");
  if (btnPhoto) btnPhoto.classList.remove("active");

  if (solid) {
    bgMode = "figure";
    if (photo) photo.hidden = true;
    if (fig) {
      fig.style.visibility = "hidden";
      fig.classList.remove("overlay");
    }
    if (solidCanvas) solidCanvas.hidden = false;
    setInteractionMode(drawMode);
    if (window.Solid3D) Solid3D.resize();
    return;
  }

  if ((bgMode === "overlay" || bgMode === "photo") && !hasPhoto) {
    bgMode = "figure";
  }

  if (hasPhoto && (bgMode === "overlay" || bgMode === "photo")) {
    photo.hidden = false;
    if (currentImageBase64) {
      const want = `data:${currentImageMime || "image/jpeg"};base64,${currentImageBase64}`;
      if (photo.getAttribute("src") !== want) photo.src = want;
    }
  }

  if (bgMode === "photo" && hasPhoto) {
    fig.style.visibility = "hidden";
    fig.classList.remove("overlay");
    if (btnPhoto) btnPhoto.classList.add("active");
  } else if (bgMode === "overlay" && hasPhoto) {
    fig.style.visibility = "visible";
    fig.classList.add("overlay");
    if (btnOverlay) btnOverlay.classList.add("active");
  } else {
    bgMode = "figure";
    fig.style.visibility = "visible";
    fig.classList.remove("overlay");
    photo.hidden = true;
    if (btnFig) btnFig.classList.add("active");
  }

  // 同步画布穿透（只看原图时也不挡）
  setInteractionMode(drawMode);

  if (geoState && bgMode !== "photo") {
    remapGeoPoints();
    renderInteractiveGeo();
  }
}

function resizeCanvas() {
  const stage = $("workbenchStage");
  const canvas = $("drawCanvas");
  if (!stage || !canvas) return;
  const rect = stage.getBoundingClientRect();
  const dpr = window.devicePixelRatio || 1;
  canvas.width = Math.max(1, Math.floor(rect.width * dpr));
  canvas.height = Math.max(1, Math.floor(rect.height * dpr));
  canvas.style.width = rect.width + "px";
  canvas.style.height = rect.height + "px";
  const ctx = canvas.getContext("2d");
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  ctx.lineCap = "round";
  ctx.lineJoin = "round";
  if (isSolidFigure(latestFigureData) && window.Solid3D) Solid3D.resize();
}

function canvasPos(e) {
  const canvas = $("drawCanvas");
  const rect = canvas.getBoundingClientRect();
  const src = e.touches ? e.touches[0] : e;
  return { x: src.clientX - rect.left, y: src.clientY - rect.top };
}

function setupDrawing() {
  const canvas = $("drawCanvas");
  if (!canvas || canvas.dataset.ready) return;
  canvas.dataset.ready = "1";
  const ctx = () => canvas.getContext("2d");

  const start = (e) => {
    if (drawMode === "move") return;
    drawing = true;
    const p = canvasPos(e);
    const c = ctx();
    c.beginPath();
    c.moveTo(p.x, p.y);
    e.preventDefault();
  };
  const move = (e) => {
    if (!drawing) return;
    const p = canvasPos(e);
    const c = ctx();
    if (drawMode === "eraser") {
      c.globalCompositeOperation = "destination-out";
      c.strokeStyle = "rgba(0,0,0,1)";
      c.lineWidth = 18;
    } else {
      c.globalCompositeOperation = "source-over";
      c.strokeStyle = "#c45c26";
      c.lineWidth = 3;
    }
    c.lineTo(p.x, p.y);
    c.stroke();
    c.beginPath();
    c.moveTo(p.x, p.y);
    e.preventDefault();
  };
  const end = () => { drawing = false; };

  canvas.addEventListener("mousedown", start);
  canvas.addEventListener("mousemove", move);
  window.addEventListener("mouseup", end);
  canvas.addEventListener("touchstart", start, { passive: false });
  canvas.addEventListener("touchmove", move, { passive: false });
  canvas.addEventListener("touchend", end);
  window.addEventListener("resize", resizeCanvas);
}

function setBusy(on, label) {
  busy = on;
  $("btnSubmit").disabled = on;
  $("btnHint").disabled = on;
  $("btnStart").disabled = on;
  $("btnStart").textContent = on ? (label || t("thinking")) : t("confirm");
  if (on) playSfx("think");
}

async function fetchJson(url, options, timeoutMs) {
  if (abortCtrl) abortCtrl.abort();
  abortCtrl = new AbortController();
  const timer = setTimeout(() => abortCtrl.abort(), timeoutMs || 50000);
  try {
    const res = await fetch(url, Object.assign({}, options, { signal: abortCtrl.signal }));
    return await res.json();
  } finally { clearTimeout(timer); }
}

async function startAiGuide() {
  const text = problemText.value.trim();
  if (!text) return alert(t("enterProblem"));
  if (busy) return;
  setBusy(true, t("thinking"));
  startStatus.textContent = t("connecting");
  startStatus.classList.remove("bad");
  feedback.textContent = "";
  try {
    const payload = { text: text, lang: currentLang };
    if (currentImageBase64) {
      payload.image_base64 = currentImageBase64;
      payload.image_mime = currentImageMime || "image/jpeg";
    }
    if (currentGeometryDescription) {
      payload.geometry_description = currentGeometryDescription;
    }
    if (currentVisionFigure) {
      payload.figure_data = currentVisionFigure;
    }
    const data = await fetchJson("/api/ai/start", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    }, 90000);
    if (!data.ok) {
      startStatus.textContent = data.message || t("startFailed");
      startStatus.classList.add("bad");
      playSfx("bad");
      return;
    }
    playSfx("ok");
    sessionId = data.session_id;
    hasDoneSolution = false;
    if (data.geometry_description) currentGeometryDescription = data.geometry_description;
    if (data.figure_data) currentVisionFigure = data.figure_data;
    chatLog.innerHTML = "";
    answerBox.value = "";
    resizeAnswerBox();
    showScreen("guide", { force: true });
    syncWorkbenchEmpty();
    addBubble("ai", data.message || t("aiStart"));
    if (data.hint) {
      addBubble("hint", t("hintPrefix") + data.hint);
      pulseHintBtn();
    }
    if (data.figure_svg || data.figure_data) {
      addFigureBubble(data.figure_svg, data.figure_caption || "", data.figure_data || null);
    } else if (currentVisionFigure) {
      showWorkbench(null, currentVisionFigure);
    } else if (currentImageBase64) {
      showWorkbench(null, null);
      bgMode = "overlay";
      syncBgMode();
      syncWorkbenchEmpty();
      resizeCanvas();
    }
    startStatus.textContent = data.vision_note
      ? t("started") + " · " + data.vision_note
      : t("started");
    feedback.textContent = data.feedback || t("defaultFeedback");
    feedback.className = "feedback ok";
    popFeedback("ok");
    if (data.completed) showDone(data.final_solution || data.message, data.review);
  } catch (err) {
    const aborted = err && err.name === "AbortError";
    startStatus.textContent = aborted ? t("timeoutStart") : t("reqFailed");
    startStatus.classList.add("bad");
    playSfx("bad");
  } finally { setBusy(false); }
}

async function sendReply(wantHint) {
  if (!sessionId) return alert(t("startGuideFirst"));
  if (busy) return;
  const answer = answerBox.value;
  if (!wantHint && !answer.trim()) return alert(t("writeSomething"));
  setBusy(true, wantHint ? t("thinking") : t("grading"));
  feedback.textContent = wantHint ? t("hintLoading") : t("gradingMsg");
  feedback.className = "feedback";
  if (!wantHint) {
    addBubble("student", answer.trim());
    playSfx("send");
  } else {
    addBubble("student", t("hintAsked"));
  }
  try {
    const data = await fetchJson("/api/ai/reply", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      // 提示请求仍带上草稿作上下文；后端会走专用提示路径
      body: JSON.stringify({ session_id: sessionId, answer: answer, want_hint: wantHint }),
    }, 90000);
    if (!data.ok) {
      feedback.textContent = data.message || t("submitFailed");
      feedback.className = "feedback bad";
      playSfx("bad");
      return;
    }

    if (wantHint) {
      const hintText = (data.hint || data.message || data.feedback || "").trim();
      if (hintText) addBubble("hint", t("hintPrefix") + hintText);
      if (data.message && data.message.trim() && data.message.trim() !== hintText) {
        addBubble("ai", data.message);
      }
      feedback.textContent = data.feedback || hintText || t("hintReady");
      feedback.className = "feedback ok";
      popFeedback("ok");
      pulseHintBtn();
    } else {
      if (data.feedback) {
        const tag = data.is_correct === true ? "ok" : data.is_correct === false ? "bad" : "";
        feedback.textContent = data.feedback;
        feedback.className = "feedback " + tag;
        if (tag) popFeedback(tag);
      }
      if (data.message) addBubble("ai", data.message);
      if (data.hint) {
        addBubble("hint", t("hintPrefix") + data.hint);
        pulseHintBtn();
      }
      answerBox.value = "";
      resizeAnswerBox();
    }

    if (data.figure_svg || data.figure_data) {
      addFigureBubble(data.figure_svg, data.figure_caption || "", data.figure_data || null);
    }
    if (data.completed && !wantHint) showDone(data.final_solution || data.message, data.review);
  } catch (err) {
    const aborted = err && err.name === "AbortError";
    feedback.textContent = aborted ? t("timeoutReply") : t("reqFailedRetry");
    feedback.className = "feedback bad";
    playSfx("bad");
  } finally { setBusy(false); }
}

function showDone(solution, review) {
  hasDoneSolution = true;
  showScreen("done", { force: true });
  finalWriteup.textContent = solution || "";
  // 完成页 = 反馈建议 + 完整解答（缺一不可）
  const fallback = review || {
    summary: currentLang === "en"
      ? "You finished the problem. Here is quick feedback."
      : "这道题你已经做完了。下面是针对过程的反馈与建议。",
    strengths: [currentLang === "en" ? "You completed the guided problem." : "能跟着引导把整道题做完。"],
    improvements: [currentLang === "en" ? "Try stating the key property before calculating." : "关键步骤可以先说出用到的性质/定理。"],
    suggestions: [currentLang === "en" ? "Practice a similar problem next." : "可以再练一道同类题巩固。"],
    source: "local",
  };
  showReview(fallback, fallback.source === "local" ? t("reviewLoading") : "");
  enrichReviewIfNeeded(fallback);
}

// ===== Workbench tools =====
$("toolMove").addEventListener("click", () => setInteractionMode("move"));
$("toolPen").addEventListener("click", () => setInteractionMode("pen"));
$("toolEraser").addEventListener("click", () => setInteractionMode("eraser"));
$("toolClear").addEventListener("click", clearDrawings);
if ($("toolResetGeo")) {
  $("toolResetGeo").addEventListener("click", resetGeoToBaseline);
}
$("toolBgFigure").addEventListener("click", () => {
  bgMode = "figure";
  syncBgMode();
});
$("toolBgPhoto").addEventListener("click", () => {
  if (!currentImageBase64) {
    alert(t("noPhoto"));
    return;
  }
  bgMode = "overlay";
  syncBgMode();
});
if ($("toolBgPhotoOnly")) {
  $("toolBgPhotoOnly").addEventListener("click", () => {
    if (!currentImageBase64) {
      alert(t("noPhoto"));
      return;
    }
    bgMode = "photo";
    syncBgMode();
  });
}

setupDrawing();

document.querySelectorAll("[data-screen]").forEach((el) => {
  el.addEventListener("click", (e) => {
    const name = el.dataset.screen;
    if (!name) return;
    if (el.tagName === "BUTTON" || el.classList.contains("home-entry") || el.classList.contains("side-logo")) {
      e.preventDefault();
      showScreen(name, { force: true });
    }
  });
});

document.querySelectorAll("[data-back]").forEach((el) => {
  el.addEventListener("click", (e) => {
    e.preventDefault();
    goBack();
  });
});

const langToggle = $("btnLangToggle");
if (langToggle) {
  langToggle.addEventListener("click", () => {
    currentLang = currentLang === "zh" ? "en" : "zh";
    applyLang();
  });
}

const btnSfxMute = $("btnSfxMute");
if (btnSfxMute) {
  syncMuteBtn();
  btnSfxMute.addEventListener("click", () => {
    setSfxMuted(!sfxMuted);
  });
}

let splashTimer = null;
let logoTipTimer = null;
let logoTipShownOnce = false;

function nudgeLogoTip() {
  const logo = $("btnReplaySplash");
  if (!logo || logoTipShownOnce) return;
  logoTipShownOnce = true;
  logo.classList.add("tip-on");
  if (logoTipTimer) clearTimeout(logoTipTimer);
  logoTipTimer = setTimeout(() => {
    logo.classList.remove("tip-on");
    logoTipTimer = null;
  }, 3200);
}

function endSplash() {
  const splash = $("splash");
  if (splash) splash.classList.add("is-done");
  if (splashTimer) {
    clearTimeout(splashTimer);
    splashTimer = null;
  }
  playSfx("splash"); // 加载完成短音
  playHomeEnter();
  // 开场结束后轻提示：侧栏 Logo 可重播
  setTimeout(nudgeLogoTip, 280);
}

function playSplash() {
  const splash = $("splash");
  if (!splash) return;
  const logo = $("btnReplaySplash");
  if (logo) {
    logo.classList.remove("tip-on");
    logo.classList.add("is-press");
    setTimeout(() => logo.classList.remove("is-press"), 140);
  }
  const home = $("screen-home");
  if (home) home.classList.remove("home-enter");
  const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  splash.classList.remove("is-done");
  splash.querySelectorAll(".splash-logo-wrap, .splash-logo, .splash-orbit span, .splash-brand h2, .splash-brand p, .splash-bar, .splash-bar i")
    .forEach((el) => {
      el.style.animation = "none";
      void el.offsetWidth;
      el.style.animation = "";
    });
  // 读条静音；结束时再播完成音。预加载保证结尾能即时出声
  preloadSfx();
  if (splashTimer) clearTimeout(splashTimer);
  splashTimer = setTimeout(endSplash, reduced ? 400 : 2800);
}

const splashSkip = $("splashSkip");
if (splashSkip) splashSkip.addEventListener("click", endSplash);

const btnReplaySplash = $("btnReplaySplash");
if (btnReplaySplash) {
  btnReplaySplash.addEventListener("click", () => {
    playSplash();
  });
}

applyLang();
showScreen("home", { force: true });
playSplash();
syncWorkbenchEmpty();
syncSearchBoardPreview();
syncPhotoToolsVisibility();
setInteractionMode("move");
