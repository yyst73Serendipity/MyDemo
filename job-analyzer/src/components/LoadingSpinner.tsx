import React from 'react';
import { Spin, Typography } from 'antd';
import { ModelId } from '../types';
import { getModelConfig } from '../services/apiService';

const { Text } = Typography;

/**
 * 加载动画组件
 */

interface LoadingSpinnerProps {
  /** 使用的模型ID */
  modelId?: ModelId;
}

/**
 * 获取模型显示名称
 */
function getModelDisplayName(modelId?: ModelId): string {
  if (!modelId) return 'AI';
  const config = getModelConfig(modelId);
  return config?.displayName || 'AI';
}

/**
 * 加载动画组件
 */
export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({ modelId }) => {
  const modelName = getModelDisplayName(modelId);

  return (
    <div style={{ textAlign: 'center', padding: '40px 0' }}>
      <Spin size="large" />
      <div style={{ marginTop: 16 }}>
        <Text>正在使用 {modelName} 分析中，请稍候...</Text>
      </div>
    </div>
  );
};
