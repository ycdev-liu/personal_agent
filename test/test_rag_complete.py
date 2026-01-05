import requests
import json

BASE_URL = "http://127.0.0.1:8001"

def check_health():
    """检查服务状态"""
    response = requests.get(f"{BASE_URL}/api/v1/health")
    data = response.json()
    print(f"服务状态: {data.get('status')}")
    if 'milvus' in data:
        print(f"知识库文档数: {data['milvus'].get('total_documents', 0)}")
    return data

def add_documents():
    """添加测试文档"""
    documents = {
        "texts": [
            "RAG（Retrieval-Augmented Generation）是检索增强生成技术。",
            "它结合了信息检索和文本生成，先从知识库中检索相关信息，然后基于这些信息生成回答。",
            "RAG 系统通常包括向量数据库、嵌入模型和生成模型三个组件。"
        ],
        "metadatas": [
            {"source": "test", "topic": "RAG"},
            {"source": "test", "topic": "RAG"},
            {"source": "test", "topic": "RAG"}
        ]
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/documents",
        json=documents
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ 添加了 {result['count']} 个文档")
        return True
    else:
        print(f"❌ 添加失败: {response.text}")
        return False

def test_rag():
    """测试 RAG 检索"""
    chat_data = {
        "user_id": "test_user",
        "message": "RAG 是什么",
        "use_memory": False,
        "use_rag": True
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/chat",
        json=chat_data
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✅ 检索成功")
        print(f"回复: {result['response'][:100]}...")
        print(f"检索到的文档数: {len(result.get('sources', []))}")
        if result.get('sources'):
            print(f"第一个文档相似度: {result['sources'][0].get('score', 0):.4f}")
        return True
    else:
        print(f"❌ 检索失败: {response.text}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("RAG 完整测试")
    print("=" * 60)
    
    # 1. 检查状态
    print("\n[1] 检查服务状态...")
    health = check_health()
    
    # 2. 如果知识库为空，添加文档
    doc_count = health.get('milvus', {}).get('total_documents', 0)
    if doc_count == 0:
        print("\n[2] 知识库为空，添加测试文档...")
        add_documents()
        print("\n[3] 再次检查状态...")
        check_health()
    else:
        print(f"\n[2] 知识库已有 {doc_count} 个文档，跳过添加")
    
    # 3. 测试 RAG 检索
    print("\n[4] 测试 RAG 检索...")
    test_rag()
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)