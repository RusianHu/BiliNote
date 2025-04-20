import subprocess
import os
import uuid


def generate_screenshot(video_path: str, output_dir: str, timestamp: int, index: int) -> str:
    """
    使用 ffmpeg 生成截图，返回生成图片路径
    """
    os.makedirs(output_dir, exist_ok=True)
    ids=str(uuid.uuid4())
    output_path = os.path.join(output_dir, f"screenshot_{str(index)+ids}.jpg")

    command = [
        "ffmpeg",
        "-ss", str(timestamp),
        "-i", video_path,
        "-frames:v", "1",
        "-q:v", "2",  # 图像质量
        output_path,
        "-y"  # 覆盖
    ]

    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True, encoding='utf-8') # 使用 check=True 会在失败时自动抛出 CalledProcessError
        return output_path
    except subprocess.CalledProcessError as e:
        # 记录详细错误信息
        from app.utils.logger import get_logger
        logger = get_logger(__name__)
        logger.error(f"FFmpeg 截图失败: {e}")
        logger.error(f"FFmpeg 命令: {' '.join(e.cmd)}")
        logger.error(f"FFmpeg 返回码: {e.returncode}")
        logger.error(f"FFmpeg 标准错误输出:\n{e.stderr}")
        # 重新抛出异常，以便上层可以捕获
        raise RuntimeError(f"生成截图失败: {e.stderr}") from e
    except FileNotFoundError:
        # 如果 ffmpeg 命令本身都找不到
        from app.utils.logger import get_logger
        logger = get_logger(__name__)
        logger.error(f"FFmpeg 命令未找到，请确保 ffmpeg 已安装并配置在系统 PATH 中，或者检查 ffmpeg_helper.py 中的路径设置。")
        raise RuntimeError("FFmpeg 命令未找到")


