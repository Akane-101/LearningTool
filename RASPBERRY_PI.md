# 树莓派部署指南（零基础版）

目标：让树莓派跑起「解题助手」，你用手机或电脑浏览器打开使用。

---

## 0. 先搞懂在干什么

| 角色 | 做什么 |
|------|--------|
| 树莓派 | 一直开着，当一台「小电脑服务器」 |
| 手机 / 电脑 | 打开网页 `http://树莓派的IP:8001` 来用 |
| 互联网 | AI（DeepSeek、百炼）还在云上算，派必须能上网 |

不是把程序「烧进芯片」就结束，而是：**派上要一直运行一个小程序**，浏览器才能连上它。

---

## 1. 你需要买什么

### 必备

1. **树莓派主板**  
   - 推荐：**Raspberry Pi 5** 或 **Pi 4**（内存 **4GB 或以上**）  
   - 不推荐太老的 Pi Zero（会很卡）

2. **电源**  
   - Pi 4：官方 5V/3A USB-C 电源  
   - Pi 5：官方 27W 电源更稳  
   - 普通手机充电器经常不够力，容易重启

3. **存储卡**  
   - microSD，**建议 32GB 及以上**，Class 10 / A1  
   - 品牌靠谱一点（三星、闪迪等）

4. **读卡器**  
   - 用来在 Windows 电脑上给 SD 卡写系统

5. **能上网**  
   - 家里 Wi‑Fi，或网线插路由器

### 建议再买（第一次更好上手）

| 配件 | 为什么 |
|------|--------|
| 散热片 / 小风扇 / 带风扇外壳 | 少过热、少死机 |
| HDMI 线 + 显示器 + 键鼠 | **第一次装系统最省事**（像用普通电脑） |
| 网线 | 比 Wi‑Fi 稳定（可选） |

> 没有显示器也可以，用「无头」方式，但对新手更难。下面按**有显示器+键鼠**写。

---

## 2. 在电脑上给 SD 卡安装系统

在你的 **Windows 电脑**上做：

### 2.1 下载官方烧录工具

1. 打开：https://www.raspberrypi.com/software/  
2. 下载并安装 **Raspberry Pi Imager**

### 2.2 写入系统

1. 把 microSD 卡插进读卡器，插入电脑  
2. 打开 Raspberry Pi Imager  
3. 按下面选：

| 选项 | 选什么 |
|------|--------|
| 选择设备 | 你的树莓派型号（如 Raspberry Pi 5） |
| 选择操作系统 | **Raspberry Pi OS (64-bit)**（带桌面的那个） |
| 选择存储 | 你的 SD 卡（看清楚盘符，别选错 U 盘） |

4. 点右下角 **齿轮 / 设置**（或「编辑设置」），建议勾选：

   - **设置主机名**：例如 `raspberrypi`  
   - **启用 SSH**（以后可用电脑远程连）  
   - **设置用户名和密码**：例如用户 `pi`，密码自己设并记住  
   - **配置无线局域网**：填你家 Wi‑Fi 名称和密码（国家选 `CN`）  
   - **区域设置**：时区选 `Asia/Shanghai`，键盘可选中文或美式

5. 保存 → 点 **写入** → 等待完成（几分钟）  
6. 弹出 SD 卡，从电脑拔出

---

## 3. 第一次开机

1. 把写好的 SD 卡插入树莓派背面卡槽  
2. 接上显示器（HDMI）、键盘、鼠标  
3. **最后**插电源（树莓派没有开关，插电即开机）  
4. 等几分钟，出现桌面  
5. 若提示更新，可先跳过或按提示完成  
6. 看右上角有没有 Wi‑Fi 图标；没连上就点图标连你家 Wi‑Fi

### 确认能上网

打开树莓派自带浏览器，访问任意网站（如 baidu.com）。  
能打开再继续。

### 查出树莓派的 IP 地址（很重要）

1. 点左上角树莓图标 → **附件** → **终端**  
2. 输入下面命令，回车：

```bash
hostname -I
```

3. 会显示类似：`192.168.1.20`  
   - 记下这个数字，后面手机要用  
   - 若有两个，一般选 `192.168.` 开头的那个

---

## 4. 把「解题助手」项目拷到树莓派

任选 **一种** 方法。

### 方法 A：U 盘（最简单）

**在 Windows 上：**

1. 打开 `e:\Learning\triangle-guide`  
2. **不要**拷贝里面的 `.venv` 文件夹（没有也没关系）  
3. **不要**拷贝 `.env`（里面有密钥，到派上再新建）  
4. 把整个 `triangle-guide` 文件夹复制到 U 盘

**在树莓派上：**

1. 插入 U 盘，桌面或文件管理器里打开 U 盘  
2. 把 `triangle-guide` 复制到：`/home/你的用户名/`  
   - 例如用户是 `pi`，就复制到 `/home/pi/triangle-guide`  
3. 安全弹出 U 盘

### 方法 B：用 Git（派已联网）

在树莓派「终端」里：

```bash
cd ~
sudo apt update
sudo apt install -y git
git clone https://github.com/Akane-101/LearningTool.git
cd LearningTool/triangle-guide
```

> 若仓库结构和上面不一致，以你实际文件夹为准，最终要进入有 `app`、`requirements.txt`、`start.sh` 的目录。

### 方法 C：从 Windows 用 scp 传（进阶）

Windows PowerShell：

```powershell
scp -r e:\Learning\triangle-guide pi@192.168.1.20:~/
```

把 `pi` 和 IP 换成你的用户名和 IP。首次会问是否信任，输入 `yes`，再输入树莓派密码。

---

## 5. 在树莓派上安装运行环境

打开**终端**，依次输入（每行回车，等做完再下一行）：

### 5.1 进入项目目录

```bash
cd ~/triangle-guide
```

若你放在别的路径，先 `cd` 到那个路径。  
用下面命令确认目录对不对：

```bash
ls
```

应能看到：`app`、`requirements.txt`、`start.sh`、`.env.example` 等。

### 5.2 安装 Python 工具

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip
```

中间若问 `Y/n`，输入 `Y` 回车。

### 5.3 创建配置文件并填密钥

```bash
cp .env.example .env
nano .env
```

`nano` 是简易编辑器：

1. 找到这两行，改成你的真实密钥（不要留「把这里换成…」）：

```env
DEEPSEEK_API_KEY=sk-xxxxxxxx
DASHSCOPE_API_KEY=sk-xxxxxxxx
```

2. 改完：按键盘 **Ctrl + O** → 回车（保存）  
3. 再按 **Ctrl + X**（退出）

密钥从哪里拿：

- DeepSeek：https://platform.deepseek.com/  
- 阿里云百炼：https://bailian.console.aliyun.com/

---

## 6. 第一次启动

仍在项目目录下：

```bash
chmod +x start.sh
./start.sh
```

### 你会看到什么

1. 创建虚拟环境 `.venv`  
2. **安装依赖** —— 树莓派上可能要 **10～30 分钟**，看起来卡住也先等  
3. 最后出现类似：

```text
Uvicorn running on http://0.0.0.0:8001
```

说明服务已经起来了。  
**这个终端窗口不要关**，关掉服务就停了。

---

## 7. 用手机 / 电脑打开网页

1. 手机连**和树莓派同一个 Wi‑Fi**（很重要）  
2. 浏览器地址栏输入（IP 换成你查到的）：

```text
http://192.168.1.20:8001
```

3. 应出现「解题助手」页面  

树莓派本机浏览器也可以打开：

```text
http://127.0.0.1:8001
```

### 打不开时逐项检查

| 情况 | 怎么办 |
|------|--------|
| 手机不是同一 Wi‑Fi | 改连同一个路由器 |
| IP 记错 | 再在派上执行 `hostname -I` |
| 服务没启动 | 终端里有没有 `Uvicorn running` |
| 路由开启了「AP 隔离」 | 换电脑有线连同一路由试，或关访客网络 |
| 地址写成了 https | 用 **http**，不要加 s |

---

## 8. 日常怎么用

### 每次要用时

1. 给树莓派通电  
2. 打开终端：

```bash
cd ~/triangle-guide
./start.sh
```

3. 手机打开 `http://派的IP:8001`

### 想关掉

在运行 `start.sh` 的终端里按：**Ctrl + C**

---

## 9. 想开机自动启动（可选，进阶）

不想每次手动 `./start.sh`，可以做成系统服务。

1. 先确认项目路径，例如 `/home/pi/triangle-guide`  
2. 先手动跑成功过一次（保证 `.venv` 已装好）  
3. 终端执行：

```bash
sudo nano /etc/systemd/system/triangle-guide.service
```

4. 粘贴下面内容（**两处路径和 User= 按你的用户改**）：

```ini
[Unit]
Description=解题助手
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/triangle-guide
ExecStart=/home/pi/triangle-guide/.venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8001
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

5. Ctrl+O 保存，Ctrl+X 退出，然后：

```bash
sudo systemctl daemon-reload
sudo systemctl enable triangle-guide
sudo systemctl start triangle-guide
sudo systemctl status triangle-guide
```

看到 `active (running)` 就成功了。  
以后开机等 1～2 分钟，手机直接访问即可。

查看日志：

```bash
journalctl -u triangle-guide -f
```

---

## 10. 常见问题（零基础）

### 「sudo 要密码」

输入的是你给树莓派设的用户密码。输入时屏幕**不显示字符**，输完直接回车。

### 「Permission denied」跑 start.sh

```bash
chmod +x start.sh
./start.sh
```

### pip 安装失败 / 内存不够

- 尽量用 4GB 以上的派  
- 关掉浏览器等占内存程序再装  
- 可加重启后再执行 `./start.sh`

### OCR（本地识字）很慢

正常。树莓派 CPU 弱，识字会慢一些；看图和 AI 引导主要靠云端，相对还好。

### 语音输入没反应

用手机 **Chrome** 打开页面，并允许麦克风。有的浏览器不支持网页语音识别。

### IP 老是变

路由器里给树莓派做「IP 绑定 / DHCP 保留」，或接受偶尔变一次、变了再查 `hostname -I`。

---

## 11. 建议你按这个顺序打勾

- [ ] 买齐：派 + 电源 + SD 卡 + 读卡器（+ 显示器键鼠更佳）  
- [ ] 用 Imager 写好 64 位系统，配好 Wi‑Fi 和用户密码  
- [ ] 开机进桌面，能上网  
- [ ] `hostname -I` 记下 IP  
- [ ] 项目拷到 `~/triangle-guide`  
- [ ] `apt` 装好 python3 / venv  
- [ ] 配好 `.env` 两个 Key  
- [ ] `./start.sh` 看到 Uvicorn running  
- [ ] 手机同一 Wi‑Fi 打开 `http://IP:8001` 成功  

全部勾完，你就已经「连上树莓派」了。

---

若卡在某一步：把**卡在第几步**、终端里的**完整报错原文**（可截图打字）记下来，再继续排查会很快。
