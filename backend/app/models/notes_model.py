from dataclasses import dataclass
from typing import Optional, Dict

from app.models.audio_model import AudioDownloadResult
from app.models.transcriber_model import TranscriptResult


@dataclass
class NoteResult:
    markdown: str                  # GPT 总结的 Markdown 内容
    transcript: TranscriptResult                # Whisper 转写结果
    audio_meta: AudioDownloadResult  # 音频下载的元信息（title、duration、封面等）
    timings: Optional[Dict[str, float]] = None  # 各阶段耗时信息

@dataclass
class ErrorResult:
    error: str # 错误信息