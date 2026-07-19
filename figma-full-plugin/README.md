# 完整包：高保真 UI + 开场动画 → 导入 Figma

一次运行生成：

- 开场动画 **4 个关键帧**（可在 Figma 里用 Prototype + Smart Animate 串起来）
- 高保真 **5 个 App 屏幕**
- 你的 **App Logo** 已内嵌（开场 + 侧栏）

**不会改**你原来的 Figma 文件。

## 导入步骤

1. 打开 [figma.com](https://www.figma.com) → **New design file**
2. **Plugins → Development → Import plugin from manifest…**
3. 选择：
   ```
   e:\Learning\triangle-guide\figma-full-plugin\manifest.json
   ```
4. 运行：**Plugins → Development → Triangle Guide Full (Hi-Fi + Splash)**
5. 新页面名：`Full UI · Splash + Hi-Fi`

## 开场怎么在 Figma 里播

1. 选中 `Splash / 01` → 右侧 **Prototype**
2. 依次连线：`01 → 02 → 03 → 04 → 01 Home`
3. 交互：After delay / On tap，动画选 **Smart Animate**，约 400–600ms
4. 点右上角 **Present** 预览

## 重新生成（换了 logo 时）

```bat
python -c "from pathlib import Path; import base64; p=Path(r'e:\Learning\triangle-guide\app\static\hifi\assets\app-logo.png'); Path(r'e:\Learning\triangle-guide\figma-full-plugin\logo.b64').write_text(base64.b64encode(p.read_bytes()).decode(), encoding='ascii')"
python e:\Learning\triangle-guide\figma-full-plugin\generate.py
```
