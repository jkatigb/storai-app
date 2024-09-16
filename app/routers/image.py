from fastapi import APIRouter, HTTPException, Depends
from ..models import Scene
from ..services.llm_service import llm_service
from ..dependencies import get_current_user
from uuid import UUID

router = APIRouter(prefix="/image", tags=["image"])

@router.post("/generate-description")
async def generate_image_description(scene: Scene, story_parameters: dict, current_user: UUID = Depends(get_current_user)):
    try:
        task_id = await llm_service.queue_generate_image_description(current_user, scene, story_parameters)
        return {"task_id": task_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate")
async def generate_image(image_prompt: str, current_user: UUID = Depends(get_current_user)):
    try:
        task_id = await llm_service.queue_generate_image(current_user, image_prompt)
        return {"task_id": task_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))