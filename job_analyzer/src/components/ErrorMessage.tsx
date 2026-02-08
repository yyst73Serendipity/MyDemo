import React from 'react';
import { Alert, Button } from 'antd';

/**
 * 错误提示组件
 */

interface ErrorMessageProps {
  /** 错误消息 */
  message: string;
  /** 重试回调 */
  onRetry?: () => void;
}

/**
 * 错误提示组件
 */
export const ErrorMessage: React.FC<ErrorMessageProps> = ({ message, onRetry }) => {
  return (
    <Alert
      message="分析失败"
      description={
        <div>
          <div style={{ marginBottom: 8 }}>{message}</div>
          {onRetry && (
            <Button size="small" onClick={onRetry}>
              重试
            </Button>
          )}
        </div>
      }
      type="error"
      showIcon
      style={{ marginBottom: 16 }}
    />
  );
};
