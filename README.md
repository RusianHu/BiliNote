<div style="display: flex; justify-content: center; align-items: center; gap: 10px;
">
    <p align="center">
  <img src="./doc/icon.svg" alt="BiliNote Banner" width="50" height="50"  />
</p>
<h1 align="center" > BiliNote v1.0.1.1</h1>
</div>

> 本项目是基于 [JefferyHcool/BiliNote](https://github.com/JefferyHcool/BiliNote) 的分支，感谢原作者的开源贡献。

<p align="center"><i>AI 视频笔记生成工具 让 AI 为你的视频做笔记</i></p>

<p align="center">
  <img src="https://img.shields.io/badge/license-MIT-blue.svg" />
  <img src="https://img.shields.io/badge/frontend-react-blue" />
  <img src="https://img.shields.io/badge/backend-fastapi-green" />
  <img src="https://img.shields.io/badge/GPT-openai%20%7C%20deepseek%20%7C%20qwen%20%7C%20openrouter-ff69b4" />
  <img src="https://img.shields.io/badge/docker-compose-blue" />
  <img src="https://img.shields.io/badge/status-active-success" />
  <img src="https://img.shields.io/github/stars/jefferyhcool/BiliNote?style=social" />
</p>



## ✨ 项目简介

BiliNote 是一个开源的 AI 视频笔记助手，支持通过哔哩哔哩、YouTube 等视频链接，自动提取内容并生成结构清晰、重点明确的 Markdown 格式笔记。支持插入截图、原片跳转等功能。

## 🔧 功能特性

- 支持多平台：Bilibili、YouTube（后续会加入更多平台）
- 本地模型音频转写（支持 Fast-Whisper）
- GPT 大模型总结视频内容（支持 OpenAI、DeepSeek、Qwen、OpenRouter）
- 自动生成结构化 Markdown 笔记
- 可选插入截图（自动截取）
- 可选内容跳转链接（关联原视频）
- 任务记录与历史回看

## 📸 截图预览
![screenshot](./doc/image1.png)
![screenshot](./doc/image2.png)
![screenshot](./doc/image3.png)

## 🚀 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/JefferyHcool/BiliNote.git
cd BiliNote
mv .env.example .env
```

### 2. 使用一键启动脚本（Windows）

```bash
# 双击运行 start_dev.bat 或在命令行执行：
start_dev.bat
```

这将自动启动后端和前端服务，并在两个独立的终端窗口中显示运行状态。

> 注意：一键启动脚本默认使用 Python 3.8 运行后端服务。如果您的系统中没有 Python 3.8，请修改 `start_dev.bat` 文件中的 `py -3.8` 为您系统中可用的 Python 版本。

### 3. 手动启动（所有平台）

#### 启动后端（FastAPI）

```bash
cd backend
pip install -r requirements.txt
python main.py
```

#### 启动前端（Vite + React）

```bash
cd BiliNote_frontend
pnpm install
pnpm dev
```

访问：`http://localhost:5173`

## ⚙️ 依赖说明
### 🎬 FFmpeg
本项目依赖 ffmpeg 用于音频处理与转码，必须安装：
```bash
# Mac (brew)
brew install ffmpeg

# Ubuntu / Debian
sudo apt install ffmpeg

# Windows
# 请从官网下载安装：https://ffmpeg.org/download.html
```
> ⚠️ 若系统无法识别 ffmpeg，请将其加入系统环境变量 PATH

### 🚀 CUDA 加速（可选）
若你希望更快地执行音频转写任务，可使用具备 NVIDIA GPU 的机器，并启用 fast-whisper + CUDA 加速版本：

具体 `fast-whisper` 配置方法，请参考：[fast-whisper 项目地址](http://github.com/SYSTRAN/faster-whisper#requirements)

### 🐳 使用 Docker 一键部署

确保你已安装 Docker 和 Docker Compose：

#### 1. 克隆本项目
```bash
git clone https://github.com/JefferyHcool/BiliNote.git
cd BiliNote
mv .env.example .env
```
#### 2. 启动 Docker Compose
``` bash
docker compose up --build
```
默认端口：

前端：http://localhost:${FRONTEND_PORT}

后端：http://localhost:${BACKEND_PORT}

.env 文件中可自定义端口与环境配置。


## ⚙️ 环境变量配置

`.env` 文件配置示例：

```ini
# 通用端口配置
BACKEND_PORT=8000
BACKEND_HOST=127.0.0.1

# 前端访问后端用
VITE_API_BASE_URL=http://127.0.0.1:8000
VITE_SCREENSHOT_BASE_URL=http://127.0.0.1:8000/static/screenshots

# 生产环境配置
ENV=production
STATIC=/static
OUT_DIR=./static/screenshots
IMAGE_BASE_URL=/static/screenshots
DATA_DIR=data

# AI 相关配置
# --- 选择 AI 提供商 ---
MODEL_PROVIDER=openai # 可选值: openai, deepseek, qwen, openrouter

# --- OpenAI 设置 ---
OPENAI_API_KEY=
OPENAI_API_BASE_URL=
OPENAI_MODEL=

# --- DeepSeek 设置 ---
DEEP_SEEK_API_KEY=
DEEP_SEEK_API_BASE_URL=https://api.deepseek.com
DEEP_SEEK_MODEL=deepseek-chat

# --- Qwen 设置 ---
QWEN_API_KEY=
QWEN_API_BASE_URL=
QWEN_MODEL=

# --- OpenRouter 设置 ---
OPENROUTER_API_KEY= # 替换为你的 OpenRouter API Key
OPENROUTER_MODEL=google/gemini-2.5-flash-preview # 或者其他 OpenRouter 支持的模型 ID

# --- 截图设置 ---
OUT_DIR=./static/screenshots
IMAGE_BASE_URL=/static/screenshots

# FFMPEG 配置
# 打包后的应用会自动查找bin目录下的ffmpeg
FFMPEG_BIN_PATH=bin/ffmpeg.exe
```

## 🧠 TODO

- [ ] 支持抖音及快手等视频平台
- [ ] 支持前端设置切换 AI 模型切换、语音转文字模型
- [ ] AI 摘要风格自定义（学术风、口语风、重点提取等）
- [ ] 笔记导出为 PDF / Word / Notion
- [x] 加入更多模型支持（已支持 OpenAI、DeepSeek、Qwen、OpenRouter）
- [ ] 加入更多音频转文本模型支持

## 📜 License

MIT License

## 👥 关于本 Fork

本项目是基于 [JefferyHcool/BiliNote](https://github.com/JefferyHcool/BiliNote) 的分支，对原项目进行了以下改进：

- 添加了一键启动脚本 `start_dev.bat`，方便 Windows 用户快速启动项目
- 完善了文档和使用说明
- 优化了部分代码结构
- 增加了 OpenRouter 支持（可使用 Claude、Gemini 等多种模型）
---

💬 你的支持与反馈是我持续优化的动力！欢迎 PR、提 issue、Star ⭐️

