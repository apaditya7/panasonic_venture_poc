from fastapi import APIRouter
from api.machines import router as machines_router

router = APIRouter()
router.include_router(machines_router, tags=["machines"])

@router.get("/health")
async def health_check():
    return {"status": "healthy"}