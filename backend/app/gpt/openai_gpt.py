from typing import List
from app.gpt.base import GPT
from openai import OpenAI
from app.gpt.prompt import BASE_PROMPT, AI_SUM, SCREENSHOT, LINK
from app.gpt.utils import fix_markdown
from app.models.gpt_model import GPTSource
from app.models.transcriber_model import TranscriptSegment
from datetime import timedelta


class OpenaiGPT(GPT):
    def __init__(self):
        from os import getenv
        self.api_key = getenv("OPENAI_API_KEY")
        self.base_url = getenv("OPENAI_API_BASE_URL")
        self.model=getenv('OPENAI_MODEL')
        print(self.model)
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        # 实例变量 screenshot 和 link 已移除

    def _format_time(self, seconds: float) -> str:
        return str(timedelta(seconds=int(seconds)))[2:]  # e.g., 03:15

    def _build_segment_text(self, segments: List[TranscriptSegment]) -> str:
        return "\n".join(
            f"{self._format_time(seg.start)} - {seg.text.strip()}"
            for seg in segments
        )

    def ensure_segments_type(self, segments) -> List[TranscriptSegment]:
        return [
            TranscriptSegment(**seg) if isinstance(seg, dict) else seg
            for seg in segments
        ]

    def create_messages(self, segments: List[TranscriptSegment], title: str, tags: str, screenshot: bool, link: bool):
        content = BASE_PROMPT.format(
            video_title=title,
            segment_text=self._build_segment_text(segments),
            tags=tags
        )
        # 根据传入的参数动态添加指令
        if link:
            print(":需要链接")
            content += LINK
        if screenshot:
            print(":需要截图")
            content += SCREENSHOT

        # 确保 AI_SUM 指令在最后添加
        content += AI_SUM

        print(content)
        return [{"role": "user", "content": content}]

    def summarize(self, source: GPTSource) -> str:
        # 直接将选项传递给 create_messages
        source.segment = self.ensure_segments_type(source.segment)
        messages = self.create_messages(
            segments=source.segment,
            title=source.title,
            tags=source.tags,
            screenshot=source.screenshot, # 传递 screenshot 选项
            link=source.link # 传递 link 选项
        )
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()


