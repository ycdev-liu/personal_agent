from fastapi import APIRouter, HTTPException
from app.api.schemas import ChatRequest, ChatResponse
from app.services.rag_service import rag_service
from app.services.memory_service import memory_service
from app.services.llm_service import llm_service
import logging
import json

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["聊天"])


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """聊天接口"""
    try:
        # 获取对话历史
        conversation_history = memory_service.get_conversation_history(
            request.user_id,
            limit=20
        )
        logger.info(conversation_history)
        # RAG 检索
        context = []
        sources = []
        if request.use_rag:
            try:
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
                logger.info("rag检索向量知识库")
                logger.info(sources)
            except Exception as e:
                logger.error(f"RAG 检索失败: {e}", exc_info=True)
                # RAG 失败时继续处理，但不使用 RAG 结果
                rag_results = []
                context = []
                sources = []
        
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
            logger.info("查询记忆")
            logger.info(memories_used)
        
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

@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """流式聊天接口"""
    async def generate():
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
                try:
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
                except Exception as e:
                    logger.error(f"RAG 检索失败: {e}", exc_info=True)
                    sources = []
            
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
            
            # 先发送元数据（sources 和 memories）
            metadata = {
                "type": "metadata",
                "sources": sources,
                "memories_used": memories_used
            }
            yield f"data: {json.dumps(metadata, ensure_ascii=False)}\n\n"
            
            # 流式生成回复
            full_response = ""
            for chunk in llm_service.stream_with_context(
                user_message=request.message,
                context=context,
                conversation_history=conversation_history,
                user_memories=user_memories
            ):
                full_response += chunk
                # 发送每个文本块
                data = {
                    "type": "chunk",
                    "content": chunk
                }
                yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
            
            # 发送完成信号
            done = {
                "type": "done"
            }
            yield f"data: {json.dumps(done, ensure_ascii=False)}\n\n"
            
            # 保存完整对话
            memory_service.save_conversation(
                user_id=request.user_id,
                user_message=request.message,
                assistant_message=full_response
            )
            
        except Exception as e:
            logger.error(f"流式聊天处理失败: {e}", exc_info=True)
            error_data = {
                "type": "error",
                "message": str(e)
            }
            yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # 禁用 Nginx 缓冲
        }
    )

        



