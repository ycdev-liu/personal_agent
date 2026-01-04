from sentence_transformers import SentenceTransformer
from typing import List
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class EmbeddingService:
    """文本嵌入服务"""
    
    def __init__(self):
        self.model_name = settings.embedding_model
        self.device = settings.embedding_device
        self.model: SentenceTransformer = None
        self._load_model()
    
    def _load_model(self):
        """加载嵌入模型"""
        try:
            self.model = SentenceTransformer(self.model_name, device=self.device)
            logger.info(f"已加载嵌入模型: {self.model_name}")
        except Exception as e:
            logger.error(f"加载嵌入模型失败: {e}")
            raise
    
    def encode(self, texts: List[str]) -> List[List[float]]:
        """将文本编码为向量"""
        if isinstance(texts, str):
            texts = [texts]
        
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()
    
    def encode_single(self, text: str) -> List[float]:
        """编码单个文本"""
        return self.encode([text])[0]


# 全局嵌入服务实例
embedding_service = EmbeddingService()

