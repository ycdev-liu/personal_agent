from fastapi import APIRouter, HTTPException
from app.api.schemas import (
    UserCreateRequest, UserResponse, UserListResponse,
    ConversationCreateRequest, ConversationResponse, ConversationListResponse
)
from app.services.user_service import user_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["用户管理"])


@router.post("/users", response_model=UserResponse)
async def create_user(request: UserCreateRequest):
    """创建新用户"""
    try:
        user = user_service.create_user(
            name=request.name,
            description=request.description
        )
        return UserResponse(**user)
    except Exception as e:
        logger.error(f"创建用户失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users", response_model=UserListResponse)
async def list_users():
    """获取用户列表"""
    try:
        users = user_service.list_users()
        return UserListResponse(
            success=True,
            users=[UserResponse(**user) for user in users],
            total=len(users)
        )
    except Exception as e:
        logger.error(f"获取用户列表失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: str):
    """获取用户信息"""
    try:
        user = user_service.get_user(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        return UserResponse(**user)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取用户失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/users/{user_id}")
async def delete_user(user_id: str):
    """删除用户"""
    try:
        success = user_service.delete_user(user_id)
        if not success:
            raise HTTPException(status_code=404, detail="用户不存在")
        return {"success": True, "message": "用户删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除用户失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/conversations", response_model=ConversationResponse)
async def create_conversation(request: ConversationCreateRequest):
    """创建新对话"""
    try:
        conversation = user_service.create_conversation(
            user_id=request.user_id,
            title=request.title
        )
        return ConversationResponse(**conversation)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"创建对话失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversations/{user_id}", response_model=ConversationListResponse)
async def list_conversations(user_id: str):
    """获取用户的对话列表"""
    try:
        conversations = user_service.list_conversations(user_id)
        return ConversationListResponse(
            success=True,
            conversations=[ConversationResponse(**conv) for conv in conversations],
            total=len(conversations)
        )
    except Exception as e:
        logger.error(f"获取对话列表失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversations/detail/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(conversation_id: str):
    """获取对话详情"""
    try:
        conversation = user_service.get_conversation(conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="对话不存在")
        return ConversationResponse(**conversation)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取对话失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """删除对话"""
    try:
        success = user_service.delete_conversation(conversation_id)
        if not success:
            raise HTTPException(status_code=404, detail="对话不存在")
        return {"success": True, "message": "对话删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除对话失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))