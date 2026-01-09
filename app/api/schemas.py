from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime


class ChatRequest(BaseModel):
    """聊天请求"""
    user_id: str = Field(..., description="用户ID")
    message: str = Field(..., description="用户消息")
    use_memory: bool = Field(default=True, description="是否使用记忆")
    use_rag: bool = Field(default=True, description="是否使用RAG检索")
    conversation_id:Optional[str] = Field(None,description="对话ID")


class ChatResponse(BaseModel):
    """聊天响应"""
    response: str = Field(..., description="助手回复")
    sources: List[Dict] = Field(default=[], description="知识库来源")
    memories_used: List[Dict] = Field(default=[], description="使用的记忆")
    conversation_id: Optional[str] = Field(None, description="对话ID")


class MemoryAddRequest(BaseModel):
    """添加记忆请求"""
    user_id: str
    content: str
    memory_type: str = Field(default="fact", description="记忆类型")
    importance: float = Field(default=0.5, ge=0.0, le=1.0, description="重要性")


# 文档相关请求和响应
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

class DocumentAddRequest(BaseModel):
    """添加文档请求"""
    texts: List[str] = Field(..., description="文档文本列表")
    metadatas: Optional[List[Dict]] = Field(None, description="文档元数据")

class DocumentAddResponse(BaseModel):
    """添加文档响应"""
    success: bool
    message: str
    count: int


# 在现有代码后添加

class UserCreateRequest(BaseModel):
    """创建用户请求"""
    name: str = Field(..., description="用户名称")
    description: Optional[str] = Field(None, description="用户描述")

class UserResponse(BaseModel):
    """用户响应"""
    id: str
    name: str
    description: Optional[str] = None
    created_at: datetime
    conversation_count: int = 0

class UserListResponse(BaseModel):
    """用户列表响应"""
    success: bool
    users: List[UserResponse]
    total: int

class ConversationCreateRequest(BaseModel):
    """创建对话请求"""
    user_id: str = Field(..., description="用户ID")
    title: Optional[str] = Field(None, description="对话标题")

class ConversationResponse(BaseModel):
    """对话响应"""
    id: str
    user_id: str
    title: str
    created_at: datetime
    updated_at: datetime
    message_count: int = 0

class ConversationListResponse(BaseModel):
    """对话列表响应"""
    success: bool
    conversations: List[ConversationResponse]
    total: int