import os
from abc import ABC
from typing import Union, Optional

import yt_dlp

from app.downloaders.base import Downloader, DownloadQuality
from app.models.notes_model import AudioDownloadResult
from app.utils.logger import get_logger
from app.utils.path_helper import get_data_dir

logger=get_logger(__name__)
class YoutubeDownloader(Downloader, ABC):
    def __init__(self):

        super().__init__()

    def download(
        self,
        video_url: str,
        output_dir: Union[str, None] = None,
        quality: DownloadQuality = "fast",
        need_video:Optional[bool]=False
    ) -> AudioDownloadResult:
        if output_dir is None:
            output_dir = get_data_dir()
        if not output_dir:
            output_dir=self.cache_data
        os.makedirs(output_dir, exist_ok=True)

        output_path = os.path.join(output_dir, "%(id)s.%(ext)s")

        ydl_opts = {
            'format': 'best[ext=mp4][height<=720]/best[height<=720]/best',
            'outtmpl': output_path,
            'noplaylist': True,
            'quiet': False,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            video_id = info.get("id")
            title = info.get("title")
            duration = info.get("duration", 0)
            cover_url = info.get("thumbnail")
            audio_path = os.path.join(output_dir, f"{video_id}.m4a")

        return AudioDownloadResult(
            file_path=audio_path,
            title=title,
            duration=duration,
            cover_url=cover_url,
            platform="youtube",
            video_id=video_id,
            raw_info={'tags':info.get('tags')}, #全部返回会报错
            video_path=None  # ❗音频下载不包含视频路径
        )

    def download_video(
            self,
            video_url: str,
            output_dir: Union[str, None] = None,
            quality: DownloadQuality = "medium",
    ) -> str:
        if output_dir is None:
            output_dir = get_data_dir()

        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, "%(id)s.%(ext)s")

        format_map = {
            "fast": "best[height<=480]",
            "medium": "best[height<=720]",
            "slow": "bestvideo+bestaudio/best"
        }
        preferred_format = format_map.get(quality, "best[height<=720]")

        # ⛑️ 多级格式容错 fallback
        fallback_formats = [
            preferred_format,
            "best[ext=mp4]",
            "bestvideo+bestaudio",
            "best"
        ]

        last_error = None
        for fmt in fallback_formats:
            ydl_opts = {
                'format': fmt,
                'outtmpl': output_path,
                'noplaylist': True,
                'quiet': False,
                'merge_output_format': 'mp4',
            }

            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(video_url, download=True)
                    video_id = info.get("id")
                    video_path = os.path.join(output_dir, f"{video_id}.mp4")
                    if os.path.exists(video_path):
                        return video_path
            except yt_dlp.utils.DownloadError as e:
                logger.warning(f"⚠️ 尝试格式失败：{fmt}")
                last_error = e
                continue

        raise last_error or Exception("未能成功下载视频")
