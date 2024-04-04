from fastapi import APIRouter

from .files_manager import router as fm_router
from .user import router as user_router


router = APIRouter()
router.include_router(
    router=fm_router,
    prefix='/files',
    tags=['Files']
)
router.include_router(
    router=user_router,
    prefix='/users',
    tags=['Users']
)
