# 在 Figma 里生成解三角形 Wireframe

Cursor 连接的 Figma MCP **只能读文件，不能直接在画布上画画**。  
用这个本地插件，在**新建空白文件**里一键生成整套 wireframe，**不会改你原来的 Untitled 文件**。

## 操作步骤

1. 打开 [figma.com](https://www.figma.com) → 左上角 **New design file**（一定要新建，别开旧文件）
2. 菜单栏：**Plugins → Development → Import plugin from manifest…**
3. 选中这个文件：
   ```
   e:\Learning\triangle-guide\figma-wireframe-plugin\manifest.json
   ```
4. 再运行：**Plugins → Development → Triangle Guide Wireframe v2**
5. 完成后会出现新页面 `Wireframe v2 · triangle-guide`，内含封面 + 7 个屏幕线框

## 生成内容

| 画板 | 内容 |
|------|------|
| 00 Cover | 流程总览 |
| 01 | 首页输入（上传/拍照/语音/示例） |
| 02 | 识图预览 |
| 03 | 摄像头 |
| 04 | AI 引导 · 平面画板分栏 |
| 05 | AI 引导 · 立体旋转 |
| 06 | 完整解答 |
| 07 | 移动端两态 |

## 若改了文案后要重新生成

```bat
python e:\Learning\triangle-guide\figma-wireframe-plugin\generate.py
```

然后在 Figma 里再跑一次插件即可。
