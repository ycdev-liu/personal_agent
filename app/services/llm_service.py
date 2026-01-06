from langchain_openai import ChatOpenAI

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage
from typing import List, Optional, Dict
from app.core.config import settings
import logging



logging.basicConfig(
    level=logging.INFO
)

logger = logging.getLogger(__name__)


class LLMService:
    """LLM 服务"""
    
    def __init__(self):
        self.model_name = settings.llm_model
        self.temperature = settings.llm_temperature
        self.max_tokens = settings.llm_max_tokens
        self.api_key = settings.openai_api_key
        self.provider = settings.llm_provider.lower()
        self.base_url=settings.llm_base_url


        is_local = self.provider == "local" or self.base_url is not None
        
        
        if is_local:
            # 本地模型：使用自定义 base_url，api_key 可以是任意值
            self.api_key = settings.openai_api_key or "none"
            base_url = self.base_url or "http://localhost:8000/v1"
            
            self.llm = ChatOpenAI(
                model=self.model_name,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                openai_api_key=self.api_key,
                base_url=base_url
            )
            logger.info(f"已初始化本地 LLM: {self.model_name} (base_url: {base_url})")
        elif self.provider == "dashscope" or "qwen" in self.model_name.lower():
            # DashScope（通义千问）兼容接口
            self.api_key = settings.openai_api_key
            if not self.api_key:
                raise ValueError("DashScope API Key 未设置，请设置 OPENAI_API_KEY")
            
            self.llm = ChatOpenAI(
                model=self.model_name,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                openai_api_key=self.api_key,
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
            )
            logger.info(f"已初始化 DashScope LLM: {self.model_name}")
        else:
            # 标准 OpenAI 接口
            self.api_key = settings.openai_api_key
            if not self.api_key:
                raise ValueError("OPENAI_API_KEY 未设置，请在 .env 文件中设置")
            
            self.llm = ChatOpenAI(
                model=self.model_name,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                openai_api_key=self.api_key
            )
            logger.info(f"已初始化 OpenAI LLM: {self.model_name}")
    def generate(
        self,
        messages: List[BaseMessage],
        system_prompt: Optional[str] = None
    ) -> str:
        """生成回复"""
        if system_prompt:
            messages = [SystemMessage(content=system_prompt)] + messages
        
        response = self.llm.invoke(messages)
        return response.content
    
    def generate_with_context(
        self,
        user_message: str,
        context: List[str],
        conversation_history: List[dict],
        user_memories: List[dict] = None
    ) -> str:
        """基于上下文生成回复"""
        # 构建系统提示
        logger.info(f"user_memories: {user_memories}")
        system_prompt = self._build_system_prompt(user_memories)
        logger.info(f"system_prompt: {system_prompt}")
        
        # 构建上下文
        context_text = "\n\n".join([
            f"[文档 {i+1}]: {doc}" for i, doc in enumerate(context)
        ])
        
        # 构建历史对话
        history_messages = []
        for msg in conversation_history[-10:]:  # 最近10轮对话
            if msg["role"] == "user":
                history_messages.append(HumanMessage(content=msg["content"]))
            else:
                history_messages.append(AIMessage(content=msg["content"]))
        
        # 构建当前消息
        current_message = f"""基于以下知识库内容回答问题：

{context_text}

用户问题：{user_message}"""
        
        messages = history_messages + [HumanMessage(content=current_message)]
        
        return self.generate(messages, system_prompt)
    
    def _build_system_prompt(self, user_memories: List[dict] = None) -> str:
        """构建系统提示"""
        base_prompt = """你是一个智能助手，能够基于提供的知识库内容和用户的历史对话记忆回答问题。
                        请遵循以下原则：
                        1. 基于知识库内容回答，不要编造信息
                        2. 如果知识库中没有相关信息，诚实告知用户
                        3. 结合用户的历史记忆，提供个性化的回答
                        4. 回答要准确、清晰、有帮助
                        5. 使用中文回答"""
        
        # 如果有用户记忆，添加到系统提示中
        if user_memories:
            memory_text = "\n\n用户相关记忆：\n"
            for i, memory in enumerate(user_memories[:5], 1):  # 最多使用5条记忆
                memory_text += f"{i}. {memory.get('content', '')}\n"
            base_prompt += memory_text
        
        return base_prompt


# 全局 LLM 服务实例
llm_service = LLMService()

