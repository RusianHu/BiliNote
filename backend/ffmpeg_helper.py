import os
import subprocess
from dotenv import load_dotenv
from typing import Optional # 导入 Optional

from app.utils.logger import get_logger
logger = get_logger(__name__)

load_dotenv()
def check_ffmpeg_exists() -> Optional[str]:
    """
    检查 ffmpeg 是否可用。优先使用 FFMPEG_BIN_PATH 环境变量指定的路径。
    如果找到 ffmpeg，返回其可执行文件路径，否则返回 None。
    """
    ffmpeg_bin_path = os.getenv("FFMPEG_BIN_PATH")
    logger.info(f"FFMPEG_BIN_PATH: {ffmpeg_bin_path}")
    if ffmpeg_bin_path:
        # 检查是否是文件路径
        if os.path.isfile(ffmpeg_bin_path) and os.path.exists(ffmpeg_bin_path):
            logger.info(f"使用指定的 ffmpeg 可执行文件: {ffmpeg_bin_path}")
            try:
                # 直接使用指定的可执行文件路径
                subprocess.run([ffmpeg_bin_path, "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
                logger.info("指定的 ffmpeg 可执行文件可用")
                return ffmpeg_bin_path
            except (FileNotFoundError, OSError, subprocess.CalledProcessError):
                logger.info("指定的 ffmpeg 可执行文件无法运行")
        # 检查是否是目录路径
        elif os.path.isdir(ffmpeg_bin_path):
            # 将目录添加到 PATH 环境变量
            # 注意：这里修改的是当前进程的环境变量，可能不会影响到 yt-dlp 的子进程
            # 但我们仍然尝试添加，并继续检查系统 PATH
            os.environ["PATH"] = ffmpeg_bin_path + os.pathsep + os.environ.get("PATH", "")
            logger.info(f"添加 ffmpeg 目录到 PATH: {os.environ.get('PATH')}")
        else:
            logger.info(f"指定的 ffmpeg 路径无效: {ffmpeg_bin_path}")

    # 尝试使用系统 PATH 中的 ffmpeg
    try:
        # 使用 'where' 命令查找可执行文件路径 (Windows)
        if os.name == 'nt':
             result = subprocess.run(["where", "ffmpeg"], capture_output=True, text=True, check=True)
             ffmpeg_path = result.stdout.strip().split('\n')[0] # 取第一个结果
             logger.info(f"在系统 PATH 中找到 ffmpeg: {ffmpeg_path}")
             return ffmpeg_path
        else: # For Linux/macOS
            result = subprocess.run(["which", "ffmpeg"], capture_output=True, text=True, check=True)
            ffmpeg_path = result.stdout.strip()
            logger.info(f"在系统 PATH 中找到 ffmpeg: {ffmpeg_path}")
            return ffmpeg_path

    except (FileNotFoundError, OSError, subprocess.CalledProcessError):
        logger.info("系统中未找到 ffmpeg")
        return None


def ensure_ffmpeg_or_raise():
    """
    校验 ffmpeg 是否可用，否则抛出异常并提示安装方式。
    """
    if check_ffmpeg_exists() is None:
        logger.error("未检测到 ffmpeg，请先安装后再使用本功能。")
        raise EnvironmentError(
            "❌ 未检测到 ffmpeg，请先安装后再使用本功能。\n"
            "👉 下载地址：https://ffmpeg.org/download.html\n"
            "🪟 Windows 推荐：https://www.gyan.dev/ffmpeg/builds/\n"
            "💡 如果你已安装，请将其路径写入 `.env` 文件，例如：\n"
            "FFMPEG_BIN_PATH=/your/custom/ffmpeg/bin/ffmpeg.exe"
        )