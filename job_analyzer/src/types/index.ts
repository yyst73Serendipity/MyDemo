/**
 * API提供商类型
 */
export type ApiProvider = 'gemini' | 'openai' | 'deepseek' | 'qwen' | 'kimi';

/**
 * 模型ID类型
 */
export type ModelId = 
  | 'gpt-5.1'
  | 'gpt-4o'
  | 'gemini-2.5-pro'
  | 'gemini-3-pro-preview'
  | 'deepseek-r1'
  | 'deepseek-v3'
  | 'qwen3-max'
  | 'qwen3-max-preview'
  | 'kimi-k2';

/**
 * 模型配置接口
 */
export interface ModelConfig {
  /** 唯一标识（用于代码中） */
  id: ModelId;
  /** 显示名称（如 "GPT-5.1"） */
  displayName: string;
  /** DMXAPI 中的实际模型 ID */
  dmxApiModelId: string;
  /** 所属提供商（用于分类和显示） */
  provider: ApiProvider;
  /** 是否可用（基于DMXAPI配置） */
  available: boolean;
}

/**
 * 分析结果项
 */
export interface AnalysisItem {
  /** 职位描述原文 */
  original: string;
  /** 大白话解读 */
  interpretation: string;
  /** 面试准备问题（HTML格式，包含<br>分隔符） */
  questions: string;
}

/**
 * 分析结果
 */
export interface AnalysisResult {
  /** 分析项数组 */
  items: AnalysisItem[];
  /** 使用的API提供商（保留用于向后兼容） */
  provider: ApiProvider;
  /** 使用的模型ID */
  modelId?: ModelId;
}

/**
 * API配置
 */
export interface ApiConfig {
  /** API提供商 */
  provider: ApiProvider;
  /** API密钥 */
  apiKey: string;
  /** 模型名称（可选） */
  model?: string;
}

/**
 * 分析请求参数
 */
export interface AnalyzeRequest {
  /** 职位描述文本 */
  text: string;
  /** 选择的模型ID */
  modelId: ModelId;
  /** API密钥（已废弃，现在统一从DMXAPI配置获取） */
  apiKey?: string;
  /** API提供商（已废弃，保留用于向后兼容，现在从modelId推导） */
  provider?: ApiProvider;
}

/**
 * API提供商信息（保留用于向后兼容）
 */
export interface ApiProviderInfo {
  /** 提供商标识 */
  value: ApiProvider;
  /** 显示名称 */
  label: string;
  /** 是否可用（根据环境变量判断） */
  available: boolean;
}

/**
 * 模型信息
 */
export interface ModelInfo {
  /** 模型ID */
  value: ModelId;
  /** 显示名称 */
  label: string;
  /** 是否可用 */
  available: boolean;
  /** 所属提供商 */
  provider: ApiProvider;
}
