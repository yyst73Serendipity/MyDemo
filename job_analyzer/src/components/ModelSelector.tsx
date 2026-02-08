import React from 'react';
import { Select } from 'antd';
import { ModelId } from '../types';
import { getAvailableModels } from '../services/apiService';

/**
 * 模型选择器组件
 */

interface ModelSelectorProps {
  /** 当前选中的模型ID */
  value: ModelId;
  /** 选择变化回调 */
  onChange: (modelId: ModelId) => void;
}

/**
 * 模型选择器组件
 */
export const ModelSelector: React.FC<ModelSelectorProps> = ({ value, onChange }) => {
  const availableModels = getAvailableModels();

  return (
    <div style={{ marginBottom: 16 }}>
      <div style={{ marginBottom: 8, fontSize: 14, fontWeight: 500 }}>
        模型选择：
      </div>
      <Select
        value={value}
        onChange={onChange}
        style={{ width: '100%', maxWidth: 400 }}
        placeholder="请选择模型"
        options={availableModels.map((model) => ({
          value: model.id,
          label: model.displayName,
          disabled: !model.available
        }))}
      />
      {availableModels.length === 0 && (
        <div style={{ color: '#999', fontSize: 12, marginTop: 4 }}>
          未配置DMXAPI API密钥，请在 .env.local 文件中配置 VITE_DMXAPI_API_KEY
        </div>
      )}
    </div>
  );
};
