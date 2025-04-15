# app/tasks/note_tasks.py
import os
import json


from app.services.note import NoteGenerator
from app.core.celery_app import celery_app
from dataclasses import asdict
from app.enmus.note_enums import DownloadQuality
from app.utils.note_helper import save_note_to_file

NOTE_OUTPUT_DIR = "note_results"

@celery_app.task(name="generate_note_task")
def generate_note_task(task_id: str, video_url: str, platform: str, quality: str, link: bool = False, screenshot: bool = False):
    try:
        note = NoteGenerator().generate(
            video_url=video_url,
            platform=platform,
            quality=DownloadQuality(quality),
            task_id=task_id,
            link=link,
            screenshot=screenshot
        )
        save_note_to_file(task_id, note)
    except Exception as e:
        save_note_to_file(task_id, {"error": str(e)})
