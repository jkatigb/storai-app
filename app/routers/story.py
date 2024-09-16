from fastapi import APIRouter, HTTPException, Depends
from ..models import StoryParameters, StoryOutline, StoryRequest
from ..services.llm_service import llm_service
from ..dependencies import get_current_user
from uuid import UUID

router = APIRouter(prefix="/story", tags=["story"])

@router.post("/synopsis")
async def create_synopsis(request: StoryRequest, current_user: UUID = Depends(get_current_user)):
    try:
        task_id = await llm_service.queue_synopsis(current_user, request.parameters)
        return {"task_id": task_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/outline")
async def generate_outline(request: StoryRequest, current_user: UUID = Depends(get_current_user)):
    try:
        task_id = await llm_service.queue_outline(current_user, request.parameters)
        return {"task_id": task_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/enhance-outline")
async def enhance_outline(outline: StoryOutline, current_user: UUID = Depends(get_current_user)):
    try:
        task_id = await llm_service.queue_enhance_outline(current_user, outline)
        return {"task_id": task_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/develop-section")
async def develop_section(section_name: str, section_outline: dict, additional_context: dict, current_user: UUID = Depends(get_current_user)):
    try:
        task_id = await llm_service.queue_develop_section(current_user, section_name, section_outline, additional_context)
        return {"task_id": task_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/task/{task_id}")
async def get_task_status(task_id: UUID, current_user: UUID = Depends(get_current_user)):
    status = llm_service.get_task_status(task_id, current_user)
    if status is None:
        raise HTTPException(status_code=404, detail="Task not found or you don't have permission to access it")
    return {"status": status}

@router.get("/task/{task_id}/result")
async def get_task_result(task_id: UUID, current_user: UUID = Depends(get_current_user)):
    result = llm_service.get_task_result(task_id, current_user)
    if result is None:
        raise HTTPException(status_code=404, detail="Task result not found or you don't have permission to access it")
    return {"result": result}