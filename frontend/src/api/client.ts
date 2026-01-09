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
  conversation_id?: string;
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
  id:string;
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

export interface DocumentItem{
  id:string;
  text:string;
  metadata:Record<string,any>;
}

export interface DocumentListResponse{
  success:boolean;
  documents:DocumentItem[];
  total:number;
}

export interface DocumentDeleteRequest{
  ids:string[];
}

export interface DocumentDeleteResponse{
  success:boolean;
  message:string;
  deleted_count:string;
}

export interface Conversation {
  id: string;
  user_id: string;
  title: string;
  created_at: string;
  updated_at: string;
  message_count: number;
}

export interface User {
  id: string;
  name: string;
  description?: string;
  created_at: string;
  conversation_count: number;
}

export interface UserCreateRequest {
  name: string;
  description?: string;
}

export interface ConversationCreateRequest {
  user_id: string;
  title?: string;
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

  // 文档处理

  // 添加文档
  async addDocuments(request: DocumentAddRequest): Promise<DocumentAddResponse> {
    const response = await apiClient.post<DocumentAddResponse>('/api/v1/documents', request);
    return response.data;
  },
  // 获取文档列表
  async getDocuments(limit:number = 100): Promise<DocumentListResponse> {
    const response = await apiClient.get<DocumentListResponse>(`/api/v1/documents?limit=${limit}`);
    return response.data;
  },
  
  // 删除列表

  async deleteDocuments(request:DocumentDeleteRequest):Promise<DocumentDeleteResponse>{
    const response = await apiClient.delete<DocumentDeleteResponse>('/api/v1/documents',{data:request});
    return response.data;
  },



  // 记忆处理

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
  // 删除记忆
  async deleteMemory(userId:string,memoryId:string):Promise<{success:boolean,message:string}>
  {
    const response = await apiClient.delete<{success:boolean,message:string}>(`/api/v1/memories/${userId}/${memoryId}`);
    return response.data;
  },


  // 用户管理
  async createUser(request: UserCreateRequest): Promise<User> {
    const response = await apiClient.post<User>('/api/v1/users', request);
    return response.data;
  },
  
  async getUsers(): Promise<{ success: boolean; users: User[]; total: number }> {
    const response = await apiClient.get<{ success: boolean; users: User[]; total: number }>('/api/v1/users');
    return response.data;
  },
  
  async getUser(userId: string): Promise<User> {
    const response = await apiClient.get<User>(`/api/v1/users/${userId}`);
    return response.data;
  },
  
  async deleteUser(userId: string): Promise<{ success: boolean; message: string }> {
    const response = await apiClient.delete<{ success: boolean; message: string }>(`/api/v1/users/${userId}`);
    return response.data;
  },
  
  // 对话管理
  async createConversation(request: ConversationCreateRequest): Promise<Conversation> {
    const response = await apiClient.post<Conversation>('/api/v1/conversations', request);
    return response.data;
  },
  
  async getConversations(userId: string): Promise<{ success: boolean; conversations: Conversation[]; total: number }> {
    const response = await apiClient.get<{ success: boolean; conversations: Conversation[]; total: number }>(
      `/api/v1/conversations/${userId}`
    );
    return response.data;
  },
  
  async deleteConversation(conversationId: string): Promise<{ success: boolean; message: string }> {
    const response = await apiClient.delete<{ success: boolean; message: string }>(
      `/api/v1/conversations/${conversationId}`
    );
    return response.data;
  },
};




export default apiClient;

