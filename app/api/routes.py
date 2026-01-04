from fastapi import APIRouter, HTTPException
from typing import List
from app.api.schemas import (
    ChatRequest, ChatResponse,
    DocumentAddRequest, DocumentAddResponse,
    MemoryAddRequest
)
from app.services.rag_service import rag_service
from app.services.memory_service import memory_service
from app.services.llm_service import llm_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["智能助手"])


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """聊天接口"""
    try:
        # 获取对话历史
        conversation_history = memory_service.get_conversation_history(
            request.user_id,
            limit=20
        )
        
        # RAG 检索
        context = []
        sources = []
        if request.use_rag:
            rag_results = rag_service.search(request.message)
            context = [r["text"] for r in rag_results]
            sources = [
                {
                    "text": r["text"],
                    "score": r["score"],
                    "metadata": r.get("metadata", {})
                }
                for r in rag_results
            ]
        
        # 获取相关记忆
        memories_used = []
        user_memories = []
        if request.use_memory:
            memories = memory_service.get_relevant_memories(
                request.user_id,
                request.message,
                top_k=5
            )
            memories_used = [
                {
                    "content": m["content"],
                    "type": m["memory_type"],
                    "importance": m["importance"]
                }
                for m in memories
            ]
            user_memories = memories
        
        # 生成回复
        response_text = llm_service.generate_with_context(
            user_message=request.message,
            context=context,
            conversation_history=conversation_history,
            user_memories=user_memories
        )
        
        # 保存对话
        memory_service.save_conversation(
            user_id=request.user_id,
            user_message=request.message,
            assistant_message=response_text
        )
        
        return ChatResponse(
            response=response_text,
            sources=sources,
            memories_used=memories_used
        )
    
    except Exception as e:
        logger.error(f"聊天处理失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/documents", response_model=DocumentAddResponse)
async def add_documents(request: DocumentAddRequest):
    """添加文档到知识库"""
    try:
        metadatas = request.metadatas or [{}] * len(request.texts)
        rag_service.add_documents(request.texts, metadatas)
        
        return DocumentAddResponse(
            success=True,
            message="文档添加成功",
            count=len(request.texts)
        )
    except Exception as e:
        logger.error(f"添加文档失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


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


@router.get("/health")
async def health_check():
    """健康检查"""
    try:
        return {
            "status": "healthy",
            "milvus": rag_service.milvus_client.get_stats(),
            "mongodb": "connected"
        }
    except Exception as e:
        logger.error(f"健康检查失败: {e}", exc_info=True)
        return {
            "status": "unhealthy",
            "error": str(e)
        }

