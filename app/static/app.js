let sessionId = null;
let cameraStream = null;
let busy = false;
let abortCtrl = null;
let currentLang = "zh";
let currentImageBase64 = null;
let currentImageMime = null;
let drawMode = "pen";
let drawing = false;
let labelsHidden = false;
let bgMode = "figure"; // figure | photo
let latestFigureSvg = null;

const I18N = {
  zh: {
    title: "AI 带你一步一步解题",
    subtitle: "拍照 / 粘贴图片 / 输入文字 → DeepSeek 在线逐步引导",
    step1: "1. 输入题目",
    dropTitle: "把题目图片拖到这里，或按 Ctrl+V 粘贴截图",
    dropHint: "也支持手机拍照、相册选图",
    upload: "上传图片",
    takePhoto: "拍照",
    openCamera: "打开摄像头",
    snap: "拍照识别",
    closeCamera: "关闭摄像头",
    problemLabel: "题目文字（可修改，也可包含你已有的做题过程）",
    problemPlaceholder: "拍照或粘贴图片后这里会自动填入文字；也可以直接打字/粘贴。\n如果你已经写了一部分解题过程，直接贴在这里，AI 会接着你的思路继续。",
    startGuide: "开始 AI 引导",
    step2: "2. AI 逐步引导",
    answerPlaceholder: "写下你的答案或思路…\n如果已经写了部分过程（含 ∵∴=° 等），直接贴在这里，AI 会接着往下引导",
    hint: "卡住了，提示一下",
    submit: "提交回答",
    fullSolution: "完整解答",
    copy: "复制全文",
    copied: "已复制",
    footer: "由 DeepSeek 提供解题引导 · 每次只推进一步，鼓励你自己思考",
    thinking: "AI 思考中…",
    grading: "AI 批改中…",
    connecting: "正在连接 DeepSeek，请稍候（通常几秒）…",
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
    ocrProcessing: "正在识别图片中的文字…",
    ocrFailed: "识别失败",
    ocrDone: "识别完成，请检查错字",
    imageAttached: "图片已附上，AI 将看图解题",
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
    workbenchHint: "可在图上涂画标注 · 可切换底图",
    toolPen: "画笔",
    toolEraser: "橡皮",
    toolClear: "清空标注",
    toolLabels: "隐藏/显示角度",
    toolBgFigure: "示意图",
    toolBgPhoto: "原题照片",
    noPhoto: "还没有原题照片，请先拍照或上传图片。",
  },
  en: {
    title: "AI Guides You Step by Step",
    subtitle: "Photo / Paste image / Type → DeepSeek online tutoring",
    step1: "1. Enter the Problem",
    dropTitle: "Drag an image here, or press Ctrl+V to paste a screenshot",
    dropHint: "Also supports phone camera and photo gallery",
    upload: "Upload",
    takePhoto: "Take Photo",
    openCamera: "Open Camera",
    snap: "Snap & Recognize",
    closeCamera: "Close Camera",
    problemLabel: "Problem text (editable; you can include your existing work)",
    problemPlaceholder: "After photo/paste, text appears here; you can also type directly.\nIf you've already written part of the solution, paste it here and AI will continue from your reasoning.",
    startGuide: "Start AI Guidance",
    step2: "2. AI Step-by-Step Guidance",
    answerPlaceholder: "Write your answer or approach…\nIf you have partial work (with ∵∴=° etc.), paste it here and AI will continue",
    hint: "I'm stuck, give me a hint",
    submit: "Submit Answer",
    fullSolution: "Full Solution",
    copy: "Copy All",
    copied: "Copied",
    footer: "Powered by DeepSeek · One step at a time, encouraging you to think",
    thinking: "AI thinking…",
    grading: "AI grading…",
    connecting: "Connecting to DeepSeek, please wait a few seconds…",
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
    ocrProcessing: "Recognizing text in the image…",
    ocrFailed: "Recognition failed",
    ocrDone: "Recognition done. Please check for errors.",
    imageAttached: "Image attached — AI will see the figure",
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
    workbenchHint: "Draw on the figure · switch background",
    toolPen: "Pen",
    toolEraser: "Eraser",
    toolClear: "Clear marks",
    toolLabels: "Toggle angle labels",
    toolBgFigure: "Diagram",
    toolBgPhoto: "Photo",
    noPhoto: "No problem photo yet. Please take or upload one first.",
  },
};

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
// ===== Language switcher =====
function applyLang() {
  document.querySelectorAll("[data-i18n]").forEach((el) => {
    const key = el.getAttribute("data-i18n");
    const val = t(key);
    const input = el.querySelector("input");
    el.textContent = val;
    if (input) el.appendChild(input);
  });
  problemText.placeholder = t("problemPlaceholder");
  answerBox.placeholder = t("answerPlaceholder");
  document.documentElement.lang = currentLang === "zh" ? "zh-CN" : "en";
  renderSamples();
  btnLangZh.classList.toggle("active", currentLang === "zh");
  btnLangEn.classList.toggle("active", currentLang === "en");
  if (!busy) btnStart.textContent = t("startGuide");
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
    btn.addEventListener("click", () => { problemText.value = s.text; });
    container.appendChild(btn);
  });
}

btnLangZh.addEventListener("click", () => { currentLang = "zh"; applyLang(); });
btnLangEn.addEventListener("click", () => { currentLang = "en"; applyLang(); });

fileInput.addEventListener("change", (e) => {
  const file = e.target.files && e.target.files[0];
  if (file) handleImageFile(file);
  e.target.value = "";
});

cameraInput.addEventListener("change", (e) => {
  const file = e.target.files && e.target.files[0];
  if (file) handleImageFile(file);
  e.target.value = "";
});

dropZone.addEventListener("dragover", (e) => { e.preventDefault(); dropZone.classList.add("dragover"); });
dropZone.addEventListener("dragleave", () => dropZone.classList.remove("dragover"));
dropZone.addEventListener("drop", (e) => {
  e.preventDefault();
  dropZone.classList.remove("dragover");
  const file = e.dataTransfer.files && e.dataTransfer.files[0];
  if (file && file.type.startsWith("image/")) handleImageFile(file);
});

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

btnOpenCamera.addEventListener("click", openCamera);
btnCloseCamera.addEventListener("click", closeCamera);
btnSnap.addEventListener("click", snapFromCamera);
btnStart.addEventListener("click", startAiGuide);
btnSubmit.addEventListener("click", () => sendReply(false));
btnHint.addEventListener("click", () => sendReply(true));

btnCopy.addEventListener("click", async () => {
  const text = finalWriteup.textContent;
  try {
    await navigator.clipboard.writeText(text);
    btnCopy.textContent = t("copied");
    setTimeout(() => (btnCopy.textContent = t("copy")), 1200);
  } catch { alert(t("copyFailed")); }
});

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

function showPreview(file) {
  const url = URL.createObjectURL(file);
  preview.src = url; preview.hidden = false;
  preview.onload = () => URL.revokeObjectURL(url);
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

  const form = new FormData();
  form.append("file", file, file.name || "problem.png");
  try {
    const res = await fetch("/api/ocr", { method: "POST", body: form });
    const data = await res.json();
    if (!data.ok) { ocrStatus.textContent = data.message || t("ocrFailed"); ocrStatus.classList.add("bad"); return; }
    problemText.value = data.text || "";
    ocrStatus.textContent = (data.message || t("ocrDone")) + (currentImageBase64 ? " · " + t("imageAttached") : "");
  } catch { ocrStatus.textContent = t("netError"); ocrStatus.classList.add("bad"); }
}

function addBubble(role, text) {
  const div = document.createElement("div");
  div.className = "bubble " + role;
  div.textContent = text;
  chatLog.appendChild(div);
  chatLog.scrollTop = chatLog.scrollHeight;
}

function addFigureBubble(svg, caption) {
  if (!svg) return;
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
  chatLog.scrollTop = chatLog.scrollHeight;
  showWorkbench(svg);
}

function showWorkbench(svg) {
  latestFigureSvg = svg || latestFigureSvg;
  const wb = $("workbench");
  if (!wb) return;
  wb.hidden = false;
  if (latestFigureSvg) {
    $("figureLayer").innerHTML = latestFigureSvg;
  }
  resizeCanvas();
  syncBgMode();
  if (currentImageBase64) {
    $("photoLayer").src = `data:${currentImageMime || "image/jpeg"};base64,${currentImageBase64}`;
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
  const fig = $("figureLayer");
  const photo = $("photoLayer");
  const hasPhoto = Boolean(currentImageBase64);
  if (bgMode === "photo" && hasPhoto) {
    fig.style.visibility = "hidden";
    photo.hidden = false;
    $("toolBgPhoto").classList.add("active");
    $("toolBgFigure").classList.remove("active");
  } else {
    bgMode = "figure";
    fig.style.visibility = "visible";
    photo.hidden = true;
    $("toolBgFigure").classList.add("active");
    $("toolBgPhoto").classList.remove("active");
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
  $("btnStart").textContent = on ? (label || t("thinking")) : t("startGuide");
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
    const data = await fetchJson("/api/ai/start", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!data.ok) { startStatus.textContent = data.message || t("startFailed"); startStatus.classList.add("bad"); return; }
    sessionId = data.session_id;
    chatLog.innerHTML = "";
    donePanel.hidden = true;
    guidePanel.hidden = false;
    answerBox.value = "";
    $("workbench").hidden = true;
    labelsHidden = false;
    $("figureLayer").classList.remove("hide-labels");
    addBubble("ai", data.message || t("aiStart"));
    if (data.hint) addBubble("hint", t("hintPrefix") + data.hint);
    if (data.figure_svg) {
      addFigureBubble(data.figure_svg, data.figure_caption || "");
    } else if (currentImageBase64) {
      showWorkbench(null);
      bgMode = "photo";
      syncBgMode();
      $("workbench").hidden = false;
      resizeCanvas();
    }
    startStatus.textContent = t("started");
    feedback.textContent = data.feedback || t("defaultFeedback");
    feedback.className = "feedback ok";
    if (data.completed) showDone(data.final_solution || data.message);
  } catch (err) {
    const aborted = err && err.name === "AbortError";
    startStatus.textContent = aborted ? t("timeoutStart") : t("reqFailed");
    startStatus.classList.add("bad");
  } finally { setBusy(false); }
}

async function sendReply(wantHint) {
  if (!sessionId) return alert(t("startGuideFirst"));
  if (busy) return;
  const answer = answerBox.value;
  if (!wantHint && !answer.trim()) return alert(t("writeSomething"));
  setBusy(true, t("grading"));
  feedback.textContent = t("gradingMsg");
  feedback.className = "feedback";
  if (!wantHint) addBubble("student", answer.trim());
  try {
    const data = await fetchJson("/api/ai/reply", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_id: sessionId, answer: answer, want_hint: wantHint }),
    });
    if (!data.ok) { feedback.textContent = data.message || t("submitFailed"); feedback.className = "feedback bad"; return; }
    if (data.feedback) {
      const tag = data.is_correct === true ? "ok" : data.is_correct === false ? "bad" : "";
      feedback.textContent = data.feedback;
      feedback.className = "feedback " + tag;
    }
    if (data.message) addBubble("ai", data.message);
    if (data.hint) addBubble("hint", t("hintPrefix") + data.hint);
    if (data.figure_svg) addFigureBubble(data.figure_svg, data.figure_caption || "");
    if (!wantHint) answerBox.value = "";
    if (data.completed) showDone(data.final_solution || data.message);
  } catch (err) {
    const aborted = err && err.name === "AbortError";
    feedback.textContent = aborted ? t("timeoutReply") : t("reqFailedRetry");
    feedback.className = "feedback bad";
  } finally { setBusy(false); }
}

function showDone(solution) {
  guidePanel.hidden = true;
  donePanel.hidden = false;
  finalWriteup.textContent = solution || "";
}

// ===== Workbench tools =====
$("toolPen").addEventListener("click", () => {
  drawMode = "pen";
  $("toolPen").classList.add("active");
  $("toolEraser").classList.remove("active");
});
$("toolEraser").addEventListener("click", () => {
  drawMode = "eraser";
  $("toolEraser").classList.add("active");
  $("toolPen").classList.remove("active");
});
$("toolClear").addEventListener("click", clearDrawings);
$("toolToggleLabels").addEventListener("click", () => {
  labelsHidden = !labelsHidden;
  $("figureLayer").classList.toggle("hide-labels", labelsHidden);
  $("toolToggleLabels").classList.toggle("active", labelsHidden);
});
$("toolBgFigure").addEventListener("click", () => {
  bgMode = "figure";
  syncBgMode();
});
$("toolBgPhoto").addEventListener("click", () => {
  if (!currentImageBase64) {
    alert(t("noPhoto"));
    return;
  }
  bgMode = "photo";
  syncBgMode();
});

setupDrawing();
applyLang();
