import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8001';



const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface ChatRequest {
  user_id: string;
  message: string;
  use_memory?: boolean;
  use_rag?: boolean;
}

export interface ChatResponse {
  response: string;
  sources: Array<{
    text: string;
    score: number;
    metadata?: Record<string, any>;
  }>;
  memories_used: Array<{
    content: string;
    type: string;
    importance: number;
  }>;
  conversation_id?: string;
}

export interface DocumentAddRequest {
  texts: string[];
  metadatas?: Array<Record<string, any>>;
}

export interface DocumentAddResponse {
  success: boolean;
  message: string;
  count: number;
}

export interface MemoryAddRequest {
  user_id: string;
  content: string;
  memory_type?: string;
  importance?: number;
}

export interface Memory {
  content: string;
  type: string;
  importance: number;
  timestamp?: string;
}

export interface MemoriesResponse {
  success: boolean;
  memories: Memory[];
}

export interface HealthResponse {
  status: string;
  milvus?: {
    collection_name: string;
    total_documents: number;
  };
  mongodb?: string;
  error?: string;
}

export const api = {
  // 健康检查
  async healthCheck(): Promise<HealthResponse> {
    // 发出请求
    const response = await apiClient.get<HealthResponse>('/api/v1/health');
    return response.data;
  },

  // 聊天
  async chat(request: ChatRequest): Promise<ChatResponse> {
    const response = await apiClient.post<ChatResponse>('/api/v1/chat', request);
    return response.data;
  },

  // 添加文档
  async addDocuments(request: DocumentAddRequest): Promise<DocumentAddResponse> {
    const response = await apiClient.post<DocumentAddResponse>('/api/v1/documents', request);
    return response.data;
  },

  // 添加记忆
  async addMemory(request: MemoryAddRequest): Promise<{ success: boolean; message: string }> {
    const response = await apiClient.post('/api/v1/memories', request);
    return response.data;
  },

  // 获取记忆
  async getMemories(userId: string): Promise<MemoriesResponse> {
    const response = await apiClient.get<MemoriesResponse>(`/api/v1/memories/${userId}`);
    return response.data;
  },
};

export default apiClient;

