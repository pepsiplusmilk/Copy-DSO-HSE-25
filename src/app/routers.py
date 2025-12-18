from fastapi import APIRouter

from src.routers.boards import router as boards_router
from src.routers.ideas import router as ideas_router
from src.routers.users import router as users_router
from src.routers.votes import router as votes_router

router = APIRouter()
router.include_router(boards_router)
router.include_router(ideas_router)
router.include_router(users_router)
router.include_router(votes_router)
