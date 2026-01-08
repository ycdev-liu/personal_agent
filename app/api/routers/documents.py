from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import List
from app.api.schemas import (
    DocumentAddRequest, DocumentAddResponse,
    DocumentItem, DocumentListResponse,
    DocumentDeleteRequest, DocumentDeleteResponse
)
from app.services.rag_service import rag_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["文档管理"])


@router.post("/documents", response_model=DocumentAddResponse)
async def add_documents(request: DocumentAddRequest):
    """添加文档到知识库"""
    try:
        metadatas = request.metadatas or [{}] * len(request.texts)
        rag_service.add_documents(request.texts, metadatas)
        
        return DocumentAddResponse(
            success=True,
            message="文档添加成功",
            count=len(request.texts)
        )
    except Exception as e:
        logger.error(f"添加文档失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/documents/upload", response_model=DocumentAddResponse)
async def upload_documents(files: List[UploadFile] = File(...)):
    """上传文档文件"""
    try:
        texts = []
        metadatas = []
        for file in files:
            content = await file.read()
            texts.append(content.decode("utf-8"))
            metadatas.append({
                "source": "file",
                "filename": file.filename,
                "content_type": file.content_type
            })

        rag_service.add_documents(texts, metadatas)

        return DocumentAddResponse(
            success=True,
            message="文档上传成功",
            count=len(texts)
        )
    except Exception as e:
        logger.error(f"文档上传失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/documents", response_model=DocumentListResponse)
async def get_documents(limit: int = 100):
    """获取文档列表"""
    try:
        documents = rag_service.get_all_documents(limit)
        
        # 将 ID 转换为字符串（避免 JavaScript 大整数精度问题）
        documents_with_str_id = [
            DocumentItem(
                id=str(doc["id"]),
                text=doc["text"],
                metadata=doc["metadata"]
            )
            for doc in documents
        ]
        
        return DocumentListResponse(
            success=True,
            documents=documents_with_str_id,
            total=len(documents_with_str_id)
        )
    except Exception as e:
        logger.error(f"获取文档失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/documents",response_model=DocumentDeleteResponse)
async def delete_documents(request: DocumentDeleteRequest):
    try:

        logger.info(f"删除文档: {request.ids}")
        id_list = [int(id_str) for id_str in request.ids]
        logger.info(f"删除文档: {id_list}")
        request.ids = id_list

        rag_service.delete_documents(request.ids)


        return DocumentDeleteResponse(
            success = True,
            message=f"成功删除{len(request.ids)}个文档",
            deleted_count=len(request.ids)
        )
    
    except Exception as e:
        logger.error(f"删除文档失败{e}",exc_info = True)
        raise HTTPException(status_code=500,detail=str(e))
