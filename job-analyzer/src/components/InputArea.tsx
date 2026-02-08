import React from 'react';
import { Input, Button, Space } from 'antd';

const { TextArea } = Input;

/**
 * 输入区域组件
 */

interface InputAreaProps {
  /** 输入值 */
  value: string;
  /** 值变化回调 */
  onChange: (value: string) => void;
  /** 是否加载中 */
  loading?: boolean;
  /** 开始分析回调 */
  onAnalyze: () => void;
}

/**
 * 输入区域组件
 */
export const InputArea: React.FC<InputAreaProps> = ({
  value,
  onChange,
  loading = false,
  onAnalyze
}) => {
  const handleClear = () => {
    onChange('');
  };

  const handleAnalyze = () => {
    if (value.trim()) {
      onAnalyze();
    }
  };

  return (
    <div>
      <TextArea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder="请粘贴职位描述..."
        rows={10}
        maxLength={10000}
        showCount
        disabled={loading}
        style={{ marginBottom: 16 }}
      />
      <Space>
        <Button onClick={handleClear} disabled={loading || !value}>
          清空
        </Button>
        <Button
          type="primary"
          onClick={handleAnalyze}
          loading={loading}
          disabled={!value.trim()}
        >
          开始分析
        </Button>
      </Space>
    </div>
  );
};
