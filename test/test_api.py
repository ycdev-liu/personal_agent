import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """测试健康检查"""
    print("[1/6] 测试健康检查...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/health")
        response.raise_for_status()
        print(f"✓ 健康检查: {response.json()}")
        return True
    except Exception as e:
        print(f"✗ 失败: {e}")
        return False

def test_add_documents():
    """测试添加文档"""
    print("\n[2/6] 测试添加文档...")
    try:
        data = {
            "texts": [
                "人工智能是计算机科学的一个分支。",
                "机器学习是人工智能的子领域。"
            ],
            "metadatas": [{"source": "test"}, {"source": "test"}]
        }
        response = requests.post(f"{BASE_URL}/api/v1/documents", json=data)
        response.raise_for_status()
        result = response.json()
        if result.get("success"):
            print(f"✓ 添加文档成功: {result['count']} 条")
            return True
        else:
            print(f"✗ 添加文档失败: {result}")
            return False
    except Exception as e:
        print(f"✗ 失败: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"  错误详情: {e.response.json()}")
        return False

def test_add_memory():
    """测试添加记忆"""
    print("\n[3/6] 测试添加记忆...")
    try:
        data = {
            "user_id": "test_user_001",
            "content": "用户喜欢喝咖啡",
            "memory_type": "preference",
            "importance": 0.8
        }
        response = requests.post(f"{BASE_URL}/api/v1/memories", json=data)
        response.raise_for_status()
        result = response.json()
        if result.get("success"):
            print(f"✓ 添加记忆成功")
            return True
        else:
            print(f"✗ 添加记忆失败: {result}")
            return False
    except Exception as e:
        print(f"✗ 失败: {e}")
        return False

def test_chat_no_rag():
    """测试聊天（不使用 RAG）"""
    print("\n[4/6] 测试聊天（不使用 RAG）...")
    try:
        data = {
            "user_id": "test_user_001",
            "message": "你好，请介绍一下你自己",
            "use_memory": True,
            "use_rag": False
        }
        response = requests.post(f"{BASE_URL}/api/v1/chat", json=data)
        response.raise_for_status()
        result = response.json()
        if "response" in result:
            print(f"✓ 聊天成功")
            print(f"  回复: {result['response'][:100]}...")
            return True
        else:
            print(f"✗ 聊天失败: 响应中缺少 'response' 字段")
            print(f"  响应: {result}")
            return False
    except Exception as e:
        print(f"✗ 失败: {e}")
        if hasattr(e, 'response') and e.response is not None:
            try:
                print(f"  错误详情: {e.response.json()}")
            except:
                print(f"  错误详情: {e.response.text}")
        return False

def test_chat_with_rag():
    """测试聊天（使用 RAG）"""
    print("\n[5/6] 测试聊天（使用 RAG）...")
    try:
        data = {
            "user_id": "test_user_001",
            "message": "什么是人工智能？",
            "use_memory": True,
            "use_rag": True
        }
        response = requests.post(f"{BASE_URL}/api/v1/chat", json=data)
        response.raise_for_status()
        result = response.json()
        if "response" in result:
            print(f"✓ RAG 聊天成功")
            print(f"  回复: {result['response'][:100]}...")
            print(f"  来源数: {len(result.get('sources', []))}")
            print(f"  记忆数: {len(result.get('memories_used', []))}")
            return True
        else:
            print(f"✗ RAG 聊天失败: 响应中缺少 'response' 字段")
            print(f"  响应: {result}")
            return False
    except Exception as e:
        print(f"✗ 失败: {e}")
        if hasattr(e, 'response') and e.response is not None:
            try:
                print(f"  错误详情: {e.response.json()}")
            except:
                print(f"  错误详情: {e.response.text}")
        return False

def test_get_memories():
    """测试获取记忆"""
    print("\n[6/6] 测试获取记忆...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/memories/test_user_001")
        response.raise_for_status()
        result = response.json()
        if result.get("success"):
            print(f"✓ 获取记忆成功: {len(result.get('memories', []))} 条")
            return True
        else:
            print(f"✗ 获取记忆失败: {result}")
            return False
    except Exception as e:
        print(f"✗ 失败: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("快速测试个人知识库智能助手 API")
    print("=" * 50)
    
    results = [
        test_health(),
        test_add_documents(),
        test_add_memory(),
        test_chat_no_rag(),
        test_chat_with_rag(),
        test_get_memories()
    ]
    
    print("\n" + "=" * 50)
    print(f"测试完成！成功: {sum(results)}/{len(results)}")
    print("=" * 50)