import React, { useState, useRef, useEffect } from 'react';
import { FileText, Plus, CheckCircle, XCircle, Upload, X, Trash2, RefreshCw } from 'lucide-react';
import { api, DocumentAddRequest, DocumentItem } from '../api/client';

const Documents: React.FC = () => {
  const [texts, setTexts] = useState<string[]>(['']);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<{ success: boolean; message: string } | null>(null);
  const [uploadedFiles, setUploadedFiles] = useState<Array<{ name: string; content: string }>>([]);
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [loadingDocuments, setLoadingDocuments] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // 支持的文件类型
  const acceptedFileTypes = ['.txt', '.md', '.csv', '.json'];
  const maxFileSize = 10 * 1024 * 1024; // 10MB

  // 加载文档列表
  const loadDocuments = async () => {
    setLoadingDocuments(true);
    try {
      const response = await api.getDocuments(1000);
      if (response.success) {
        setDocuments(response.documents);
      }
    } catch (error) {
      console.error("加载文档列表失败:", error);
      setResult({
        success: false,
        message: "加载文档列表失败，请稍后重试"
      });
    } finally {
      setLoadingDocuments(false);
    }
  };

  useEffect(() => {
    loadDocuments();
  }, []);

  // 删除文档
// 删除文档
const handleDeleteDocument = async (id: string) => {
  if (!confirm("确定要删除这个文档吗？")) return;

  try {
    const response = await api.deleteDocuments({ ids: [id]});
    if (response.success) {
      setResult({ success: true, message: response.message });
      // 重新加载文档列表
      await loadDocuments();
      // 3秒后清除成功消息
      setTimeout(() => setResult(null), 3000);
    } else {
      setResult({
        success: false,
        message: response.message || "删除失败"
      });
    }
  } catch (error: any) {
    setResult({
      success: false,
      message: error.response?.data?.detail || error.message || "删除失败"
    });
  }
};






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

  const handleFileSelect = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (!files || files.length === 0) return;

    const newFiles: Array<{ name: string; content: string }> = [];

    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      
      // 检查文件类型
      const fileExtension = '.' + file.name.split('.').pop()?.toLowerCase();
      if (!acceptedFileTypes.includes(fileExtension)) {
        setResult({
          success: false,
          message: `不支持的文件类型: ${file.name}。支持的类型: ${acceptedFileTypes.join(', ')}`,
        });
        continue;
      }

      // 检查文件大小
      if (file.size > maxFileSize) {
        setResult({
          success: false,
          message: `文件 ${file.name} 太大（最大 ${maxFileSize / 1024 / 1024}MB）`,
        });
        continue;
      }

      try {
        const content = await readFileContent(file);
        newFiles.push({ name: file.name, content });
      } catch (error: any) {
        setResult({
          success: false,
          message: `读取文件 ${file.name} 失败: ${error.message}`,
        });
      }
    }

    if (newFiles.length > 0) {
      setUploadedFiles([...uploadedFiles, ...newFiles]);
      // 将文件内容添加到文本列表
      const fileContents = newFiles.map(f => f.content);
      setTexts([...texts, ...fileContents]);
      setResult({
        success: true,
        message: `成功上传 ${newFiles.length} 个文件`,
      });
    }

    // 重置文件输入
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const readFileContent = (file: File): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      
      reader.onload = (e) => {
        const content = e.target?.result as string;
        resolve(content);
      };
      
      reader.onerror = () => {
        reject(new Error('文件读取失败'));
      };
      
      // 读取为文本
      reader.readAsText(file, 'UTF-8');
    });
  };

  const handleRemoveUploadedFile = (index: number) => {
    const fileToRemove = uploadedFiles[index];
    setUploadedFiles(uploadedFiles.filter((_, i) => i !== index));
    
    // 从文本列表中移除对应的内容
    const fileIndex = texts.findIndex((text) => {
      // 找到对应文件内容的位置
      return text === fileToRemove.content;
    });
    
    if (fileIndex !== -1) {
      const newTexts = texts.filter((_, i) => i !== fileIndex);
      if (newTexts.length === 0) {
        setTexts(['']);
      } else {
        setTexts(newTexts);
      }
    }
  };

  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };

  const handleSubmit = async () => {
    const validTexts = texts.filter(text => text.trim());
    if (validTexts.length === 0) {
      setResult({ success: false, message: '请至少输入一个文档或上传一个文件' });
      return;
    }

    setLoading(true);
    setResult(null);

    try {
      const request: DocumentAddRequest = {
        texts: validTexts,
        metadatas: validTexts.map((text) => {
          // 如果是上传的文件，在 metadata 中记录文件名
          const fileInfo = uploadedFiles.find(f => f.content === text);
          return {
            source: fileInfo ? 'file' : 'manual',
            filename: fileInfo?.name || undefined,
          };
        }),
      };

      const response = await api.addDocuments(request);
      setResult({ success: response.success, message: response.message });
      
      if (response.success) {
        setTexts(['']);
        setUploadedFiles([]);
        loadDocuments(); // 添加成功后刷新列表
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
        <button 
          className="refresh-button" 
          onClick={loadDocuments} 
          disabled={loadingDocuments}
          title="刷新文档列表"
        >
          <RefreshCw size={20} className={loadingDocuments ? 'spinning' : ''} />
          刷新
        </button>
      </div>

      {/* 文档列表区域 */}
      <div className="documents-list-section">
        <h3>已添加的文档 ({documents.length})</h3>
        {loadingDocuments ? (
          <div className="loading">加载中...</div>
        ) : documents.length === 0 ? (
          <div className="empty-state">暂无文档，请添加文档到知识库</div>
        ) : (
          <div className="documents-list">
            {documents.map((doc) => (
              <div key={doc.id} className="document-item">
                <div className="document-content">
                  <div className="document-text">
                    {doc.text.length > 150 
                      ? `${doc.text.substring(0, 150)}...` 
                      : doc.text}
                  </div>
                  <div className="document-meta">
                    {doc.metadata?.filename && (
                      <span className="document-filename">
                        <FileText size={12} />
                        {doc.metadata.filename}
                      </span>
                    )}
                    {doc.metadata?.source && (
                      <span className="document-source">
                        来源: {doc.metadata.source === 'file' ? '文件' : '手动输入'}
                      </span>
                    )}
                    <span className="document-id">ID: {doc.id}</span>
                  </div>
                </div>
                <button
                  className="delete-document-button"
                  onClick={() => handleDeleteDocument(doc.id)}
                  title="删除文档"
                >
                  <Trash2 size={16} />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* 添加文档区域 */}
      <div className="add-documents-section">
        <h3>添加新文档</h3>
        <div className="documents-content">
          <p className="description">
            添加文档到知识库，系统会自动分块并生成向量索引，用于 RAG 检索。
            支持手动输入或上传文件（.txt, .md, .csv, .json）。
          </p>

        {/* 文件上传区域 */}
        <div className="upload-section">
          <input
            ref={fileInputRef}
            type="file"
            multiple
            accept={acceptedFileTypes.join(',')}
            onChange={handleFileSelect}
            style={{ display: 'none' }}
          />
          <button className="upload-button" onClick={handleUploadClick}>
            <Upload size={20} />
            上传文件
          </button>
          <span className="upload-hint">支持 {acceptedFileTypes.join(', ')} 格式，单个文件最大 10MB</span>
        </div>

        {/* 已上传文件列表 */}
        {uploadedFiles.length > 0 && (
          <div className="uploaded-files">
            <h3>已上传的文件：</h3>
            {uploadedFiles.map((file, index) => (
              <div key={index} className="uploaded-file-item">
                <FileText size={16} />
                <span>{file.name}</span>
                <button
                  className="remove-file-button"
                  onClick={() => handleRemoveUploadedFile(index)}
                >
                  <X size={16} />
                </button>
              </div>
            ))}
          </div>
        )}

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
          flex: 1;
          font-size: 20px;
          font-weight: 600;
        }

        .refresh-button {
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 8px 16px;
          background: #6c757d;
          color: white;
          border: none;
          border-radius: 8px;
          cursor: pointer;
          font-size: 14px;
        }

        .refresh-button:hover:not(:disabled) {
          background: #5a6268;
        }

        .refresh-button:disabled {
          background: #ccc;
          cursor: not-allowed;
        }

        .spinning {
          animation: spin 1s linear infinite;
        }

        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }

        .documents-list-section {
          margin-bottom: 30px;
          padding: 20px;
          background: #f8f9fa;
          border-radius: 8px;
        }

        .documents-list-section h3 {
          font-size: 16px;
          font-weight: 600;
          margin-bottom: 16px;
          color: #495057;
        }

        .documents-list {
          display: flex;
          flex-direction: column;
          gap: 12px;
          max-height: 500px;
          overflow-y: auto;
        }

        .document-item {
          display: flex;
          align-items: flex-start;
          gap: 12px;
          padding: 12px;
          background: white;
          border: 1px solid #e5e5e5;
          border-radius: 8px;
          transition: box-shadow 0.2s;
        }

        .document-item:hover {
          box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        .document-content {
          flex: 1;
          min-width: 0;
        }

        .document-text {
          margin-bottom: 8px;
          color: #495057;
          line-height: 1.5;
          word-wrap: break-word;
        }

        .document-meta {
          display: flex;
          flex-wrap: wrap;
          gap: 8px;
          font-size: 12px;
          color: #6c757d;
        }

        .document-filename,
        .document-source,
        .document-id {
          display: flex;
          align-items: center;
          gap: 4px;
          padding: 4px 8px;
          background: #e9ecef;
          border-radius: 4px;
        }

        .delete-document-button {
          padding: 8px;
          background: #dc3545;
          color: white;
          border: none;
          border-radius: 4px;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          flex-shrink: 0;
        }

        .delete-document-button:hover {
          background: #c82333;
        }

        .add-documents-section {
          margin-top: 30px;
        }

        .add-documents-section h3 {
          font-size: 16px;
          font-weight: 600;
          margin-bottom: 16px;
          color: #495057;
        }

        .loading,
        .empty-state {
          text-align: center;
          padding: 40px;
          color: #6c757d;
        }

        .description {
          color: #6c757d;
          margin-bottom: 20px;
          font-size: 14px;
        }

        .upload-section {
          display: flex;
          flex-direction: column;
          gap: 8px;
          margin-bottom: 20px;
          padding: 16px;
          background: #f8f9fa;
          border: 2px dashed #dee2e6;
          border-radius: 8px;
        }

        .upload-button {
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 10px 20px;
          background: #007bff;
          color: white;
          border: none;
          border-radius: 8px;
          cursor: pointer;
          font-size: 14px;
          font-weight: 500;
          width: fit-content;
        }

        .upload-button:hover {
          background: #0056b3;
        }

        .upload-hint {
          font-size: 12px;
          color: #6c757d;
        }

        .uploaded-files {
          margin-bottom: 20px;
          padding: 12px;
          background: #f8f9fa;
          border-radius: 8px;
        }

        .uploaded-files h3 {
          font-size: 14px;
          font-weight: 600;
          margin-bottom: 8px;
          color: #495057;
        }

        .uploaded-file-item {
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 8px;
          background: white;
          border-radius: 4px;
          margin-bottom: 4px;
        }

        .uploaded-file-item span {
          flex: 1;
          font-size: 14px;
          color: #495057;
        }

        .remove-file-button {
          background: none;
          border: none;
          color: #dc3545;
          cursor: pointer;
          padding: 4px;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .remove-file-button:hover {
          background: #f8d7da;
          border-radius: 4px;
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