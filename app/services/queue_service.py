from ..celery_app import (
    generate_synopsis,
    generate_outline,
    enhance_outline,
    develop_section,
    generate_image_description,
    generate_image
)
from ..models import QueuedTask
from uuid import UUID
from typing import Dict

class QueueService:
    def __init__(self):
        self.results: Dict[UUID, Dict] = {}

    async def add_task(self, task: QueuedTask) -> UUID:
        celery_task = None
        if task.task_type == "synopsis":
            celery_task = generate_synopsis.delay(str(task.user_id), task.parameters)
        elif task.task_type == "outline":
            celery_task = generate_outline.delay(str(task.user_id), task.parameters)
        elif task.task_type == "enhance_outline":
            celery_task = enhance_outline.delay(str(task.user_id), task.parameters)
        elif task.task_type == "develop_section":
            celery_task = develop_section.delay(str(task.user_id), task.parameters["section_name"], task.parameters["section_outline"], task.parameters["additional_context"])
        elif task.task_type == "generate_image_description":
            celery_task = generate_image_description.delay(str(task.user_id), task.parameters["scene"], task.parameters["story_parameters"])
        elif task.task_type == "generate_image":
            celery_task = generate_image.delay(str(task.user_id), task.parameters["image_prompt"])
        
        if celery_task:
            self.results[task.id] = {"user_id": task.user_id, "celery_task_id": celery_task.id}
            return task.id
        else:
            raise ValueError(f"Unknown task type: {task.task_type}")

    def get_task_status(self, task_id: UUID, user_id: UUID) -> str:
        if task_id in self.results and self.results[task_id]["user_id"] == user_id:
            celery_task_id = self.results[task_id]["celery_task_id"]
            celery_task = generate_synopsis.AsyncResult(celery_task_id)  # You can use any task here, they all have the same AsyncResult method
            return celery_task.status
        return None

    def get_task_result(self, task_id: UUID, user_id: UUID):
        if task_id in self.results and self.results[task_id]["user_id"] == user_id:
            celery_task_id = self.results[task_id]["celery_task_id"]
            celery_task = generate_synopsis.AsyncResult(celery_task_id)  # You can use any task here, they all have the same AsyncResult method
            if celery_task.ready():
                return celery_task.result
        return None

queue_service = QueueService()