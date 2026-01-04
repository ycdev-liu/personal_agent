# 个人知识库智能助手

基于 LangChain + FastAPI + Milvus + MongoDB 构建的 RAG 智能助手，支持长期记忆和个性化对话。

## 功能特性

- 🔍 **RAG 检索增强生成**：使用 Milvus 向量数据库实现语义检索
- 🧠 **长期记忆**：使用 MongoDB 存储用户记忆和对话历史
- 💬 **个性化对话**：基于用户历史记忆提供个性化回复
- 📚 **知识库管理**：支持添加和管理文档知识库
- 🔄 **可持续学习**：自动保存对话和用户记忆，实现持续学习
- 🚀 **多 LLM 支持**：支持 OpenAI、DashScope（通义千问）和本地模型

## 技术栈

- **后端框架**: FastAPI
- **LLM 框架**: LangChain
- **LLM 提供商**: OpenAI / DashScope（通义千问）/ 本地模型（OpenAI 兼容接口）
- **向量数据库**: Milvus
- **文档数据库**: MongoDB
- **嵌入模型**: Sentence Transformers
- **前端**: React + TypeScript + Vite

## 快速开始

### 环境要求

- Python 3.12+
- Node.js 18+ (前端)
- Docker & Docker Compose (数据库服务)
- uv (Python 包管理器，推荐) 或 pip

### 1. 安装后端依赖
h
# 使用 uv (推荐)
uv sync

# 或使用 pip
pip install -r requirements.txt### 2. 安装前端依赖

cd frontend
npm install### 3. 配置

项目支持两种配置方式：

#### 方式一：使用 YAML 配置文件（推荐）

编辑 `config/settings.yaml`：

# API 配置
api:
  host: "127.0.0.1"
  port: 8001
  title: "个人知识库智能助手"

# LLM 配置
llm:
  provider: "local"  # "openai" | "dashscope" | "local"
  model: "/root/large_model_project/models/Qwen2.5-3B-Instruct"  # 本地模型路径
  temperature: 0.7
  max_tokens: 1024
  api_key: "none"  # 本地模型可为任意值
  base_url: "http://localhost:8000/v1"  # 本地模型服务地址#### 方式二：使用环境变量

创建 `.env` 文件（可选）：

# API 配置
API_HOST=127.0.0.1
API_PORT=8001

# LLM 配置
LLM_PROVIDER=local  # openai | dashscope | local
LLM_MODEL=/root/large_model_project/models/Qwen2.5-3B-Instruct
LLM_BASE_URL=http://localhost:8000/v1
OPENAI_API_KEY=none  # 本地模型可为任意值

# 数据库配置（如果使用 Docker，会自动配置）
MILVUS_HOST=localhost
MILVUS_PORT=19530
MONGODB_URI=mongodb://localhost:27017**注意**：YAML 配置优先级高于环境变量，如果两者都存在，YAML 配置会覆盖环境变量。

### 4. 启动数据库服务

使用 Docker Compose 启动 Milvus 和 MongoDB：

# 启动数据库服务（Milvus、etcd、MinIO、MongoDB）
docker-compose up -d milvus etcd minio mongodb

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f milvus
docker-compose logs -f mongodb### 5. 启动后端应用

# 方式一：使用 uv
uv run python main.py

# 方式二：使用 Python
python main.py

# 方式三：使用 uvicorn
uvicorn main:app --host 127.0.0.1 --port 8001 --reload后端应用将在 http://127.0.0.1:8001 启动。

### 6. 启动前端应用

cd frontend
npm run dev前端应用将在 http://localhost:3000 启动。

### 7. 开发环境快速启动（Windows PowerShell）

项目提供了开发环境启动脚本，可以一键启动所有服务：
l
.\start-dev.ps1该脚本会：
- 检查并启动 Docker 数据库服务
- 启动后端服务（端口 8001）
- 启动前端服务（端口 3000）

### 8. 访问应用

- **前端界面**: http://localhost:3000
- **API 文档**: http://127.0.0.1:8001/docs
- **API 根路径**: http://127.0.0.1:8001/

## LLM 配置说明

项目支持三种 LLM 提供商：

### OpenAI

llm:
  provider: "openai"
  model: "gpt-4-turbo-preview"  # 或 gpt-3.5-turbo
  temperature: 0.7
  max_tokens: 2000
  api_key: "sk-your-openai-api-key"或在 `.env` 文件中：
LLM_PROVIDER=openai
LLM_MODEL=gpt-4-turbo-preview
OPENAI_API_KEY=sk-your-openai-api-key### DashScope（通义千问）

llm:
  provider: "dashscope"
  model: "qwen-plus"  # qwen-turbo | qwen-plus | qwen-max
  temperature: 0.7
  max_tokens: 2000
  api_key: "sk-your-dashscope-api-key"或在 `.env` 文件中：
LLM_PROVIDER=dashscope
LLM_MODEL=qwen-plus
OPENAI_API_KEY=sk-your-dashscope-api-key  # DashScope API Key**获取 DashScope API Key**: https://dashscope.console.aliyun.com/

### 本地模型（OpenAI 兼容接口）

llm:
  provider: "local"
  model: "/path/to/your/model"  # 模型路径或标识符
  temperature: 0.7
  max_tokens: 1024  # 根据模型上下文长度调整
  api_key: "none"  # 可为任意值
  base_url: "http://localhost:8000/v1"  # 本地模型服务地址或在 `.env` 文件中：
LLM_PROVIDER=local
LLM_MODEL=/path/to/your/model
LLM_BASE_URL=http://localhost:8000/v1
OPENAI_API_KEY=none**注意**：
- 本地模型服务需要提供 OpenAI 兼容的 API 接口
- `base_url` 应该指向本地模型服务的 `/v1` 端点
- `max_tokens` 需要根据模型的上下文长度调整（如 Qwen2.5-3B 为 2048）

## API 使用示例

### 聊天

curl -X POST "http://127.0.0.1:8001/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "message": "什么是人工智能？",
    "use_memory": true,
    "use_rag": true
  }'### 添加文档到知识库

curl -X POST "http://127.0.0.1:8001/api/v1/documents" \
  -H "Content-Type: application/json" \
  -d '{
    "texts": [
      "人工智能是计算机科学的一个分支，致力于创建能够执行通常需要人类智能的任务的系统。",
      "机器学习是人工智能的一个子领域，通过算法使计算机能够从数据中学习。"
    ],
    "metadatas": [
      {"source": "wiki"},
      {"source": "wiki"}
    ]
  }'### 添加用户记忆

curl -X POST "http://127.0.0.1:8001/api/v1/memories" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "content": "用户喜欢喝咖啡，每天早上都会喝一杯",
    "memory_type": "preference",
    "importance": 0.8
  }'### 获取用户记忆

curl -X GET "http://127.0.0.1:8001/api/v1/memories/user123"### 健康检查

curl -X GET "http://127.0.0.1:8001/api/v1/health"## 项目结构
