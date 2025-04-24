import re
import httpx
from typing import Optional


def extract_video_id(url: str, platform: str) -> Optional[str]:
    """
    从视频链接中提取视频 ID

    :param url: 视频链接
    :param platform: 平台名（bilibili / youtube / douyin）
    :return: 提取到的视频 ID 或 None
    """
    if platform == "bilibili":
        # 匹配 BV号（如 BV1vc411b7Wa）
        match = re.search(r"BV([0-9A-Za-z]+)", url)
        return f"BV{match.group(1)}" if match else None

    elif platform == "youtube":
        # 匹配 v=xxxxx 或 youtu.be/xxxxx，ID 长度通常为 11
        match = re.search(r"(?:v=|youtu\.be/)([0-9A-Za-z_-]{11})", url)
        return match.group(1) if match else None

    elif platform == "douyin":
        # 匹配 douyin.com/video/1234567890123456789
        match = re.search(r"/video/(\d+)", url)
        if match:
            return match.group(1)

        # 处理抖音短链接 (如 v.douyin.com/xxx/)
        if "v.douyin.com" in url:
            try:
                # 发送请求并跟随重定向
                response = httpx.get(url, follow_redirects=True)
                # 从最终URL中提取视频ID
                final_url = str(response.url)
                match = re.search(r"/video/(\d+)", final_url)
                return match.group(1) if match else None
            except Exception as e:
                print(f"解析抖音短链接出错: {e}")
                return None

    return None
