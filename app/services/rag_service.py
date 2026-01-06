from typing import List, Dict
from app.core.milvus_client import MilvusClient
from app.services.embedding_service import embedding_service
from app.core.config import settings
from app.utils.text_processor import TextProcessor
import logging

logging.basicConfig(
    level=logging.INFO
)

logger = logging.getLogger(__name__)


class RAGService:
    """RAG 检索增强生成服务"""
    
    def __init__(self):
        self.milvus_client = MilvusClient()
        self.text_processor = TextProcessor()
        self.top_k = settings.rag_top_k
        self.similarity_threshold = settings.rag_similarity_threshold
    
    def add_documents(self, texts: List[str], metadatas: List[dict] = None):
        """添加文档到知识库"""
        if metadatas is None:
            metadatas = [{}] * len(texts)
        
        # 文本分块
        chunks = []
        chunk_metadatas = []
        
        for text, metadata in zip(texts, metadatas):
            text_chunks = self.text_processor.split_text(text)
            chunks.extend(text_chunks)
            chunk_metadatas.extend([metadata] * len(text_chunks))
        
        # 生成向量
        vectors = embedding_service.encode(chunks)
        
        # 插入 Milvus
        self.milvus_client.insert(chunks, vectors, chunk_metadatas)
        logger.info(f"已添加 {len(chunks)} 个文档块到知识库")

    def delete_documents(self,ids:List[int]):
        """删除文档"""
        if not ids:
            logger.warning("删除列表为空")
            return 

        self.milvus_client.delete(ids)
        logger.info(f"已删除 {len(ids)} 个文档")

    
    def search(self, query: str, top_k: int = None) -> List[Dict]:
        """检索相关文档"""
        if top_k is None:
            top_k = self.top_k
        
        # 生成查询向量
        query_vector = embedding_service.encode_single(query)

        
        
        # 向量搜索
        results = self.milvus_client.search(query_vector, top_k=top_k)

        logger.info(f"检索查询: '{query}'")
        logger.info(f"Milvus 返回 {len(results)} 个结果（过滤前）")

        if results:
            scores = [r['score'] for r in results]
            logger.info(f"相似度分数范围: {min(scores):.4f} ~ {max(scores):.4f}")
            logger.info(f"当前阈值: {self.similarity_threshold}")
            for i, r in enumerate(results[:3], 1):  # 只显示前3个
                logger.info(f"  结果 {i}: 相似度={r['score']:.4f}, 文本={r['text'][:50]}...")
        else:
            logger.warning("Milvus 未返回任何结果（可能知识库为空）")
        
        
        # 过滤低相似度结果
        filtered_results = [
            r for r in results 
            if r["score"] >= self.similarity_threshold
        ]
        
        return filtered_results

    def  get_all_documents(self,limit:int =1000) ->List[Dict]:
        """获取所有文档"""
        return self.milvus_client.query_all(limit)
    


    
    def get_context(self, query: str, top_k: int = None) -> List[str]:
        """获取检索到的上下文文本"""
        results = self.search(query, top_k)
        return [r["text"] for r in results]


# 全局 RAG 服务实例
rag_service = RAGService()

