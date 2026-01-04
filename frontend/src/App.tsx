import React, { useState, useEffect } from 'react';
import { MessageSquare, FileText, Brain, Activity } from 'lucide-react';

import Chat from './components/Chat';
import Documents from './components/Documents';
import Memories from './components/Memories';

import { api } from './api/client';

type Tab = 'chat' | 'documents' | 'memories';

const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<Tab>('chat');
  const [userId] = useState(() => {
    const stored = localStorage.getItem('userId');
    return stored || `user_${Date.now()}`;
  });
  const [health, setHealth] = useState<any>(null);

  useEffect(() => {
    localStorage.setItem('userId', userId);
    checkHealth();
    const interval = setInterval(checkHealth, 30000); // 每30秒检查一次
    return () => clearInterval(interval);
  }, []);

  const checkHealth = async () => {
    try {
      const response = await api.healthCheck();
      setHealth(response);
    } catch (error) {
      setHealth({ status: 'unhealthy', error: '无法连接到服务器' });
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <h1>个人知识库智能助手</h1>
          <div className="health-status">
            <Activity size={16} />
            <span className={health?.status === 'healthy' ? 'healthy' : 'unhealthy'}>
              {health?.status === 'healthy' ? '运行正常' : '服务异常'}
            </span>
            {health?.milvus && (
              <span className="milvus-info">
                Milvus: {health.milvus.total_documents} 文档
              </span>
            )}
          </div>
        </div>
      </header>

      <div className="app-body">
        <nav className="sidebar">
          <button
            className={`nav-item ${activeTab === 'chat' ? 'active' : ''}`}
            onClick={() => setActiveTab('chat')}
          >
            <MessageSquare size={20} />
            <span>对话</span>
          </button>
          <button
            className={`nav-item ${activeTab === 'documents' ? 'active' : ''}`}
            onClick={() => setActiveTab('documents')}
          >
            <FileText size={20} />
            <span>知识库</span>
          </button>
          <button
            className={`nav-item ${activeTab === 'memories' ? 'active' : ''}`}
            onClick={() => setActiveTab('memories')}
          >
            <Brain size={20} />
            <span>记忆</span>
          </button>
        </nav>

        <main className="main-content">
          {activeTab === 'chat' && <Chat userId={userId} />}
          {activeTab === 'documents' && <Documents />}
          {activeTab === 'memories' && <Memories userId={userId} />}
        </main>
      </div>

      <style>{` 
        .app {
          display: flex;
          flex-direction: column;
          height: 100vh;
          overflow: hidden;
        }

        .app-header {
          background: #fff;
          border-bottom: 1px solid #e5e5e5;
          padding: 16px 24px;
          box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        .header-content {
          max-width: 1400px;
          margin: 0 auto;
          display: flex;
          justify-content: space-between;
          align-items: center;
        }

        .app-header h1 {
          font-size: 24px;
          font-weight: 600;
          margin: 0;
        }

        .health-status {
          display: flex;
          align-items: center;
          gap: 12px;
          font-size: 14px;
        }

        .health-status .healthy {
          color: #28a745;
        }

        .health-status .unhealthy {
          color: #dc3545;
        }

        .milvus-info {
          color: #6c757d;
          font-size: 12px;
        }

        .app-body {
          flex: 1;
          display: flex;
          overflow: hidden;
        }

        .sidebar {
          width: 200px;
          background: #f8f9fa;
          border-right: 1px solid #e5e5e5;
          padding: 20px 0;
          display: flex;
          flex-direction: column;
          gap: 4px;
        }

        .nav-item {
          display: flex;
          align-items: center;
          gap: 12px;
          padding: 12px 20px;
          border: none;
          background: transparent;
          cursor: pointer;
          font-size: 14px;
          color: #495057;
          transition: all 0.2s;
        }

        .nav-item:hover {
          background: #e9ecef;
        }

        .nav-item.active {
          background: #007bff;
          color: white;
        }

        .main-content {
          flex: 1;
          padding: 24px;
          overflow-y: auto;
          background: #f5f5f5;
        }

        @media (max-width: 768px) {
          .sidebar {
            width: 80px;
          }

          .nav-item span {
            display: none;
          }

          .header-content {
            flex-direction: column;
            gap: 12px;
            align-items: flex-start;
          }
        }
      `}</style>
     </div>
  );
};

export default App;

