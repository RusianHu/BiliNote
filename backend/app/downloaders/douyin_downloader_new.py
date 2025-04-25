import os
import re
import json
import time
import random
import urllib.parse
import execjs
import requests
import tempfile
from abc import ABC
from typing import Union, Optional, List, Dict, Tuple
from os import getenv

from app.downloaders.base import Downloader, DownloadQuality
from app.models.notes_model import AudioDownloadResult
from app.utils.path_helper import get_data_dir
from app.utils.logger import get_logger

logger = get_logger(__name__)

class DouyinConfig:
    """抖音API配置类"""
    HOST = 'https://www.douyin.com'
    
    # 通用请求参数
    COMMON_PARAMS = {
        'device_platform': 'webapp',
        'aid': '6383',
        'channel': 'channel_pc_web',
        'update_version_code': '170400',
        'pc_client_type': '1',  # Windows
        'version_code': '190500',
        'version_name': '19.5.0',
        'cookie_enabled': 'true',
        'screen_width': '1680',  # from cookie dy_swidth
        'screen_height': '1050',  # from cookie dy_sheight
        'browser_language': 'zh-CN',
        'browser_platform': 'Win32',
        'browser_name': 'Chrome',
        'browser_version': '126.0.0.0',
        'browser_online': 'true',
        'engine_name': 'Blink',
        'engine_version': '126.0.0.0',
        'os_name': 'Windows',
        'os_version': '10',
        'cpu_core_num': '8',  # device_web_cpu_core
        'device_memory': '8',  # device_web_memory_size
        'platform': 'PC',
        'downlink': '10',
        'effective_type': '4g',
        'round_trip_time': '50',
    }
    
    # 通用请求头
    COMMON_HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "sec-fetch-site": "same-origin",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
        "sec-ch-ua-platform": "Windows",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua": '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
        "referer": "https://www.douyin.com/?recommend=1",
        "priority": "u=1, i",
        "pragma": "no-cache",
        "cache-control": "no-cache",
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
        "accept": "application/json, text/plain, */*",
        "dnt": "1",
    }

class DouyinAPI:
    """抖音API封装类"""
    def __init__(self, cookie: str):
        self.cookie = cookie
        # 加载JavaScript签名文件
        js_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'js', 'douyin.js')
        try:
            with open(js_path, 'r', encoding='utf-8') as f:
                js_code = f.read()
            self.douyin_sign = execjs.compile(js_code)
            logger.info("成功加载抖音签名JS文件")
        except Exception as e:
            logger.error(f"加载抖音签名JS文件失败: {str(e)}")
            self.douyin_sign = None
    
    async def common_request(self, uri: str, params: dict) -> Tuple[dict, bool]:
        """通用请求方法"""
        url = f'{DouyinConfig.HOST}{uri}'
        
        # 合并通用参数
        params.update(DouyinConfig.COMMON_PARAMS)
        
        # 准备请求头
        headers = DouyinConfig.COMMON_HEADERS.copy()
        headers['Cookie'] = self.cookie
        
        # 处理参数
        params = await self._deal_params(params, headers)
        
        # 构建查询字符串
        query = '&'.join([f'{k}={urllib.parse.quote(str(v))}' for k, v in params.items()])
        
        # 根据URI选择签名方法
        call_name = 'sign_reply' if 'reply' in uri else 'sign_datail'
        
        # 生成签名
        if self.douyin_sign:
            params["a_bogus"] = self.douyin_sign.call(call_name, query, headers["User-Agent"])
        
        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()
            return data, data.get('status_code', -1) == 0
        except Exception as e:
            logger.error(f"请求失败: {str(e)}")
            return {}, False
    
    async def _deal_params(self, params: dict, headers: dict) -> dict:
        """处理请求参数"""
        cookie_dict = self._cookies_to_dict(headers.get('Cookie', ''))
        
        # 更新参数
        params.update({
            'msToken': self._get_ms_token(),
            'screen_width': cookie_dict.get('dy_swidth', 2560),
            'screen_height': cookie_dict.get('dy_sheight', 1440),
            'cpu_core_num': cookie_dict.get('device_web_cpu_core', 24),
            'device_memory': cookie_dict.get('device_web_memory_size', 8),
            'verifyFp': cookie_dict.get('s_v_web_id'),
            'fp': cookie_dict.get('s_v_web_id'),
            'webid': cookie_dict.get('ttwid', "7393173430232106534")
        })
        
        return params
    
    @staticmethod
    def _cookies_to_dict(cookie_string: str) -> dict:
        """将cookie字符串转换为字典"""
        return {
            cookie.split('=', 1)[0]: cookie.split('=', 1)[1]
            for cookie in cookie_string.split('; ')
            if cookie and cookie != 'douyin.com' and '=' in cookie
        }
    
    @staticmethod
    def _get_ms_token(length: int = 120) -> str:
        """生成随机msToken"""
        base_str = 'ABCDEFGHIGKLMNOPQRSTUVWXYZabcdefghigklmnopqrstuvwxyz0123456789='
        return ''.join(random.choice(base_str) for _ in range(length))
    
    async def get_video_info(self, video_url: str) -> Tuple[dict, bool]:
        """获取视频信息"""
        # 从URL中提取视频ID
        video_id = self._extract_video_id(video_url)
        if not video_id:
            logger.error(f"无法从URL中提取视频ID: {video_url}")
            return {}, False
        
        # 构建请求参数
        params = {
            "previous_page": "web_code_link",
            "aweme_id": video_id
        }
        
        # 发送请求
        return await self.common_request('/aweme/v1/web/aweme/detail/', params)
    
    def _extract_video_id(self, url: str) -> str:
        """从URL中提取视频ID"""
        # 处理短链接
        if 'v.douyin.com' in url:
            try:
                response = requests.head(url, allow_redirects=True)
                url = response.url
            except Exception as e:
                logger.error(f"解析短链接失败: {str(e)}")
                return ""
        
        # 从URL中提取视频ID
        patterns = [
            r'video/(\d+)',  # 标准URL格式
            r'aweme_id=(\d+)',  # 查询参数格式
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return ""

class DouyinDownloaderNew(Downloader, ABC):
    """抖音下载器类"""
    def __init__(self):
        super().__init__()
        self.cookies = getenv('DOUYIN_COOKIES')
        if not self.cookies:
            logger.warning("未配置抖音cookies，可能导致下载失败。请在.env文件中设置DOUYIN_COOKIES")
        self.api = DouyinAPI(self.cookies)
        self.download_record = set()  # 记录已下载的视频ID
    
    def _sanitize_filename(self, name: str, max_length: int = 50) -> str:
        """清理文件名"""
        # 移除非法字符
        name = re.sub(r'[\\/:*?"<>|]', '_', name)
        # 移除多余空格
        name = ' '.join(name.split())
        return name[:max_length]
    
    def _get_download_headers(self) -> dict:
        """获取下载用的请求头"""
        headers = DouyinConfig.COMMON_HEADERS.copy()
        headers.update({
            'Accept': '*/*',
            'Accept-Encoding': 'identity;q=1, *;q=0',
            'Range': 'bytes=0-',
            'Referer': 'https://www.douyin.com/',
            'Cookie': self.cookies
        })
        return headers
    
    async def download_media(self, url: str, output_path: str) -> bool:
        """下载媒体文件"""
        try:
            headers = self._get_download_headers()
            response = requests.get(url, headers=headers, stream=True)
            response.raise_for_status()
            
            # 确保目录存在
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            with open(output_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            logger.info(f"下载成功: {output_path}")
            return True
        except Exception as e:
            logger.error(f"下载失败: {str(e)}")
            return False
    
    async def download_internal(self, video_url: str, output_dir: str, is_audio: bool = True) -> Tuple[str, dict]:
        """内部下载方法"""
        # 获取视频信息
        data, success = await self.api.get_video_info(video_url)
        if not success:
            raise Exception(f"获取视频信息失败: {data}")
        
        # 提取视频信息
        aweme_detail = data.get('aweme_detail', {})
        video_id = aweme_detail.get('aweme_id', '')
        title = aweme_detail.get('desc', f'douyin_{video_id}')
        title = self._sanitize_filename(title)
        
        # 提取媒体URL
        if is_audio:
            # 获取音频URL
            music_info = aweme_detail.get('music', {})
            play_url = music_info.get('play_url', {})
            media_url = play_url.get('uri', '')
            if not media_url:
                media_urls = play_url.get('url_list', [])
                media_url = media_urls[0] if media_urls else ''
            
            # 如果没有音频URL，尝试从视频中提取
            if not media_url:
                video_info = aweme_detail.get('video', {})
                play_addr = video_info.get('play_addr', {})
                media_urls = play_addr.get('url_list', [])
                media_url = media_urls[0] if media_urls else ''
            
            # 设置输出文件路径
            file_ext = 'm4a'
            output_path = os.path.join(output_dir, f"{video_id}.{file_ext}")
        else:
            # 获取视频URL
            video_info = aweme_detail.get('video', {})
            play_addr = video_info.get('play_addr', {})
            media_urls = play_addr.get('url_list', [])
            media_url = media_urls[0] if media_urls else ''
            
            # 设置输出文件路径
            file_ext = 'mp4'
            output_path = os.path.join(output_dir, f"{video_id}.{file_ext}")
        
        if not media_url:
            raise Exception(f"无法获取{'音频' if is_audio else '视频'}URL")
        
        # 下载媒体
        success = await self.download_media(media_url, output_path)
        if not success:
            raise Exception(f"下载{'音频' if is_audio else '视频'}失败")
        
        # 提取其他信息
        duration = aweme_detail.get('duration', 0) // 1000  # 毫秒转秒
        cover_url = ''
        if 'cover' in aweme_detail:
            cover_urls = aweme_detail['cover'].get('url_list', [])
            cover_url = cover_urls[0] if cover_urls else ''
        
        # 返回结果
        info = {
            'title': title,
            'duration': duration,
            'cover_url': cover_url,
            'video_id': video_id,
            'tags': aweme_detail.get('text_extra', [])
        }
        
        return output_path, info
    
    async def download(
        self,
        video_url: str,
        output_dir: Union[str, None] = None,
        quality: DownloadQuality = "fast",
        need_video: Optional[bool] = False
    ) -> AudioDownloadResult:
        """下载音频"""
        if output_dir is None:
            output_dir = get_data_dir()
        
        os.makedirs(output_dir, exist_ok=True)
        
        try:
            # 下载音频
            audio_path, info = await self.download_internal(video_url, output_dir, is_audio=True)
            
            # 如果需要视频，也下载视频
            video_path = None
            if need_video:
                video_path, _ = await self.download_internal(video_url, output_dir, is_audio=False)
            
            return AudioDownloadResult(
                file_path=audio_path,
                title=info['title'],
                duration=info['duration'],
                cover_url=info['cover_url'],
                platform="douyin",
                video_id=info['video_id'],
                raw_info={'tags': info['tags']},
                video_path=video_path
            )
        except Exception as e:
            logger.error(f"下载抖音音频失败: {str(e)}")
            raise
    
    async def download_video(
        self,
        video_url: str,
        output_dir: Union[str, None] = None,
    ) -> str:
        """下载视频，返回视频文件路径"""
        if output_dir is None:
            output_dir = get_data_dir()
        
        os.makedirs(output_dir, exist_ok=True)
        
        try:
            # 下载视频
            video_path, _ = await self.download_internal(video_url, output_dir, is_audio=False)
            
            if not os.path.exists(video_path):
                raise FileNotFoundError(f"视频文件未找到: {video_path}")
            
            return video_path
        except Exception as e:
            logger.error(f"下载抖音视频失败: {str(e)}")
            raise
