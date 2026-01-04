# query_models.py
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="none"
)

# 尝试不同的模型路径
test_models = [
    "/root/large_model_project/models/Qwen2.5-3B-Instruct",
    "/root/large_model_project/model/Qwen2.5-3B-Instruct",
    "Qwen2.5-3B-Instruct",
    "qwen2.5-3b-instruct",
]

print("测试模型路径...")
for model_path in test_models:
    try:
        resp = client.chat.completions.create(
            model=model_path,
            messages=[{"role": "user", "content": "你好"}],
            max_tokens=5
        )
        print(f"✓ 成功: {model_path}")
        print(f"  响应: {resp.choices[0].message.content}")
        break
    except Exception as e:
        error_msg = str(e)
        if "does not exist" in error_msg:
            print(f"✗ 模型不存在: {model_path}")
        else:
            print(f"✗ 其他错误: {model_path} - {error_msg[:100]}")