from typing import List, Dict, Optional
from datetime import datetime
from app.core.mongodb_client import mongodb_client
from app.services.embedding_service import embedding_service
import numpy as np
import logging

logger = logging.getLogger(__name__)


class MemoryService:
    """用户记忆服务"""
    
    def __init__(self):
        self.memory_collection = mongodb_client.get_collection("user_memories")
        self.conversation_collection = mongodb_client.get_collection("conversation_history")
    
    def save_conversation(
        self,
        user_id: str,
        user_message: str,
        assistant_message: str,
        metadata: Optional[dict] = None
    ):
        """保存对话记录"""
        conversation = {
            "user_id": user_id,
            "user_message": user_message,
            "assistant_message": assistant_message,
            "timestamp": datetime.utcnow(),
            "metadata": metadata or {}
        }
        
        self.conversation_collection.insert_one(conversation)
        logger.info(f"已保存用户 {user_id} 的对话记录")
    
    def get_conversation_history(
        self,
        user_id: str,
        limit: int = 20
    ) -> List[dict]:
        """获取对话历史"""
        conversations = list(self.conversation_collection.find(
            {"user_id": user_id}
        ).sort("timestamp", -1).limit(limit))
        
        # 将对话转换为消息格式
        messages = []
        for conv in reversed(conversations):
            messages.append({
                "role": "user",
                "content": conv["user_message"],
                "timestamp": conv["timestamp"]
            })
            messages.append({
                "role": "assistant",
                "content": conv["assistant_message"],
                "timestamp": conv["timestamp"]
            })
        
        return messages
    
    def save_memory(
        self,
        user_id: str,
        content: str,
        memory_type: str = "fact",
        importance: float = 0.5,
        metadata: Optional[dict] = None
    ):
        """保存用户记忆"""
        # 生成记忆向量用于相似度检索
        vector = embedding_service.encode_single(content)
        
        memory = {
            "user_id": user_id,
            "content": content,
            "memory_type": memory_type,  # fact, preference, event, etc.
            "importance": importance,
            "vector": vector,
            "timestamp": datetime.utcnow(),
            "metadata": metadata or {}
        }
        
        self.memory_collection.insert_one(memory)
        logger.info(f"已保存用户 {user_id} 的记忆: {memory_type}")
    
    def get_relevant_memories(
        self,
        user_id: str,
        query: str,
        top_k: int = 5
    ) -> List[dict]:
        """检索相关记忆"""
        query_vector = embedding_service.encode_single(query)
        
        # 获取用户的所有记忆
        memories = list(self.memory_collection.find({"user_id": user_id}))
        
        # 计算向量相似度（余弦相似度）
        scored_memories = []
        for memory in memories:
            if "vector" not in memory:
                continue
            
            # 计算余弦相似度
            vec1 = np.array(query_vector)
            vec2 = np.array(memory["vector"])
            
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                score = 0.0
            else:
                score = dot_product / (norm1 * norm2)
            
            scored_memories.append({
                **memory,
                "score": float(score)
            })
        
        # 按分数和重要性排序
        scored_memories.sort(
            key=lambda x: (x["score"], x.get("importance", 0)),
            reverse=True
        )
        
        return scored_memories[:top_k]


# 全局记忆服务实例
memory_service = MemoryService()

