from fastapi import APIRouter, HTTPException
from app.api.schemas import MemoryAddRequest
from app.services.memory_service import memory_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["记忆管理"])


@router.post("/memories")
async def add_memory(request: MemoryAddRequest):
    """添加用户记忆"""
    try:
        memory_service.save_memory(
            user_id=request.user_id,
            content=request.content,
            memory_type=request.memory_type,
            importance=request.importance
        )
        return {"success": True, "message": "记忆保存成功"}
    except Exception as e:
        logger.error(f"保存记忆失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/memories/{user_id}")
async def get_memories(user_id: str):
    """获取用户记忆"""
    try:
        memories = memory_service.get_relevant_memories(user_id, "", top_k=50)
        return {
            "success": True,
            "memories": [
                {
                    "id": str(m["_id"]),
                    "content": m["content"],
                    "type": m["memory_type"],
                    "importance": m["importance"],
                    "timestamp": m.get("timestamp")
                }
                for m in memories
            ]
        }
    except Exception as e:
        logger.error(f"获取记忆失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/memories/{user_id}/{memory_id}")
async def delete_memory(user_id: str, memory_id: str):
    """删除用户记忆"""
    try:
        logger.info(f"删除记忆: user_id={user_id}, memory_id={memory_id}")

        result = memory_service.delete_memory(user_id, memory_id)
        
        if result == False:
            raise HTTPException(status_code=404, detail="记忆不存在")

        return {"success": True, "message": "记忆删除成功"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除记忆失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))