# app/routers/note.py
import json
import os
import uuid
from typing import Optional

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, validator
from dataclasses import asdict

from app.db.video_task_dao import get_task_by_video
from app.enmus.note_enums import DownloadQuality
from app.services.note import NoteGenerator
from app.utils.response import ResponseWrapper as R
from app.utils.url_parser import extract_video_id
from app.validators.video_url_validator import is_supported_video_url
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import StreamingResponse
import httpx

# from app.services.downloader import download_raw_audio
# from app.services.whisperer import transcribe_audio
from app.tasks.note_tasks import generate_note_task
router = APIRouter()


class RecordRequest(BaseModel):
    video_id: str
    platform: str


class VideoRequest(BaseModel):
    video_url: str
    platform: str
    quality: DownloadQuality
    screenshot: Optional[bool] = False
    link: Optional[bool] = False

    @validator("video_url")
    def validate_supported_url(cls, v):
        url = str(v)
        # 支持平台校验
        if not is_supported_video_url(url):
            raise ValueError("暂不支持该视频平台或链接格式无效")
        return v


NOTE_OUTPUT_DIR = "note_results"





def run_note_task(task_id: str, video_url: str, platform: str, quality: DownloadQuality, link: bool = False,screenshot: bool = False):
    try:
        note = NoteGenerator().generate(
            video_url=video_url,
            platform=platform,
            quality=quality,
            task_id=task_id,
            link=link,
            screenshot=screenshot
        )
        print('Note 结果',note)
        save_note_to_file(task_id, note)
    except Exception as e:
        save_note_to_file(task_id, {"error": str(e)})


@router.post('/delete_task')
def delete_task(data:RecordRequest):
    try:

        NoteGenerator().delete_note(video_id=data.video_id,platform=data.platform)
        return R.success(msg='删除成功')
    except Exception as e:
        return R.error(msg=e)


@router.post("/generate_note")
def generate_note(data: VideoRequest, background_tasks: BackgroundTasks):
    try:

        video_id = extract_video_id(data.video_url, data.platform)
        if not video_id:
            raise HTTPException(status_code=400, detail="无法提取视频 ID")
        existing = get_task_by_video(video_id, data.platform)
        if existing:
            return R.error(
                msg='笔记已生成，请勿重复发起',

            )

        task_id = str(uuid.uuid4())

        generate_note_task.delay(
            task_id=task_id,
            video_url=data.video_url,
            platform=data.platform,
            quality=data.quality.value,
            link=data.link,
            screenshot=data.screenshot
        )
        return R.success({"task_id": task_id})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/task_status/{task_id}")
def get_task_status(task_id: str):
    path = os.path.join(NOTE_OUTPUT_DIR, f"{task_id}.json")
    if not os.path.exists(path):
        return R.success({"status": "PENDING"})

    with open(path, "r", encoding="utf-8") as f:
        content = json.load(f)

    if "error" in content:
        return R.error(content["error"], code=500)
    content['id'] = task_id
    return R.success({
        "status": "SUCCESS",
        "result": content
    })


@router.get("/image_proxy")
async def image_proxy(request: Request, url: str):
    headers = {
        "Referer": "https://www.bilibili.com/",  # 模拟B站来源
        "User-Agent": request.headers.get("User-Agent", ""),
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url, headers=headers)
            if resp.status_code != 200:
                raise HTTPException(status_code=resp.status_code, detail="图片获取失败")

            content_type = resp.headers.get("Content-Type", "image/jpeg")
            return StreamingResponse(resp.aiter_bytes(), media_type=content_type)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
