from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime


class ChatRequest(BaseModel):
    """聊天请求"""
    user_id: str = Field(..., description="用户ID")
    message: str = Field(..., description="用户消息")
    use_memory: bool = Field(default=True, description="是否使用记忆")
    use_rag: bool = Field(default=True, description="是否使用RAG检索")


class ChatResponse(BaseModel):
    """聊天响应"""
    response: str = Field(..., description="助手回复")
    sources: List[Dict] = Field(default=[], description="知识库来源")
    memories_used: List[Dict] = Field(default=[], description="使用的记忆")
    conversation_id: Optional[str] = Field(None, description="对话ID")




class DocumentAddRequest(BaseModel):
    """添加文档请求"""
    texts: List[str] = Field(..., description="文档文本列表")
    metadatas: Optional[List[Dict]] = Field(None, description="文档元数据")


class DocumentAddResponse(BaseModel):
    """添加文档响应"""
    success: bool
    message: str
    count: int


class MemoryAddRequest(BaseModel):
    """添加记忆请求"""
    user_id: str
    content: str
    memory_type: str = Field(default="fact", description="记忆类型")
    importance: float = Field(default=0.5, ge=0.0, le=1.0, description="重要性")

class DocumentItem(BaseModel):
    """文档项"""
    id: str 
    text: str
    metadata: dict

class DocumentListResponse(BaseModel):
    """文档列表响应"""
    success: bool
    documents: List[DocumentItem]
    total: int

class DocumentDeleteRequest(BaseModel):
    """删除文档请求"""
    ids: List[str] = Field(..., description="要删除的文档ID列表")

class DocumentDeleteResponse(BaseModel):
    """删除文档响应"""
    success: bool
    message: str
    deleted_count: int