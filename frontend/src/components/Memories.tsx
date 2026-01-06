import React, { useState, useEffect } from 'react';
import { Brain, Plus, Trash2 } from 'lucide-react';
import { api, Memory, MemoryAddRequest } from '../api/client';

interface MemoriesProps {
  userId: string;
}

const Memories: React.FC<MemoriesProps> = ({ userId }) => {
  const [memories, setMemories] = useState<Memory[]>([]);
  const [loading, setLoading] = useState(false);
  const [showAddForm, setShowAddForm] = useState(false);
  const [formData, setFormData] = useState<MemoryAddRequest>({
    user_id: userId,
    content: '',
    memory_type: 'fact',
    importance: 0.5,
  });

  useEffect(() => {
    loadMemories();
  }, [userId]);

  const loadMemories = async () => {
    setLoading(true);
    try {
      const response = await api.getMemories(userId);
      if (response.success) {
        setMemories(response.memories);
      }
    } catch (error) {
      console.error('加载记忆失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.content.trim()) return;

    try {
      await api.addMemory(formData);
      setFormData({
        user_id: userId,
        content: '',
        memory_type: 'fact',
        importance: 0.5,
      });
      setShowAddForm(false);
      loadMemories();
    } catch (error: any) {
      alert(error.response?.data?.detail || error.message);
    }
  };
  const handleDelete = async (memoryId:string) => {
    if(!confirm("确定要删除这个记忆吗？")) return;
    try{await api.deleteMemory(userId,memoryId);
      loadMemories();
    }catch(error:any){
      alert(error.response?.data?.detail || error.message);
    }
  }

  return (
    <div className="memories-container">
      <div className="memories-header">
        <Brain size={24} />
        <h2>用户记忆</h2>
        <button className="add-button" onClick={() => setShowAddForm(!showAddForm)}>
          <Plus size={20} />
          添加记忆
        </button>
      </div>

      {showAddForm && (
        <form className="add-form" onSubmit={handleSubmit}>
          <textarea
            className="form-input"
            value={formData.content}
            onChange={(e) => setFormData({ ...formData, content: e.target.value })}
            placeholder="输入记忆内容..."
            rows={3}
            required
          />
          <div className="form-row">
            <div className="form-group">
              <label>类型</label>
              <select
                value={formData.memory_type}
                onChange={(e) => setFormData({ ...formData, memory_type: e.target.value })}
              >
                <option value="fact">事实</option>
                <option value="preference">偏好</option>
                <option value="event">事件</option>
              </select>
            </div>
            <div className="form-group">
              <label>重要性: {(formData.importance * 100).toFixed(0)}%</label>
              <input
                type="range"
                min="0"
                max="1"
                step="0.1"
                value={formData.importance}
                onChange={(e) => setFormData({ ...formData, importance: parseFloat(e.target.value) })}
              />
            </div>
          </div>
          <div className="form-actions">
            <button type="submit" className="submit-button">保存</button>
            <button type="button" className="cancel-button" onClick={() => setShowAddForm(false)}>
              取消
            </button>
          </div>
  

        </form>
      )}

      <div className="memories-list">
        {loading ? (
          <div className="loading">加载中...</div>
        ) : memories.length === 0 ? (
          <div className="empty-state">暂无记忆</div>
        ) : (
          memories.map((memory, index) => (
            <div key={index} className="memory-item">
              <div className="memory-content">{memory.content}</div>
              <div className="memory-meta">
                <button className ="delete-button" onClick={()=>handleDelete(memory.id)}>
                  <Trash2 size={16} />
                </button>
                <span className="memory-type">{memory.type}</span>
                <span className="memory-importance">
                  重要性: {(memory.importance * 100).toFixed(0)}%
                </span>
                {memory.timestamp && (
                  <span className="memory-time">
                    {new Date(memory.timestamp).toLocaleString()}
                  </span>
                )}
              </div>
            </div>
          ))
        )}
      </div>

      <style>{`
        .memories-container {
          background: white;
          border-radius: 8px;
          padding: 24px;
        }

        .memories-header {
          display: flex;
          align-items: center;
          gap: 12px;
          margin-bottom: 20px;
        }

        .memories-header h2 {
          flex: 1;
          font-size: 20px;
          font-weight: 600;
        }

        .add-button {
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 8px 16px;
          background: #007bff;
          color: white;
          border: none;
          border-radius: 8px;
          cursor: pointer;
          font-size: 14px;
        }

        .add-button:hover {
          background: #0056b3;
        }

        .add-form {
          padding: 16px;
          background: #f8f9fa;
          border-radius: 8px;
          margin-bottom: 20px;
        }

        .form-input {
          width: 100%;
          padding: 12px;
          border: 1px solid #e5e5e5;
          border-radius: 8px;
          font-size: 14px;
          font-family: inherit;
          margin-bottom: 12px;
        }

        .form-input:focus {
          outline: none;
          border-color: #007bff;
        }

        .form-row {
          display: grid;
          grid-template-columns: 1fr 2fr;
          gap: 12px;
          margin-bottom: 12px;
        }

        .form-group {
          display: flex;
          flex-direction: column;
          gap: 4px;
        }

        .form-group label {
          font-size: 12px;
          color: #6c757d;
        }

        .form-group select,
        .form-group input[type="range"] {
          padding: 8px;
          border: 1px solid #e5e5e5;
          border-radius: 4px;
        }

        .form-actions {
          display: flex;
          gap: 8px;
        }

        .submit-button,
        .cancel-button {
          padding: 8px 16px;
          border: none;
          border-radius: 8px;
          cursor: pointer;
          font-size: 14px;
        }

        .submit-button {
          background: #007bff;
          color: white;
        }

        .submit-button:hover {
          background: #0056b3;
        }

        .cancel-button {
          background: #6c757d;
          color: white;
        }

        .cancel-button:hover {
          background: #5a6268;
        }

        .memories-list {
          display: flex;
          flex-direction: column;
          gap: 12px;
        }

        .loading,
        .empty-state {
          text-align: center;
          padding: 40px;
          color: #6c757d;
        }

        .memory-item {
          padding: 16px;
          border: 1px solid #e5e5e5;
          border-radius: 8px;
        }

        .memory-content {
          margin-bottom: 8px;
          line-height: 1.5;
        }

        .memory-meta {
          display: flex;
          gap: 12px;
          font-size: 12px;
          color: #6c757d;
        }

        .memory-type {
          background: #e9ecef;
          padding: 2px 8px;
          border-radius: 4px;
        }

        .memory-importance {
          color: #007bff;
        }
      `}</style>
    </div>
  );
};

export default Memories;

