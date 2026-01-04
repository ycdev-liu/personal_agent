import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Loader2 } from 'lucide-react';
import { api, ChatRequest, ChatResponse } from '../api/client';


// 创建消息模版
interface Message {
  role: 'user' | 'assistant';
  content: string;
  sources?: ChatResponse['sources'];
  memories?: ChatResponse['memories_used'];
  timestamp: Date;
}

interface ChatProps {
  userId: string;
}

const Chat: React.FC<ChatProps> = ({ userId }) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [useMemory, setUseMemory] = useState(true);
  const [useRag, setUseRag] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userMessage: Message = {
      role: 'user',
      content: input,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const request: ChatRequest = {
        user_id: userId,
        message: input,
        use_memory: useMemory,
        use_rag: useRag,
      };

      // 得到回答

      const response = await api.chat(request);

      //  生成消息
      const assistantMessage: Message = {
        role: 'assistant',
        content: response.response,
        sources: response.sources,
        memories: response.memories_used,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error: any) {
      const errorMessage: Message = {
        role: 'assistant',
        content: `错误: ${error.response?.data?.detail || error.message}`,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="chat-container">
      <div className="chat-header">
        <h2>智能对话</h2>
        <div className="chat-options">
          
          <label>
            <input
              type="checkbox"
              checked={useMemory}
              onChange={(e) => setUseMemory(e.target.checked)}
            />
            使用记忆
          </label>
          <label>
            <input
              type="checkbox"
              checked={useRag}
              onChange={(e) => setUseRag(e.target.checked)}
            />
            使用 RAG
          </label>
        </div>
      </div>

      <div className="messages-container">
        {messages.length === 0 && (
          <div className="empty-state">
            <Bot size={48} />
            <p>开始对话吧！我可以基于知识库和你的记忆为你提供帮助。</p>
          </div>
        )}

        {messages.map((message, index) => (
          <div key={index} className={`message ${message.role}`}>
            <div className="message-avatar">
              {message.role === 'user' ? <User size={20} /> : <Bot size={20} />}
            </div>
            <div className="message-content">
              <div className="message-text">{message.content}</div>
              
              {message.sources && message.sources.length > 0 && (
                <div className="message-sources">
                  <strong>知识库来源 ({message.sources.length}):</strong>
                  {message.sources.map((source, idx) => (
                    <div key={idx} className="source-item">
                      <span className="source-text">{source.text.substring(0, 100)}...</span>
                      <span className="source-score">相似度: {(source.score * 100).toFixed(1)}%</span>
                    </div>
                  ))}
                </div>
              )}

              {message.memories && message.memories.length > 0 && (
                <div className="message-memories">
                  <strong>使用的记忆 ({message.memories.length}):</strong>
                  {message.memories.map((memory, idx) => (
                    <div key={idx} className="memory-item">
                      {memory.content} (重要性: {(memory.importance * 100).toFixed(0)}%)
                    </div>
                  ))}
                </div>
              )}

              <div className="message-time">
                {message.timestamp.toLocaleTimeString()}
              </div>
            </div>
          </div>
        ))}

        {loading && (
          <div className="message assistant">
            <div className="message-avatar">
              <Bot size={20} />
            </div>
            <div className="message-content">
              <Loader2 className="loader" size={20} />
              <span>思考中...</span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input-container">
        <textarea
          className="chat-input"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="输入消息..."
          rows={1}
        />
        <button
          className="send-button"
          onClick={handleSend}
          disabled={!input.trim() || loading}
        >
          <Send size={20} />
        </button>
      </div>

      <style>{`
        .chat-container {
          display: flex;
          flex-direction: column;
          height: 100%;
          background: white;
          border-radius: 8px;
          overflow: hidden;
        }

        .chat-header {
          padding: 16px 20px;
          border-bottom: 1px solid #e5e5e5;
          display: flex;
          justify-content: space-between;
          align-items: center;
        }

        .chat-header h2 {
          font-size: 20px;
          font-weight: 600;
        }

        .chat-options {
          display: flex;
          gap: 16px;
        }

        .chat-options label {
          display: flex;
          align-items: center;
          gap: 6px;
          font-size: 14px;
          cursor: pointer;
        }

        .messages-container {
          flex: 1;
          overflow-y: auto;
          padding: 20px;
          display: flex;
          flex-direction: column;
          gap: 16px;
        }

        .empty-state {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          height: 100%;
          color: #999;
          text-align: center;
        }

        .empty-state p {
          margin-top: 16px;
          font-size: 14px;
        }

        .message {
          display: flex;
          gap: 12px;
          max-width: 80%;
        }

        .message.user {
          align-self: flex-end;
          flex-direction: row-reverse;
        }

        .message-avatar {
          width: 32px;
          height: 32px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          flex-shrink: 0;
        }

        .message.user .message-avatar {
          background: #007bff;
          color: white;
        }

        .message.assistant .message-avatar {
          background: #e9ecef;
          color: #495057;
        }

        .message-content {
          flex: 1;
          display: flex;
          flex-direction: column;
          gap: 8px;
        }

        .message-text {
          padding: 12px 16px;
          border-radius: 12px;
          line-height: 1.5;
          white-space: pre-wrap;
        }

        .message.user .message-text {
          background: #007bff;
          color: white;
        }

        .message.assistant .message-text {
          background: #f8f9fa;
          color: #212529;
        }

        .message-sources,
        .message-memories {
          margin-top: 8px;
          padding: 8px 12px;
          background: #f8f9fa;
          border-radius: 8px;
          font-size: 12px;
        }

        .source-item,
        .memory-item {
          margin-top: 4px;
          padding: 4px 0;
          border-top: 1px solid #e9ecef;
        }

        .source-text {
          display: block;
          color: #6c757d;
        }

        .source-score {
          display: block;
          color: #007bff;
          font-weight: 500;
          margin-top: 2px;
        }

        .message-time {
          font-size: 11px;
          color: #999;
          margin-top: 4px;
        }

        .loader {
          animation: spin 1s linear infinite;
        }

        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }

        .chat-input-container {
          padding: 16px 20px;
          border-top: 1px solid #e5e5e5;
          display: flex;
          gap: 12px;
          align-items: flex-end;
        }

        .chat-input {
          flex: 1;
          padding: 12px 16px;
          border: 1px solid #e5e5e5;
          border-radius: 24px;
          font-size: 14px;
          resize: none;
          max-height: 120px;
          font-family: inherit;
        }

        .chat-input:focus {
          outline: none;
          border-color: #007bff;
        }

        .send-button {
          width: 44px;
          height: 44px;
          border-radius: 50%;
          border: none;
          background: #007bff;
          color: white;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          flex-shrink: 0;
        }

        .send-button:hover:not(:disabled) {
          background: #0056b3;
        }

        .send-button:disabled {
          background: #ccc;
          cursor: not-allowed;
        }
      `}</style>
    </div>
  );
};

export default Chat;

