from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.customer_request import router as support_router

router = APIRouter()

router.include_router(auth_router)
router.include_router(support_router)
