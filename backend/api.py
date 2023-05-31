from fastapi import FastAPI, UploadFile, WebSocket
from celery import uuid
import settings
import os
import aioredis
import shutil
from fastapi import UploadFile
import os
from worker import generate_image_task, dummy_task


async def save_file(file: UploadFile):
    file_name, file_ext = os.path.splitext(file.filename)  # type: ignore
    file_id = uuid()
    file_path = os.path.join(settings.UPLOADS_DIR, f"{file_id}{file_ext}")

    data = await file.read()
    with open(file_path, "wb") as f:
        f.write(data)

    return file_path


shutil.rmtree(settings.UPLOADS_DIR, ignore_errors=True)
shutil.rmtree(settings.OUTPUTS_DIR, ignore_errors=True)
os.makedirs(settings.UPLOADS_DIR, exist_ok=True)
os.makedirs(settings.OUTPUTS_DIR, exist_ok=True)

app = FastAPI()


@app.get("/")
async def index():
    return {
        "name": "NST",
        "version": "1.0.0",
    }


@app.post("/generate", status_code=201)
async def generate(content_img: UploadFile, style_img: UploadFile):
    task_id = uuid()
    content_image_path = await save_file(content_img)
    style_image_path = await save_file(style_img)
    output_image_path = os.path.join(settings.OUTPUTS_DIR, f"{task_id}.jpg")

    task = generate_image_task.apply_async(task_id=task_id, kwargs={
        "content_img": content_image_path,
        "style_img": style_image_path,
        "output_path": output_image_path,
        "lr": settings.LR,
        "epochs": settings.EPOCHS,
        "alpha": settings.ALPHA,
        "beta": settings.BETA
    })

    return {
        "id": task.id
    }


@app.websocket("/status/{task_id}")
async def task_status(task_id: str, websocket: WebSocket):
    await websocket.accept()

    channel = f"task:{task_id}:progress"
    redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    redis = await aioredis.from_url(redis_url)
    psub = redis.pubsub()

    async with psub as p:
        await p.subscribe(channel)
        try:
            while True:
                message = await psub.get_message(ignore_subscribe_messages=True)
                if message:
                    await websocket.send_json(str(message.get("data", ""), "UTF-8"))
        except Exception as exc:
            print(exc)
