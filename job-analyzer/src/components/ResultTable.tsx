import React, { useState } from 'react';
import { Table, Button, message, Dropdown } from 'antd';
import type { MenuProps } from 'antd';
import { AnalysisItem, ApiProvider, ModelId } from '../types';
import { copyTableAsHTML, copyTableAsMarkdown, copyTableAsPlainText } from '../utils/copyTable';
import { getModelConfig } from '../services/apiService';

/**
 * 结果表格组件
 */

interface ResultTableProps {
  /** 分析结果项 */
  items: AnalysisItem[];
  /** 使用的API提供商（保留用于向后兼容） */
  provider: ApiProvider;
  /** 使用的模型ID */
  modelId?: ModelId;
}

/**
 * 获取模型显示名称
 */
function getModelDisplayName(modelId?: ModelId, provider?: ApiProvider): string {
  if (modelId) {
    const config = getModelConfig(modelId);
    if (config) {
      return config.displayName;
    }
  }
  // 向后兼容：如果没有modelId，使用provider
  if (provider) {
    switch (provider) {
      case 'gemini':
        return 'Gemini';
      case 'openai':
        return 'GPT';
      case 'deepseek':
        return 'DeepSeek';
      case 'qwen':
        return 'Qwen';
      case 'kimi':
        return 'Kimi';
      default:
        return 'AI';
    }
  }
  return 'AI';
}

/**
 * 结果表格组件
 */
export const ResultTable: React.FC<ResultTableProps> = ({ items, provider, modelId }) => {
  const [copying, setCopying] = useState(false);

  // 定义表格列
  const columns = [
    {
      title: '职位描述原文',
      dataIndex: 'original',
      key: 'original',
      width: '33%',
      render: (text: string) => (
        <div style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>
          {text}
        </div>
      )
    },
    {
      title: '大白话解读',
      dataIndex: 'interpretation',
      key: 'interpretation',
      width: '33%',
      render: (text: string) => (
        <div style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>
          {text}
        </div>
      )
    },
    {
      title: '面试准备哪些问题',
      dataIndex: 'questions',
      key: 'questions',
      width: '34%',
      render: (text: string) => (
        <div
          style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}
          dangerouslySetInnerHTML={{ __html: text }}
        />
      )
    }
  ];

  const handleCopy = async (format: 'html' | 'markdown' | 'plain-text') => {
    setCopying(true);
    try {
      switch (format) {
        case 'html':
          await copyTableAsHTML(items);
          message.success('已复制为HTML格式');
          break;
        case 'markdown':
          await copyTableAsMarkdown(items);
          message.success('已复制为Markdown格式');
          break;
        case 'plain-text':
          await copyTableAsPlainText(items);
          message.success('已复制为纯文本格式');
          break;
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '复制失败';
      message.error(errorMessage);
    } finally {
      setCopying(false);
    }
  };

  const menuItems: MenuProps['items'] = [
    {
      key: 'html',
      label: 'HTML格式',
      onClick: () => handleCopy('html'),
    },
    {
      key: 'markdown',
      label: 'Markdown格式',
      onClick: () => handleCopy('markdown'),
    },
    {
      key: 'plain-text',
      label: '纯文本格式',
      onClick: () => handleCopy('plain-text'),
    },
  ];

  return (
    <div>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ fontSize: 14, color: '#666' }}>
          使用模型：{getModelDisplayName(modelId, provider)}
        </div>
        <Dropdown menu={{ items: menuItems }} trigger={['click']}>
          <Button type="primary" loading={copying}>
            复制表格
          </Button>
        </Dropdown>
      </div>
      <div style={{ marginBottom: 16 }}>
        <Table
          columns={columns}
          dataSource={items.map((item, index) => ({ ...item, key: index }))}
          pagination={false}
          bordered
          scroll={{ x: 'max-content' }}
        />
      </div>
    </div>
  );
};
