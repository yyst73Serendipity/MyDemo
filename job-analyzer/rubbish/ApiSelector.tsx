import React from 'react';
import { Radio, Space } from 'antd';
import { ApiProvider, ApiProviderInfo } from '../types';
import { isApiAvailable } from '../services/apiService';

/**
 * API选择器组件
 */

interface ApiSelectorProps {
  /** 当前选中的API */
  value: ApiProvider;
  /** 选择变化回调 */
  onChange: (provider: ApiProvider) => void;
}

/**
 * API提供商配置信息
 */
const API_PROVIDERS: ApiProviderInfo[] = [
  {
    value: 'gemini',
    label: 'Gemini',
    available: isApiAvailable('gemini')
  },
  {
    value: 'openai',
    label: 'GPT',
    available: isApiAvailable('openai')
  },
  {
    value: 'deepseek',
    label: 'DeepSeek',
    available: isApiAvailable('deepseek')
  }
];

/**
 * API选择器组件
 */
export const ApiSelector: React.FC<ApiSelectorProps> = ({ value, onChange }) => {
  return (
    <div style={{ marginBottom: 16 }}>
      <div style={{ marginBottom: 8, fontSize: 14, fontWeight: 500 }}>
        API选择：
      </div>
      <Radio.Group value={value} onChange={(e) => onChange(e.target.value)}>
        <Space>
          {API_PROVIDERS.map((provider) => (
            <Radio
              key={provider.value}
              value={provider.value}
              disabled={!provider.available}
            >
              {provider.label}
              {!provider.available && (
                <span style={{ color: '#999', fontSize: 12, marginLeft: 4 }}>
                  (未配置)
                </span>
              )}
            </Radio>
          ))}
        </Space>
      </Radio.Group>
    </div>
  );
};
