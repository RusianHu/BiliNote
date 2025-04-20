from typing import List
from app.gpt.base import GPT
from openai import OpenAI
from app.gpt.prompt import BASE_PROMPT, AI_SUM, SCREENSHOT, LINK # 假设 OpenRouter 也支持这些提示
from app.models.gpt_model import GPTSource
from app.models.transcriber_model import TranscriptSegment
from datetime import timedelta
import os

class OpenRouterGPT(GPT):
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.model = os.getenv("OPENROUTER_MODEL") # 例如 "openai/gpt-4o", "google/gemini-pro" 等
        self.base_url = "https://openrouter.ai/api/v1"
        # 可选：从环境变量读取站点信息，用于 OpenRouter 排行榜
        self.site_url = os.getenv("OPENROUTER_SITE_URL", "") # 你的网站 URL
        self.site_name = os.getenv("OPENROUTER_SITE_NAME", "") # 你的网站名称

        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable not set.")
        if not self.model:
            raise ValueError("OPENROUTER_MODEL environment variable not set.")

        print(f"Initializing OpenRouterGPT with model: {self.model}")
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        self.screenshot = False
        self.link = False # 根据需要决定是否默认启用链接

    def _format_time(self, seconds: float) -> str:
        """将秒数格式化为 mm:ss"""
        return str(timedelta(seconds=int(seconds)))[2:]

    def _build_segment_text(self, segments: List[TranscriptSegment]) -> str:
        """构建用于提示的转录片段文本"""
        return "\n".join(
            f"{self._format_time(seg.start)} - {seg.text.strip()}"
            for seg in segments
        )

    def ensure_segments_type(self, segments) -> List[TranscriptSegment]:
        """确保 segments 列表中的元素是 TranscriptSegment 类型"""
        return [
            TranscriptSegment(**seg) if isinstance(seg, dict) else seg
            for seg in segments
        ]

    def create_messages(self, segments: List[TranscriptSegment], title: str, tags: str):
        """创建发送给 GPT API 的消息列表"""
        content = BASE_PROMPT.format(
            video_title=title,
            segment_text=self._build_segment_text(segments),
            tags=tags
        )
        if self.screenshot:
            print(":需要截图")
            content += SCREENSHOT
        if self.link:
            print(":需要链接")
            content += LINK
        # print(content) # 调试时可以取消注释
        return [{"role": "user", "content": content + AI_SUM}]

    def summarize(self, source: GPTSource) -> str:
        """
        使用 OpenRouter API 生成视频摘要。

        :param source: 包含视频标题、标签、转录片段等信息的 GPTSource 对象。
        :return: 生成的 Markdown 格式笔记。
        """
        self.screenshot = source.screenshot
        self.link = source.link
        source.segment = self.ensure_segments_type(source.segment)
        messages = self.create_messages(source.segment, source.title, source.tags)

        extra_headers = {}
        if self.site_url:
            extra_headers["HTTP-Referer"] = self.site_url
        if self.site_name:
            extra_headers["X-Title"] = self.site_name

        try:
            print("--- Calling OpenRouter API ---")
            print(f"Model: {self.model}")
            # print(f"Messages: {messages}") # 消息内容可能很长，调试时按需开启
            print(f"Extra Headers: {extra_headers}")

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                extra_headers=extra_headers if extra_headers else None
            )

            print("--- OpenRouter API Response ---")
            print(response) # 打印完整的响应对象以供调试

            # 添加健壮性检查
            if response and response.choices and len(response.choices) > 0:
                choice = response.choices[0]
                if choice and choice.message and choice.message.content:
                    summary = choice.message.content.strip()
                    print("--- Summary Extracted ---")
                    # print(summary) # 摘要内容可能很长
                    # OpenRouter 返回的内容可能不需要 unicode_escape 解码，先注释掉
                    # from app.gpt.utils import fix_markdown
                    # return fix_markdown(summary)
                    return summary
                else:
                    error_msg = "OpenRouter response structure invalid: message or content missing."
                    print(f"Error: {error_msg}")
                    print(f"Choice object: {choice}")
                    return f"Error generating summary with OpenRouter: {error_msg}"
            else:
                error_msg = "OpenRouter response structure invalid: choices missing or empty."
                print(f"Error: {error_msg}")
                print(f"Response object: {response}")
                return f"Error generating summary with OpenRouter: {error_msg}"

        except Exception as e:
            # 打印更详细的异常信息，包括类型
            import traceback
            print(f"Error calling OpenRouter API: {type(e).__name__}: {e}")
            traceback.print_exc() # 打印完整的堆栈跟踪
            return f"Error generating summary with OpenRouter: {type(e).__name__}: {e}"