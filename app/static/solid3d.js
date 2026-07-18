/**
 * 初中立体几何可旋转示意图（纯 Canvas，无外部依赖）。
 * 用法：Solid3D.mount(canvas, figure) / Solid3D.setFigure(figure) / Solid3D.destroy()
 */
(function (global) {
  "use strict";

  let canvas = null;
  let ctx = null;
  let figure = null;
  let yaw = 0.55;
  let pitch = 0.35;
  let dragging = false;
  let lastX = 0;
  let lastY = 0;
  let raf = 0;
  let allowRotate = true;

  function dimsOf(f) {
    const d = (f && f.dims) || {};
    return {
      length: +d.length || 4,
      width: +d.width || 3,
      height: +d.height || 5,
      radius: +d.radius || 2,
    };
  }

  function buildMesh(f) {
    const solid = (f && f.solid) || "cube";
    const { length: L, width: W, height: H, radius: R } = dimsOf(f);
    const verts = {};
    const edges = [];

    if (solid === "cube") {
      const a = L;
      Object.assign(verts, {
        A: [0, 0, 0], B: [a, 0, 0], C: [a, a, 0], D: [0, a, 0],
        E: [0, 0, a], F: [a, 0, a], G: [a, a, a], H: [0, a, a],
      });
      edges.push(
        ["A", "B"], ["B", "C"], ["C", "D"], ["D", "A"],
        ["E", "F"], ["F", "G"], ["G", "H"], ["H", "E"],
        ["A", "E"], ["B", "F"], ["C", "G"], ["D", "H"]
      );
    } else if (solid === "rectangular_prism") {
      Object.assign(verts, {
        A: [0, 0, 0], B: [L, 0, 0], C: [L, W, 0], D: [0, W, 0],
        E: [0, 0, H], F: [L, 0, H], G: [L, W, H], H: [0, W, H],
      });
      edges.push(
        ["A", "B"], ["B", "C"], ["C", "D"], ["D", "A"],
        ["E", "F"], ["F", "G"], ["G", "H"], ["H", "E"],
        ["A", "E"], ["B", "F"], ["C", "G"], ["D", "H"]
      );
    } else if (solid === "triangular_prism") {
      Object.assign(verts, {
        A: [0, 0, 0], B: [L, 0, 0], C: [L * 0.5, W, 0],
        D: [0, 0, H], E: [L, 0, H], F: [L * 0.5, W, H],
      });
      edges.push(
        ["A", "B"], ["B", "C"], ["C", "A"],
        ["D", "E"], ["E", "F"], ["F", "D"],
        ["A", "D"], ["B", "E"], ["C", "F"]
      );
    } else if (solid === "square_pyramid") {
      Object.assign(verts, {
        A: [0, 0, 0], B: [L, 0, 0], C: [L, W, 0], D: [0, W, 0],
        S: [L * 0.5, W * 0.5, H],
      });
      edges.push(
        ["A", "B"], ["B", "C"], ["C", "D"], ["D", "A"],
        ["A", "S"], ["B", "S"], ["C", "S"], ["D", "S"]
      );
    } else if (solid === "cylinder" || solid === "cone") {
      const n = 24;
      for (let i = 0; i < n; i++) {
        const ang = (Math.PI * 2 * i) / n;
        const x = R + R * Math.cos(ang);
        const y = R + R * Math.sin(ang);
        verts["B" + i] = [x, y, 0];
        edges.push(["B" + i, "B" + ((i + 1) % n)]);
        if (solid === "cylinder") {
          verts["T" + i] = [x, y, H];
          edges.push(["T" + i, "T" + ((i + 1) % n)]);
          if (i % 4 === 0) edges.push(["B" + i, "T" + i]);
        } else {
          edges.push(["B" + i, "S"]);
        }
      }
      if (solid === "cone") verts.S = [R, R, H];
    } else {
      return buildMesh({ solid: "cube", dims: { length: 4, width: 4, height: 4, radius: 2 } });
    }

    // 居中，并缩放到单位尺度，保证相机始终在几何体外
    const keys = Object.keys(verts);
    let cx = 0, cy = 0, cz = 0;
    keys.forEach((k) => {
      cx += verts[k][0]; cy += verts[k][1]; cz += verts[k][2];
    });
    cx /= keys.length; cy /= keys.length; cz /= keys.length;
    let maxR = 1e-6;
    keys.forEach((k) => {
      const x = verts[k][0] - cx;
      const y = verts[k][1] - cy;
      const z = verts[k][2] - cz;
      verts[k] = [x, y, z];
      maxR = Math.max(maxR, Math.hypot(x, y, z));
    });
    const norm = 1.35 / maxR; // 归一化后半径约 1.35
    keys.forEach((k) => {
      verts[k] = [verts[k][0] * norm, verts[k][1] * norm, verts[k][2] * norm];
    });
    return { verts, edges, solid };
  }

  function rotate(p) {
    let [x, y, z] = p;
    const cy = Math.cos(yaw), sy = Math.sin(yaw);
    let x1 = x * cy - y * sy;
    let y1 = x * sy + y * cy;
    const cp = Math.cos(pitch), sp = Math.sin(pitch);
    let y2 = y1 * cp - z * sp;
    let z2 = y1 * sp + z * cp;
    return [x1, y2, z2];
  }

  function project(p, w, h) {
    const [x, y, z] = rotate(p);
    // 正交投影：无近大远小，旋转时立方体不会被透视“扯歪”
    const scale = Math.min(w, h) * 0.34;
    return {
      x: w / 2 + x * scale,
      y: h / 2 - z * scale,
      depth: y,
    };
  }

  function hiSet(f) {
    const set = new Set();
    (f.highlight_edges || []).forEach((e) => {
      if (Array.isArray(e) && e.length >= 2) set.add([e[0], e[1]].map(String).sort().join("-"));
    });
    return set;
  }

  function draw() {
    if (!ctx || !canvas || !figure) return;
    const dpr = window.devicePixelRatio || 1;
    const w = canvas.clientWidth || 360;
    const h = canvas.clientHeight || 280;
    if (canvas.width !== Math.round(w * dpr) || canvas.height !== Math.round(h * dpr)) {
      canvas.width = Math.round(w * dpr);
      canvas.height = Math.round(h * dpr);
    }
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, w, h);
    ctx.fillStyle = "#fffdf8";
    ctx.fillRect(0, 0, w, h);

    const mesh = buildMesh(figure);
    const hi = hiSet(figure);
    const projected = {};
    Object.keys(mesh.verts).forEach((k) => {
      projected[k] = project(mesh.verts[k], w, h);
    });

    const sorted = mesh.edges.slice().sort((e1, e2) => {
      const d1 = (projected[e1[0]].depth + projected[e1[1]].depth) / 2;
      const d2 = (projected[e2[0]].depth + projected[e2[1]].depth) / 2;
      return d1 - d2;
    });

    sorted.forEach(([a, b]) => {
      const p1 = projected[a];
      const p2 = projected[b];
      if (!p1 || !p2) return;
      const key = [a, b].map(String).sort().join("-");
      const isHi = hi.has(key);
      const back = (p1.depth + p2.depth) / 2 > 0.15;
      ctx.beginPath();
      ctx.moveTo(p1.x, p1.y);
      ctx.lineTo(p2.x, p2.y);
      ctx.strokeStyle = isHi ? "#c45c26" : "#1c2a24";
      ctx.lineWidth = isHi ? 2.8 : 2.1;
      ctx.setLineDash(back && mesh.solid !== "cylinder" && mesh.solid !== "cone" ? [5, 4] : []);
      ctx.stroke();
      ctx.setLineDash([]);
    });

    // 顶点字母
    if (["cube", "rectangular_prism", "triangular_prism", "square_pyramid"].includes(mesh.solid)) {
      ctx.fillStyle = "#1c2a24";
      ctx.font = "700 13px Segoe UI, Microsoft YaHei, sans-serif";
      Object.keys(projected).forEach((name) => {
        if (name.length > 2) return;
        const p = projected[name];
        ctx.fillText(name, p.x + 6, p.y - 6);
      });
    }

    const labels = figure.labels || {};
    const bits = Object.keys(labels).slice(0, 4).map((k) => `${k}=${labels[k]}`).join(" · ");
    if (bits) {
      ctx.fillStyle = "#0f6b4c";
      ctx.font = "13px Segoe UI, Microsoft YaHei, sans-serif";
      ctx.textAlign = "center";
      ctx.fillText(bits, w / 2, 20);
      ctx.textAlign = "start";
    }

    const cap = figure.caption || "";
    if (cap) {
      ctx.fillStyle = "#5a6b62";
      ctx.font = "13px Segoe UI, Microsoft YaHei, sans-serif";
      ctx.textAlign = "center";
      ctx.fillText(cap, w / 2, h - 12);
      ctx.textAlign = "start";
    }

    if (allowRotate) {
      ctx.fillStyle = "#8a9a92";
      ctx.font = "12px Segoe UI, Microsoft YaHei, sans-serif";
      ctx.fillText("拖动旋转（形状固定）", 10, h - 12);
    }
  }

  function schedule() {
    if (raf) return;
    raf = requestAnimationFrame(() => {
      raf = 0;
      draw();
    });
  }

  function onDown(ev) {
    if (!allowRotate) return;
    dragging = true;
    const p = ev.touches ? ev.touches[0] : ev;
    lastX = p.clientX;
    lastY = p.clientY;
    ev.preventDefault();
  }
  function onMove(ev) {
    if (!allowRotate || !dragging) return;
    const p = ev.touches ? ev.touches[0] : ev;
    const dx = p.clientX - lastX;
    const dy = p.clientY - lastY;
    lastX = p.clientX;
    lastY = p.clientY;
    yaw += dx * 0.01;
    pitch = Math.max(-1.2, Math.min(1.2, pitch + dy * 0.01));
    schedule();
    ev.preventDefault();
  }
  function onUp() {
    dragging = false;
  }

  function bind() {
    canvas.addEventListener("mousedown", onDown);
    window.addEventListener("mousemove", onMove);
    window.addEventListener("mouseup", onUp);
    canvas.addEventListener("touchstart", onDown, { passive: false });
    canvas.addEventListener("touchmove", onMove, { passive: false });
    canvas.addEventListener("touchend", onUp);
  }

  function unbind() {
    if (!canvas) return;
    canvas.removeEventListener("mousedown", onDown);
    window.removeEventListener("mousemove", onMove);
    window.removeEventListener("mouseup", onUp);
    canvas.removeEventListener("touchstart", onDown);
    canvas.removeEventListener("touchmove", onMove);
    canvas.removeEventListener("touchend", onUp);
  }

  const api = {
    mount(el, fig) {
      canvas = el;
      ctx = el.getContext("2d");
      figure = fig;
      yaw = 0.55;
      pitch = 0.35;
      allowRotate = true;
      canvas.style.cursor = "grab";
      canvas.style.pointerEvents = "auto";
      bind();
      schedule();
    },
    setFigure(fig) {
      figure = fig;
      schedule();
    },
    setRotateEnabled(on) {
      allowRotate = !!on;
      if (canvas) {
        canvas.style.cursor = allowRotate ? "grab" : "default";
        canvas.style.pointerEvents = allowRotate ? "auto" : "none";
      }
      schedule();
    },
    resize() {
      schedule();
    },
    destroy() {
      unbind();
      if (raf) cancelAnimationFrame(raf);
      raf = 0;
      canvas = null;
      ctx = null;
      figure = null;
    },
    isSolid(fig) {
      return !!(fig && (fig.type === "solid" || fig.solid));
    },
  };

  global.Solid3D = api;
})(window);
