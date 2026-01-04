from pymilvus import (
    connections,
    Collection,
    FieldSchema,
    CollectionSchema,
    DataType,
    utility
)
from typing import List, Optional
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class MilvusClient:
    """Milvus 向量数据库客户端"""
    
    def __init__(self):
        self.host = settings.milvus_host
        self.port = settings.milvus_port
        self.collection_name = settings.milvus_collection_name
        self.dimension = settings.milvus_dimension
        self.collection: Optional[Collection] = None
        self._connect()
        self._ensure_collection()
    
    def _connect(self):
        """连接 Milvus"""
        try:
            connections.connect(
                alias="default",
                host=self.host,
                port=self.port
            )
            logger.info(f"已连接到 Milvus: {self.host}:{self.port}")
        except Exception as e:
            logger.error(f"连接 Milvus 失败: {e}")
            raise
    
    def _ensure_collection(self):
        """确保集合存在，不存在则创建"""
        if utility.has_collection(self.collection_name):
            self.collection = Collection(self.collection_name)
            logger.info(f"集合 '{self.collection_name}' 已存在")
        else:
            # 创建集合
            fields = [
                FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
                FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=65535),
                FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=self.dimension),
                FieldSchema(name="metadata", dtype=DataType.JSON),
            ]
            schema = CollectionSchema(fields, "知识库集合")
            self.collection = Collection(self.collection_name, schema)
            
            # 创建索引
            index_params = {
                "metric_type": "L2",
                "index_type": "IVF_FLAT",
                "params": {"nlist": 1024}
            }
            self.collection.create_index("vector", index_params)
            logger.info(f"已创建集合 '{self.collection_name}'")
        
        # 加载集合到内存
        self.collection.load()
    
    def insert(self, texts: List[str], vectors: List[List[float]], metadatas: List[dict]):
        """插入文档向量"""
        if len(texts) != len(vectors) or len(texts) != len(metadatas):
            raise ValueError("文本、向量和元数据数量必须一致")
        
        # 准备数据，按照字段顺序
        data = []
        for text, vector, metadata in zip(texts, vectors, metadatas):
            data.append({
                text,
                vector,
               metadata
            })
        
        self.collection.insert(data)
        self.collection.flush()
        logger.info(f"已插入 {len(texts)} 条文档")
    
    def search(self, query_vector: List[float], top_k: int = 5) -> List[dict]:
        """向量相似度搜索"""
        search_params = {
            "metric_type": "L2",
            "params": {"nprobe": 10}
        }
        
        results = self.collection.search(
            data=[query_vector],
            anns_field="vector",
            param=search_params,
            limit=top_k,
            output_fields=["text", "metadata"]
        )
        
        # 格式化结果
        formatted_results = []
        for hits in results:
            for hit in hits:
                formatted_results.append({
                    "id": hit.id,
                    "text": hit.entity.get("text"),
                    "metadata": hit.entity.get("metadata"),
                    "distance": hit.distance,
                    "score": 1 / (1 + hit.distance)  # 转换为相似度分数
                })
        
        return formatted_results
    
    def delete(self, ids: List[int]):
        """删除文档"""
        expr = f"id in {ids}"
        self.collection.delete(expr)
        self.collection.flush()
        logger.info(f"已删除 {len(ids)} 条文档")
    
    def get_stats(self) -> dict:
        """获取集合统计信息"""
        stats = self.collection.num_entities
        return {
            "collection_name": self.collection_name,
            "total_documents": stats
        }