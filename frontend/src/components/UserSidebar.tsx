import React, { useState, useEffect } from 'react';
import { Plus, User as UserIcon, MessageSquare, Trash2 } from 'lucide-react';
import { api, User, Conversation } from '../api/client';

interface UserSidebarProps {
  currentUserId: string | null;
  currentConversationId: string | null;
  onUserSelect: (userId: string) => void;
  onConversationSelect: (conversationId: string, userId: string) => void;
  onNewConversation: (userId: string) => void;
}

const UserSidebar: React.FC<UserSidebarProps> = ({
  currentUserId,
  currentConversationId,
  onUserSelect,
  onConversationSelect,
  onNewConversation,
}) => {
  const [users, setUsers] = useState<User[]>([]);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [showUserForm, setShowUserForm] = useState(false);
  const [newUserName, setNewUserName] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadUsers();
  }, []);

  useEffect(() => {
    if (currentUserId) {
      loadConversations(currentUserId);
    }
  }, [currentUserId]);

  const loadUsers = async () => {
    try {
      const response = await api.getUsers();
      setUsers(response.users);
      if (response.users.length > 0 && !currentUserId) {
        onUserSelect(response.users[0].id);
      }
    } catch (error) {
      console.error('加载用户失败:', error);
    }
  };

  const loadConversations = async (userId: string) => {
    try {
      const response = await api.getConversations(userId);
      setConversations(response.conversations);
    } catch (error) {
      console.error('加载对话失败:', error);
    }
  };

  const handleCreateUser = async () => {
    if (!newUserName.trim()) return;
    
    setLoading(true);
    try {
      const user = await api.createUser({ name: newUserName });
      setUsers([...users, user]);
      setNewUserName('');
      setShowUserForm(false);
      onUserSelect(user.id);
    } catch (error) {
      console.error('创建用户失败:', error);
      alert('创建用户失败');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateConversation = async () => {
    if (!currentUserId) return;
    
    setLoading(true);
    try {
      const conversation = await api.createConversation({ user_id: currentUserId });
      setConversations([conversation, ...conversations]);
      onConversationSelect(conversation.id, currentUserId);
    } catch (error) {
      console.error('创建对话失败:', error);
      alert('创建对话失败');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteUser = async (userId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!confirm('确定要删除这个用户及其所有对话吗？')) return;
    
    try {
      await api.deleteUser(userId);
      setUsers(users.filter(u => u.id !== userId));
      if (currentUserId === userId) {
        if (users.length > 1) {
          const nextUser = users.find(u => u.id !== userId);
          if (nextUser) {
            onUserSelect(nextUser.id);
          }
        } else {
          onUserSelect('');
        }
      }
    } catch (error) {
      console.error('删除用户失败:', error);
      alert('删除用户失败');
    }
  };

  const handleDeleteConversation = async (conversationId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!confirm('确定要删除这个对话吗？')) return;
    
    try {
      await api.deleteConversation(conversationId);
      setConversations(conversations.filter(c => c.id !== conversationId));
      if (currentConversationId === conversationId) {
        // 切换到其他对话或创建新对话
        const remaining = conversations.filter(c => c.id !== conversationId);
        if (remaining.length > 0) {
          onConversationSelect(remaining[0].id, remaining[0].user_id);
        } else if (currentUserId) {
          onNewConversation(currentUserId);
        }
      }
    } catch (error) {
      console.error('删除对话失败:', error);
      alert('删除对话失败');
    }
  };

  return (
    <div className="user-sidebar">
      <div className="sidebar-section">
        <div className="section-header">
          <h3>用户</h3>
          <button
            className="icon-button"
            onClick={() => setShowUserForm(!showUserForm)}
            title="新建用户"
          >
            <Plus size={16} />
          </button>
        </div>
        
        {showUserForm && (
          <div className="user-form">
            <input
              type="text"
              placeholder="输入用户名"
              value={newUserName}
              onChange={(e) => setNewUserName(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleCreateUser()}
            />
            <button onClick={handleCreateUser} disabled={loading}>
              创建
            </button>
          </div>
        )}
        
        <div className="user-list">
          {users.map((user) => (
            <div
              key={user.id}
              className={`user-item ${currentUserId === user.id ? 'active' : ''}`}
              onClick={() => onUserSelect(user.id)}
            >
              <UserIcon size={16} />
              <span className="user-name">{user.name}</span>
              <span className="user-count">{user.conversation_count}</span>
              <button
                className="delete-button"
                onClick={(e) => handleDeleteUser(user.id, e)}
                title="删除用户"
              >
                <Trash2 size={14} />
              </button>
            </div>
          ))}
        </div>
      </div>

      {currentUserId && (
        <div className="sidebar-section">
          <div className="section-header">
            <h3>对话</h3>
            <button
              className="icon-button"
              onClick={handleCreateConversation}
              disabled={loading}
              title="新建对话"
            >
              <Plus size={16} />
            </button>
          </div>
          
          <div className="conversation-list">
            {conversations.map((conv) => (
              <div
                key={conv.id}
                className={`conversation-item ${currentConversationId === conv.id ? 'active' : ''}`}
                onClick={() => onConversationSelect(conv.id, conv.user_id)}
              >
                <MessageSquare size={16} />
                <span className="conversation-title">{conv.title}</span>
                <button
                  className="delete-button"
                  onClick={(e) => handleDeleteConversation(conv.id, e)}
                  title="删除对话"
                >
                  <Trash2 size={14} />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      <style>{`
        .user-sidebar {
          width: 250px;
          background: #f8f9fa;
          border-right: 1px solid #e5e5e5;
          display: flex;
          flex-direction: column;
          height: 100%;
          overflow-y: auto;
        }
        
        .sidebar-section {
          padding: 16px;
          border-bottom: 1px solid #e5e5e5;
        }
        
        .section-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 12px;
        }
        
        .section-header h3 {
          font-size: 14px;
          font-weight: 600;
          margin: 0;
        }
        
        .icon-button {
          background: none;
          border: none;
          cursor: pointer;
          padding: 4px;
          display: flex;
          align-items: center;
          color: #007bff;
        }
        
        .user-form {
          display: flex;
          gap: 8px;
          margin-bottom: 12px;
        }
        
        .user-form input {
          flex: 1;
          padding: 6px 10px;
          border: 1px solid #ddd;
          border-radius: 4px;
          font-size: 13px;
        }
        
        .user-form button {
          padding: 6px 12px;
          background: #007bff;
          color: white;
          border: none;
          border-radius: 4px;
          cursor: pointer;
          font-size: 13px;
        }
        
        .user-list, .conversation-list {
          display: flex;
          flex-direction: column;
          gap: 4px;
        }
        
        .user-item, .conversation-item {
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 8px 12px;
          border-radius: 6px;
          cursor: pointer;
          transition: background 0.2s;
        }
        
        .user-item:hover, .conversation-item:hover {
          background: #e9ecef;
        }
        
        .user-item.active, .conversation-item.active {
          background: #007bff;
          color: white;
        }
        
        .user-name, .conversation-title {
          flex: 1;
          font-size: 13px;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }
        
        .user-count {
          font-size: 11px;
          color: #999;
        }
        
        .user-item.active .user-count {
          color: rgba(255, 255, 255, 0.8);
        }
        
        .delete-button {
          background: none;
          border: none;
          cursor: pointer;
          padding: 4px;
          display: flex;
          align-items: center;
          color: #dc3545;
          opacity: 0.6;
        }
        
        .delete-button:hover {
          opacity: 1;
        }
        
        .user-item.active .delete-button {
          color: white;
        }
      `}</style>
    </div>
  );
};

export default UserSidebar;