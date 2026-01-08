import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
import yaml


class Settings(BaseSettings):
    """应用配置"""
    
    # API 配置
    api_host: str = Field(default="127.0.0.1", alias="API_HOST")
    api_port: int = Field(default=8001, alias="API_PORT")
    api_title: str = Field(default="个人知识库智能助手", alias="API_TITLE")
    
    # LLM 配置
    llm_provider: str = Field(default="openai", alias="LLM_PROVIDER")
    llm_model: str = Field(default="gpt-4-turbo-preview", alias="LLM_MODEL")
    llm_temperature: float = Field(default=0.7, alias="LLM_TEMPERATURE")
    llm_max_tokens: int = Field(default=2000, alias="LLM_MAX_TOKENS")
    openai_api_key: Optional[str] = Field(default=None, alias="OPENAI_API_KEY")
    # 本地模型部署
    llm_base_url : Optional[str] = Field(default=None,alias="LLM_BASE_URL")


    
    # Milvus 配置
    milvus_host: str = Field(default="localhost", alias="MILVUS_HOST")
    milvus_port: int = Field(default=19530, alias="MILVUS_PORT")
    milvus_collection_name: str = Field(default="knowledge_base", alias="MILVUS_COLLECTION")
    milvus_dimension: int = Field(default=768, alias="MILVUS_DIMENSION")
    
    # MongoDB 配置
    mongodb_uri: str = Field(default="mongodb://localhost:27017", alias="MONGODB_URI")
    mongodb_database: str = Field(default="personal_agent", alias="MONGODB_DATABASE")
    
    # 嵌入模型配置
    embedding_model: str = Field(
        default=None,
        alias="EMBEDDING_MODEL"
    )
    embedding_device: str = Field(default="cpu", alias="EMBEDDING_DEVICE")
    
    # RAG 配置
    rag_top_k: int = Field(default=5, alias="RAG_TOP_K")
    rag_similarity_threshold: float = Field(default=0.7, alias="RAG_SIMILARITY_THRESHOLD")
    rag_chunk_size: int = Field(default=500, alias="RAG_CHUNK_SIZE")
    rag_chunk_overlap: int = Field(default=50, alias="RAG_CHUNK_OVERLAP")
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )


def load_config() -> Settings:
    """加载配置"""
    config_path = Path(__file__).parent.parent.parent / "config" / "settings.yaml"
    
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            yaml_config = yaml.safe_load(f)
        
        # 从 YAML 更新环境变量（如果存在）
        if yaml_config:
            for section, values in yaml_config.items():
                if isinstance(values, dict):
                    for key, value in values.items():
                        env_key = f"{section.upper()}_{key.upper()}"
                        os.environ[env_key] = str(value)
    
    return Settings()
    
settings = load_config()
print(settings.embedding_model)