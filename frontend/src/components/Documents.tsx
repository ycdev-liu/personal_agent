import React, { useState } from 'react';
import { FileText, Plus, CheckCircle, XCircle } from 'lucide-react';
import { api, DocumentAddRequest } from '../api/client';

const Documents: React.FC = () => {
  const [texts, setTexts] = useState<string[]>(['']);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<{ success: boolean; message: string } | null>(null);

  const handleAddText = () => {
    setTexts([...texts, '']);
  };

  const handleTextChange = (index: number, value: string) => {
    const newTexts = [...texts];
    newTexts[index] = value;
    setTexts(newTexts);
  };

  const handleRemoveText = (index: number) => {
    if (texts.length > 1) {
      setTexts(texts.filter((_, i) => i !== index));
    }
  };

  const handleSubmit = async () => {
    const validTexts = texts.filter(text => text.trim());
    if (validTexts.length === 0) {
      setResult({ success: false, message: '请至少输入一个文档' });
      return;
    }

    setLoading(true);
    setResult(null);

    try {
      const request: DocumentAddRequest = {
        texts: validTexts,
        metadatas: validTexts.map(() => ({ source: 'manual' })),
      };

      const response = await api.addDocuments(request);
      setResult({ success: response.success, message: response.message });
      
      if (response.success) {
        setTexts(['']);
      }
    } catch (error: any) {
      setResult({
        success: false,
        message: error.response?.data?.detail || error.message,
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="documents-container">
      <div className="documents-header">
        <FileText size={24} />
        <h2>知识库管理</h2>
      </div>

      <div className="documents-content">
        <p className="description">
          添加文档到知识库，系统会自动分块并生成向量索引，用于 RAG 检索。
        </p>

        <div className="texts-list">
          {texts.map((text, index) => (
            <div key={index} className="text-item">
              <textarea
                className="text-input"
                value={text}
                onChange={(e) => handleTextChange(index, e.target.value)}
                placeholder={`文档 ${index + 1}...`}
                rows={4}
              />
              {texts.length > 1 && (
                <button
                  className="remove-button"
                  onClick={() => handleRemoveText(index)}
                >
                  <XCircle size={20} />
                </button>
              )}
            </div>
          ))}
        </div>

        <div className="actions">
          <button className="add-button" onClick={handleAddText}>
            <Plus size={20} />
            添加更多文档
          </button>
        </div>

        {result && (
          <div className={`result ${result.success ? 'success' : 'error'}`}>
            {result.success ? <CheckCircle size={20} /> : <XCircle size={20} />}
            <span>{result.message}</span>
          </div>
        )}

        <button
          className="submit-button"
          onClick={handleSubmit}
          disabled={loading || texts.every(t => !t.trim())}
        >
          {loading ? '添加中...' : '添加到知识库'}
        </button>
      </div>

      <style>{`
        .documents-container {
          background: white;
          border-radius: 8px;
          padding: 24px;
        }

        .documents-header {
          display: flex;
          align-items: center;
          gap: 12px;
          margin-bottom: 20px;
        }

        .documents-header h2 {
          font-size: 20px;
          font-weight: 600;
        }

        .description {
          color: #6c757d;
          margin-bottom: 20px;
          font-size: 14px;
        }

        .texts-list {
          display: flex;
          flex-direction: column;
          gap: 12px;
          margin-bottom: 16px;
        }

        .text-item {
          position: relative;
        }

        .text-input {
          width: 100%;
          padding: 12px;
          border: 1px solid #e5e5e5;
          border-radius: 8px;
          font-size: 14px;
          font-family: inherit;
          resize: vertical;
        }

        .text-input:focus {
          outline: none;
          border-color: #007bff;
        }

        .remove-button {
          position: absolute;
          top: 8px;
          right: 8px;
          background: #dc3545;
          color: white;
          border: none;
          border-radius: 50%;
          width: 28px;
          height: 28px;
          display: flex;
          align-items: center;
          justify-content: center;
          cursor: pointer;
        }

        .remove-button:hover {
          background: #c82333;
        }

        .actions {
          margin-bottom: 16px;
        }

        .add-button {
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 8px 16px;
          background: #f8f9fa;
          border: 1px dashed #dee2e6;
          border-radius: 8px;
          cursor: pointer;
          font-size: 14px;
        }

        .add-button:hover {
          background: #e9ecef;
        }

        .result {
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 12px;
          border-radius: 8px;
          margin-bottom: 16px;
          font-size: 14px;
        }

        .result.success {
          background: #d4edda;
          color: #155724;
        }

        .result.error {
          background: #f8d7da;
          color: #721c24;
        }

        .submit-button {
          width: 100%;
          padding: 12px;
          background: #007bff;
          color: white;
          border: none;
          border-radius: 8px;
          font-size: 16px;
          font-weight: 500;
          cursor: pointer;
        }

        .submit-button:hover:not(:disabled) {
          background: #0056b3;
        }

        .submit-button:disabled {
          background: #ccc;
          cursor: not-allowed;
        }
      `}</style>
    </div>
  );
};

export default Documents;

