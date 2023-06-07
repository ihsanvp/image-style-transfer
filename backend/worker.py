import os
from celery.utils.log import get_logger
import redis
import json
from model import generate_styled_image
from datetime import datetime
from celery import Celery
from torchvision.utils import save_image

redis_url = os.environ.get("REDIS_URL", "redis://127.0.0.1:6379/0")
worker = Celery(__name__, broker=redis_url, backend=redis_url)
logger = get_logger(__name__)

# Terminate all pending tasks
worker.control.purge()


@worker.task(name="dummy")
def dummy_task():
    folder = "/tmp/celery"
    os.makedirs(folder, exist_ok=True)
    now = datetime.now().strftime("%Y-%m-%dT%H:%M:%s")
    with open(f"{folder}/task-{now}.txt", "w") as f:
        f.write("hello!")


@worker.task(name="generate_image", bind=True)
def generate_image_task(
    self,
    content_img: str,
    style_img: str,
    output_path: str,
    lr: float,
    epochs: int,
    alpha: float,
    beta: float,
):
    r = redis.from_url(redis_url)

    def publish(total: int, completed: int):
        channel = f"task:{self.request.id}:progress"
        r.publish(channel, json.dumps({
            "total": total,
            "completed": completed
        }))

    total = epochs
    completed = 0

    publish(total=total, completed=completed)

    for epoch in generate_styled_image(
        content_img_path=content_img,
        style_img_path=style_img,
        output_path=output_path,
        lr=lr,
        epochs=epochs,
        alpha=alpha,
        beta=beta
    ):
        completed += 1
        publish(total=total, completed=completed)


