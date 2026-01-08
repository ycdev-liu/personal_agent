from fastapi import APIRouter
from app.api.routers import chat, documents, memories, health

# 创建主路由器
router = APIRouter()

# 注册各个业务模块的路由
router.include_router(chat.router)
router.include_router(documents.router)
router.include_router(memories.router)
router.include_router(health.router)