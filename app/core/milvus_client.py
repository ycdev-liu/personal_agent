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
            # 一张集合模版
            # 一旦创建不可修改
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
                "metric_type": "COSINE",
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
        
        # # 准备数据，按照字段顺序
        # data = []
        # for text, vector, metadata in zip(texts, vectors, metadatas):
        #     data.append({
        #         text,
        #         vector,
        #        metadata
        #     })

            # Milvus 按列格式插入数据（列表的列表）

        # 不需要插入id
        data = [
            texts,      # 所有文本的列表
            vectors,    # 所有向量的列表（列表的列表）
            metadatas   # 所有元数据的列表
        ]
        
        self.collection.insert(data)
        # 将内存中的数据写入磁盘
        # flush() = “现在就把插入的数据真正存下来”
        # 决定数据是否能被索引 & 稳定查询
        # 不要每条数据都 flush，批量更好
        self.collection.flush()
        logger.info(f"已插入 {len(texts)} 条文档")
    
    def search(self, query_vector: List[float], top_k: int = 5) -> List[dict]:
        """向量相似度搜索"""
        # search_params = {
        #     "metric_type": "L2",
        #     "params": {"nprobe": 10}
        # }
        # 余弦相似度
        search_params = {
            "metric_type": "COSINE",
            "params": {"nprobe": 10}
        }

        
        results = self.collection.search(
            data=[query_vector], # 根据向量查询
            anns_field="vector", # 向量字段
            param=search_params, # 查询参数
            limit=top_k, # 返回结果数量
            output_fields=["text", "metadata"] # 返回字段 text 文本 metadata 元数据
        )

        
        # 格式化结果
        formatted_results = []
        for hits in results:
            for hit in hits:
                # 每条结果是一个字典
                formatted_results.append({
                    "id": hit.id,
                    "text": hit.entity.get("text"), # 命中记录的文本
                    "metadata": hit.entity.get("metadata"), # 命中记录的元数据
                    "distance": hit.distance, # 默然存在       
                    "score": 1 / (1 + hit.distance)  # 转换为相似度分数
                })
        
        return formatted_results


        

    def query_all(self,limit :int = 1000) -> List[dict]:
        """查询所有文档"""


        results = self.collection.query(
            expr="id >= 0",
            output_fields=["text", "metadata","id"],
            limit=limit
        )
        formatted_results = []
        logger.info(f"查询到 {len(results)} 条文档")
        logger.info(f"results: {results}")

        for result in results:
            formatted_results.append({
                "id": str(result.get("id")),
                "text": result.get("text",""),
                "metadata": result.get("metadata",{}),
            })
        logger.info(f"formatted_results: {formatted_results}")
    
        return formatted_results
    
    def delete(self, ids: List[int]):
        """删除文档"""
        if not ids:
            logger.warning("没有提供要删除的文档ID")
            return 

        
        
        logger.info(f"删除ID: {ids}")
        ids_str = ",".join(str(id) for id in ids)
        expr = f"id in [{ids_str}]"
        logger.info(f"删除表达式: {expr}")
        self.collection.delete(expr)
        
        # 将内存中的数据写入磁盘
        self.collection.flush()
        logger.info(f"已删除 {len(ids)} 条文档")
    


    def get_stats(self) -> dict:
        """获取集合统计信息"""
        stats = self.collection.num_entities
        return {
            "collection_name": self.collection_name,
            "total_documents": stats
        }