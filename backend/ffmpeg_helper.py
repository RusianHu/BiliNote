import os
import subprocess
from dotenv import load_dotenv

from app.utils.logger import get_logger
logger = get_logger(__name__)

load_dotenv()
def check_ffmpeg_exists() -> bool:
    """
    检查 ffmpeg 是否可用。优先使用 FFMPEG_BIN_PATH 环境变量指定的路径。
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
                logger.info("ffmpeg 已安装")
                return True
            except (FileNotFoundError, OSError, subprocess.CalledProcessError):
                logger.info("指定的 ffmpeg 可执行文件无法运行")
        # 检查是否是目录路径
        elif os.path.isdir(ffmpeg_bin_path):
            # 将目录添加到 PATH 环境变量
            os.environ["PATH"] = ffmpeg_bin_path + os.pathsep + os.environ.get("PATH", "")
            logger.info(f"添加 ffmpeg 目录到 PATH: {os.environ.get('PATH')}")
        else:
            logger.info(f"指定的 ffmpeg 路径无效: {ffmpeg_bin_path}")

    # 尝试使用系统 PATH 中的 ffmpeg
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        logger.info("系统 PATH 中的 ffmpeg 已安装")
        return True
    except (FileNotFoundError, OSError, subprocess.CalledProcessError):
        logger.info("系统中未找到 ffmpeg")
        return False


def ensure_ffmpeg_or_raise():
    """
    校验 ffmpeg 是否可用，否则抛出异常并提示安装方式。
    """
    if not check_ffmpeg_exists():
        logger.error("未检测到 ffmpeg，请先安装后再使用本功能。")
        raise EnvironmentError(
            "❌ 未检测到 ffmpeg，请先安装后再使用本功能。\n"
            "👉 下载地址：https://ffmpeg.org/download.html\n"
            "🪟 Windows 推荐：https://www.gyan.dev/ffmpeg/builds/\n"
            "💡 如果你已安装，请将其路径写入 `.env` 文件，例如：\n"
            "FFMPEG_BIN_PATH=/your/custom/ffmpeg/bin"
        )