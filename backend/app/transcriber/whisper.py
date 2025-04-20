from faster_whisper import WhisperModel

from app.decorators.timeit import timeit
from app.models.transcriber_model import TranscriptSegment, TranscriptResult
from app.transcriber.base import Transcriber
from app.utils.env_checker import is_cuda_available, is_torch_installed
from app.utils.logger import get_logger
from app.utils.path_helper import get_model_dir

from events import transcription_finished
from pathlib import Path
import os
from tqdm import tqdm
from huggingface_hub import snapshot_download

'''
 Size of the model to use (tiny, tiny.en, base, base.en, small, small.en, distil-small.en, medium, medium.en, distil-medium.en, large-v1, large-v2, large-v3, large, distil-large-v2, distil-large-v3, large-v3-turbo, or turbo
'''
logger=get_logger(__name__)

class WhisperTranscriber(Transcriber):
    # TODO:修改为可配置
    def __init__(
            self,
            model_size: str = "base",
            device: str = 'cpu',
            compute_type: str = None,
            cpu_threads: int = 1,
    ):
        if device == 'cpu' or device is None:
            self.device = 'cpu'
        else:
            self.device = "cuda" if self.is_cuda() else "cpu"
            if device == 'cuda' and self.device == 'cpu':
                print('没有 cuda 使用 cpu进行计算')

        self.compute_type = compute_type or ("float16" if self.device == "cuda" else "int8")

        # 直接使用项目根目录下的 backend/models/whisper-{model_size} 目录
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
        custom_model_path = os.path.join(project_root, "backend", "models", f"whisper-{model_size}")

        # 打印路径信息便于调试
        logger.info(f"Project root: {project_root}")
        logger.info(f"Custom model path: {custom_model_path}")
        logger.info(f"Custom model path exists: {Path(custom_model_path).exists()}")
        if Path(custom_model_path).exists():
            logger.info(f"Custom model path contents: {list(Path(custom_model_path).iterdir())}")

        # 然后检查默认的模型目录
        model_dir = get_model_dir("whisper")
        model_path = os.path.join(model_dir, f"whisper-{model_size}")

        # 打印默认模型路径信息
        logger.info(f"Default model dir: {model_dir}")
        logger.info(f"Default model path: {model_path}")
        logger.info(f"Default model path exists: {Path(model_path).exists()}")
        if Path(model_path).exists():
            logger.info(f"Default model path contents: {list(Path(model_path).iterdir())}")

        # 如果项目根目录下存在模型，使用该目录
        if Path(custom_model_path).exists() and os.path.isfile(os.path.join(custom_model_path, "model.bin")):
            logger.info(f"使用项目根目录下的模型: {custom_model_path}")
            model_path = custom_model_path
        # 如果默认目录下不存在模型，尝试下载
        elif not Path(model_path).exists() or not os.path.isfile(os.path.join(model_path, "model.bin")):
            logger.info(f"模型 whisper-{model_size} 不存在，开始下载...")
            try:
                repo_id = f"guillaumekln/faster-whisper-{model_size}"
                snapshot_download(
                    repo_id,
                    local_dir=model_path,
                    local_dir_use_symlinks=False,
                )
                logger.info("模型下载完成")
            except Exception as e:
                logger.error(f"模型下载失败: {e}")
                raise

        self.model = WhisperModel(
            model_size,
            device=self.device,
            compute_type=self.compute_type,
            cpu_threads=cpu_threads,
            download_root=model_dir
        )
    @staticmethod
    def is_torch_installed() -> bool:
        try:
            import torch
            return True
        except ImportError:
            return False

    @staticmethod
    def is_cuda() -> bool:
        try:
            if is_cuda_available():
                print("✅ CUDA 可用，使用 GPU")
                return True
            elif is_torch_installed():
                print("⚠️ 只装了 torch，但没有 CUDA，用 CPU")
                return False
            else:
                print("❌ 还没有安装 torch，请先安装")
                return False

        except ImportError:
            return False

    @timeit
    def transcript(self, file_path: str) -> TranscriptResult:
        try:

            segments_raw, info = self.model.transcribe(file_path)

            segments = []
            full_text = ""

            for seg in segments_raw:
                text = seg.text.strip()
                full_text += text + " "
                segments.append(TranscriptSegment(
                    start=seg.start,
                    end=seg.end,
                    text=text
                ))

            result= TranscriptResult(
                language=info.language,
                full_text=full_text.strip(),
                segments=segments,
                raw=info
            )
            self.on_finish(file_path, result)
            return result
        except Exception as e:
            print(f"转写失败：{e}")


    def on_finish(self,video_path:str,result: TranscriptResult)->None:
        print("转写完成")
        transcription_finished.send({
            "file_path": video_path,
        })

