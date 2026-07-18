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

## 部署到树莓派

本质不变：树莓派当「小服务器」，手机/电脑浏览器访问它。

### 推荐硬件

- Raspberry Pi 4 / 5（建议 **4GB+** 内存）
- 已装 **Raspberry Pi OS (64-bit)**，能上网
- Pi 3 也能跑，但 OCR/装依赖会更慢

### 步骤

1. **把项目拷到树莓派**（任选）
   - U 盘 / SCP：`scp -r triangle-guide pi@树莓派IP:~/`
   - 或在派上：`git clone ...` 后进入 `triangle-guide`

2. **装系统依赖**（在派上执行一次）

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip
```

3. **配置密钥**

```bash
cd ~/triangle-guide   # 按你的实际路径
cp .env.example .env
nano .env             # 填入 DEEPSEEK_API_KEY、DASHSCOPE_API_KEY
```

4. **启动**

```bash
chmod +x start.sh
./start.sh
```

首次 `pip install` 在树莓派上可能要十几分钟，属正常。

5. **怎么打开页面**
   - 查派的 IP：`hostname -I`（例如 `192.168.1.20`）
   - 同一 Wi‑Fi 下，手机/电脑浏览器打开：`http://192.168.1.20:8001`
   - 派本机浏览器：`http://127.0.0.1:8001`

> `start.sh` 默认监听 `0.0.0.0:8001`，局域网才能访问。若只想本机用，可：  
> `HOST=127.0.0.1 ./start.sh`

### 开机自启（可选）

用 systemd 建服务，例如 `/etc/systemd/system/triangle-guide.service`：

```ini
[Unit]
Description=Triangle Guide
After=network.target

[Service]
User=pi
WorkingDirectory=/home/pi/triangle-guide
ExecStart=/home/pi/triangle-guide/.venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8001
Restart=always

[Install]
WantedBy=multi-user.target
```

然后：

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now triangle-guide
```

### 树莓派上要注意

| 点 | 说明 |
|----|------|
| 必须能上网 | AI 仍走云端（DeepSeek / 百炼），派只跑网页服务 |
| OCR 偏重 | `ddddocr` 首次加载慢；内存不够可先只测文字题 |
| 摄像头 | 网页「拍照」用的是**访问端**设备摄像头（手机浏览器），不是必须插派摄像头 |
| 防火墙 | 若开了 ufw：`sudo ufw allow 8001` |

## 常见问题

- **打不开页面**：确认终端里 uvicorn 在跑，地址是 `8001` 端口  
- **看图失败**：检查 `DASHSCOPE_API_KEY` 与百炼余额/开通  
- **引导失败**：检查 `DEEPSEEK_API_KEY` 与账户余额  
- **语音输入失败**：语音走百炼 ASR（同一把 `DASHSCOPE_API_KEY`），请用 Chrome/Edge 并允许麦克风；点一次开始录音，再点一次结束并识别  
- **局域网打不开**：确认用了 `0.0.0.0` 启动，且电脑/手机与派在同一网络  
