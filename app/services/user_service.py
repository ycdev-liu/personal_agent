from typing import List,Dict,Optional

from datetime import datetime

from bson import ObjectId
from app.core.mongodb_client import mongodb_client
import logging

# logging.basicConfig(
#     level=logging.INFO
# )

logger = logging.getLogger(__name__)




class UserService:
    """用户管理服务"""
    
    def __init__(self):
        self.user_collection = mongodb_client.get_collection("users")
        self.conversation_collection = mongodb_client.get_collection("conversations")
    
    def create_user(self, name: str, description: Optional[str] = None) -> Dict:
        """创建新用户"""
        user = {
            "name": name,
            "description": description or "",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = self.user_collection.insert_one(user)
        user["_id"] = result.inserted_id
        logger.info(f"创建新用户: {name} (ID: {result.inserted_id})")
        
        return {
            "id": str(user["_id"]),
            "name": user["name"],
            "description": user["description"],
            "created_at": user["created_at"],
            "conversation_count": 0
        }
    
    def get_user(self, user_id: str) -> Optional[Dict]:
        """获取用户信息"""
        try:
            user = self.user_collection.find_one({"_id": ObjectId(user_id)})
            if not user:
                return None
            
            # 统计对话数量
            conversation_count = self.conversation_collection.count_documents(
                {"user_id": user_id}
            )
            
            return {
                "id": str(user["_id"]),
                "name": user["name"],
                "description": user.get("description", ""),
                "created_at": user["created_at"],
                "conversation_count": conversation_count
            }
        except Exception as e:
            logger.error(f"获取用户失败: {e}")
            return None
    
    def list_users(self, limit: int = 100) -> List[Dict]:
        """获取用户列表"""
        users = list(self.user_collection.find().sort("created_at", -1).limit(limit))
        
        result = []
        for user in users:
            conversation_count = self.conversation_collection.count_documents(
                {"user_id": str(user["_id"])}
            )
            result.append({
                "id": str(user["_id"]),
                "name": user["name"],
                "description": user.get("description", ""),
                "created_at": user["created_at"],
                "conversation_count": conversation_count
            })
        
        return result
    
    def delete_user(self, user_id: str) -> bool:
        """删除用户及其所有对话"""
        try:
            # 删除用户的所有对话
            self.conversation_collection.delete_many({"user_id": user_id})
            
            # 删除用户
            result = self.user_collection.delete_one({"_id": ObjectId(user_id)})
            
            if result.deleted_count > 0:
                logger.info(f"已删除用户: {user_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"删除用户失败: {e}")
            return False
    
    def create_conversation(self, user_id: str, title: Optional[str] = None) -> Dict:
        """创建新对话"""
        # 验证用户是否存在
        user = self.get_user(user_id)
        if not user:
            raise ValueError(f"用户不存在: {user_id}")
        
        # 如果没有提供标题，使用默认标题
        if not title:
            conversation_count = self.conversation_collection.count_documents(
                {"user_id": user_id}
            )
            title = f"对话 {conversation_count + 1}"
        
        conversation = {
            "user_id": user_id,
            "title": title,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "message_count": 0
        }
        
        result = self.conversation_collection.insert_one(conversation)
        conversation["_id"] = result.inserted_id
        logger.info(f"创建新对话: {title} (用户: {user_id})")
        
        return {
            "id": str(conversation["_id"]),
            "user_id": conversation["user_id"],
            "title": conversation["title"],
            "created_at": conversation["created_at"],
            "updated_at": conversation["updated_at"],
            "message_count": 0
        }
    
    def get_conversation(self, conversation_id: str) -> Optional[Dict]:
        """获取对话信息"""
        try:
            conversation = self.conversation_collection.find_one(
                {"_id": ObjectId(conversation_id)}
            )
            if not conversation:
                return None
            
            return {
                "id": str(conversation["_id"]),
                "user_id": conversation["user_id"],
                "title": conversation["title"],
                "created_at": conversation["created_at"],
                "updated_at": conversation["updated_at"],
                "message_count": conversation.get("message_count", 0)
            }
        except Exception as e:
            logger.error(f"获取对话失败: {e}")
            return None
    
    def list_conversations(self, user_id: str, limit: int = 100) -> List[Dict]:
        """获取用户的对话列表"""
        conversations = list(
            self.conversation_collection.find({"user_id": user_id})
            .sort("updated_at", -1)
            .limit(limit)
        )
        
        result = []
        for conv in conversations:
            result.append({
                "id": str(conv["_id"]),
                "user_id": conv["user_id"],
                "title": conv["title"],
                "created_at": conv["created_at"],
                "updated_at": conv["updated_at"],
                "message_count": conv.get("message_count", 0)
            })
        
        return result
    
    def delete_conversation(self, conversation_id: str) -> bool:
        """删除对话"""
        try:
            result = self.conversation_collection.delete_one(
                {"_id": ObjectId(conversation_id)}
            )
            
            if result.deleted_count > 0:
                logger.info(f"已删除对话: {conversation_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"删除对话失败: {e}")
            return False
    
    def update_conversation_title(self, conversation_id: str, title: str) -> bool:
        """更新对话标题"""
        try:
            result = self.conversation_collection.update_one(
                {"_id": ObjectId(conversation_id)},
                {"$set": {"title": title, "updated_at": datetime.utcnow()}}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"更新对话标题失败: {e}")
            return False


# 全局用户服务实例
user_service = UserService()