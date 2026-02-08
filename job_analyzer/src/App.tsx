import React, { useState } from 'react';
import { Layout, Typography, message } from 'antd';
import { ModelId, AnalysisResult } from './types';
import { analyzeJobDescription, getAvailableModels, getDmxApiConfig } from './services/apiService';
import { ModelSelector } from './components/ModelSelector';
import { InputArea } from './components/InputArea';
import { ResultTable } from './components/ResultTable';
import { LoadingSpinner } from './components/LoadingSpinner';
import { ErrorMessage } from './components/ErrorMessage';
import './styles/index.css';

const { Header, Content } = Layout;
const { Title } = Typography;

/**
 * 主应用组件
 */
const App: React.FC = () => {
  // 状态管理
  const [selectedModelId, setSelectedModelId] = useState<ModelId>(() => {
    // 默认选择第一个可用的模型
    const availableModels = getAvailableModels();
    const firstAvailable = availableModels.find(model => model.available);
    return firstAvailable?.id || 'gpt-5.1'; // 默认值：GPT-5.1
  });
  const [inputText, setInputText] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  /**
   * 处理模型选择变化
   */
  const handleModelChange = (modelId: ModelId) => {
    const dmxConfig = getDmxApiConfig();
    if (!dmxConfig) {
      message.warning('未配置DMXAPI API密钥，请在 .env.local 文件中配置 VITE_DMXAPI_API_KEY');
      return;
    }
    setSelectedModelId(modelId);
    setResult(null);
    setError(null);
  };

  /**
   * 处理分析请求
   */
  const handleAnalyze = async () => {
    // 检查输入
    if (!inputText.trim()) {
      message.warning('请输入职位描述');
      return;
    }

    // 检查API密钥（统一使用DMXAPI配置）
    const dmxConfig = getDmxApiConfig();
    if (!dmxConfig) {
      message.error('未配置DMXAPI API密钥，请在 .env.local 文件中配置 VITE_DMXAPI_API_KEY');
      return;
    }

    // 开始分析
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const analysisResult = await analyzeJobDescription({
        text: inputText.trim(),
        modelId: selectedModelId
      });
      setResult(analysisResult);
      message.success('分析完成');
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '分析失败，请重试';
      setError(errorMessage);
      message.error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  /**
   * 处理重试
   */
  const handleRetry = () => {
    handleAnalyze();
  };

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header style={{ background: '#fff', padding: '0 24px', boxShadow: '0 2px 8px rgba(0,0,0,0.1)' }}>
        <Title level={3} style={{ margin: '16px 0', color: '#1890ff' }}>
          岗位分析解读工具
        </Title>
      </Header>
      <Content style={{ padding: '24px', maxWidth: '1200px', margin: '0 auto', width: '100%' }}>
        <div style={{ background: '#fff', padding: '24px', borderRadius: '8px', boxShadow: '0 2px 8px rgba(0,0,0,0.1)' }}>
          {/* 模型选择器 */}
          <ModelSelector value={selectedModelId} onChange={handleModelChange} />

          {/* 输入区域 */}
          <InputArea
            value={inputText}
            onChange={setInputText}
            loading={loading}
            onAnalyze={handleAnalyze}
          />

          {/* 加载状态 */}
          {loading && <LoadingSpinner modelId={selectedModelId} />}

          {/* 错误提示 */}
          {error && !loading && (
            <ErrorMessage message={error} onRetry={handleRetry} />
          )}

          {/* 结果展示 */}
          {result && !loading && (
            <ResultTable 
              items={result.items} 
              provider={result.provider} 
              modelId={result.modelId}
            />
          )}
        </div>
      </Content>
    </Layout>
  );
};

export default App;
