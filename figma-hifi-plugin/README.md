# 高保真 UI → 导入 Figma

在**新建空白 Design 文件**里运行本插件，生成 5 个高保真屏幕（对齐你现有 Figma 的配色与信息架构）。  
**不会修改**原来的 Untitled 文件。

## 导入步骤

1. 打开 [figma.com](https://www.figma.com) → **New design file**
2. **Plugins → Development → Import plugin from manifest…**
3. 选择：
   ```
   e:\Learning\triangle-guide\figma-hifi-plugin\manifest.json
   ```
4. 运行：**Plugins → Development → Triangle Guide Hi-Fi UI**
5. 出现新页面 `Hi-Fi UI · triangle-guide`

## 生成屏幕

| 画板 | 内容 |
|------|------|
| 01 Home | 早上好 + 搜索题目 / 快速练习 |
| 02 Search | 上传照片 + 画板 + 题目文字 |
| 03 Guide | 示例芯片 + 画板 + AI 对话 |
| 04 Solid | 立体旋转 + 引导 |
| 05 Done | 完整解答 + 复制 |

## 重新生成 code.js

```bat
python e:\Learning\triangle-guide\figma-hifi-plugin\generate.py
```
