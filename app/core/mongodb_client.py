from pymongo import MongoClient
from pymongo.database import Database
from typing import Optional
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class MongoDBClient:
    """MongoDB 客户端"""
    
    def __init__(self):
        self.uri = settings.mongodb_uri
        self.database_name = settings.mongodb_database
        self.client: Optional[MongoClient] = None
        self.db: Optional[Database] = None
        self._connect()
    
    def _connect(self):
        """连接 MongoDB"""
        try:
            self.client = MongoClient(self.uri)
            self.db = self.client[self.database_name]
            # 测试连接
            self.client.admin.command('ping')
            logger.info(f"已连接到 MongoDB: {self.database_name}")
        except Exception as e:
            logger.error(f"连接 MongoDB 失败: {e}")
            raise
    
    def get_collection(self, collection_name: str):
        """获取集合"""
        return self.db[collection_name]
    
    def close(self):
        """关闭连接"""
        if self.client:
            self.client.close()
            logger.info("MongoDB 连接已关闭")


# 全局 MongoDB 客户端实例
mongodb_client = MongoDBClient()

