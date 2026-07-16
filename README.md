# 解题助手（原型）

拍照 / 上传几何题 → 百炼识图描摹 → DeepSeek 逐步引导。

## 别人电脑怎么用（推荐）

### 1. 准备环境

- 安装 [Python 3.10+](https://www.python.org/downloads/)（安装时勾选 **Add Python to PATH**）
- 需要能上网（调用 DeepSeek、阿里云百炼）

### 2. 拿到项目

任选一种：

- **Git**：`git clone https://github.com/Akane-101/LearningTool.git`  
  然后进入 `triangle-guide` 目录  
- **压缩包**：把本文件夹打成 zip（不要包含 `.venv`、`.env`），发给对方解压

### 3. 配置密钥

在 `triangle-guide` 目录：

1. 复制 `.env.example` 为 `.env`
2. 填入自己的 Key（**不要用别人的 Key 分享出去**）：

```env
DEEPSEEK_API_KEY=你的DeepSeek密钥
DASHSCOPE_API_KEY=你的百炼密钥
```

- DeepSeek：https://platform.deepseek.com/  
- 百炼：https://bailian.console.aliyun.com/

### 4. 启动

**Windows**：双击 `start.bat`  

或手动：

```bat
cd triangle-guide
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\python -m uvicorn app.main:app --host 127.0.0.1 --port 8001
```

浏览器打开：http://127.0.0.1:8001

## 打包时注意

| 要带走 | 不要带走 |
|--------|----------|
| `app/`、`requirements.txt`、`.env.example`、`start.bat`、`README.md` | `.venv/`（体积大，对方自己装） |
| | `.env`（含密钥，各自配置） |
| | `__pycache__/` |

在资源管理器中选中上述文件/文件夹 → 右键压缩即可。

## 功能说明

- **文字题**：直接粘贴后点「开始 AI 引导」
- **有图题**：上传/拍照 → 自动识字+描图 → 可叠加原图拖动对齐 → AI 引导
- 无原图时不会显示「叠加原图 / 只看原图」

## 常见问题

- **打不开页面**：确认终端里 uvicorn 在跑，地址是 `8001` 端口  
- **看图失败**：检查 `DASHSCOPE_API_KEY` 与百炼余额/开通  
- **引导失败**：检查 `DEEPSEEK_API_KEY` 与账户余额  
