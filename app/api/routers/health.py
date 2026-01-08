from fastapi import APIRouter,HTTPException
from app.services.rag_service import rag_service
import logging


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1",tags=["健康检查"])

@router.get("/health")
async def health():
    """健康检查"""
    try:
        milvus_status = rag_service.milvus_client.get_stats()
        return {
            "status":"healthy",
            "milvus":milvus_status,
            "mongodb":"connected"
        }
    except Exception as e:
        logger.error(f"健康检查失败: {e}",exc_info=True)
        return {"status":"unhealthy","error":str(e)}