import OpenAI from 'openai';
import { ApiProvider, AnalyzeRequest, AnalysisResult, ModelId, ModelConfig } from '../types';
import { buildMessages } from '../utils/promptBuilder';
import { parseAnalysisResponse } from '../utils/parseResponse';

/**
 * 模型配置列表
 */
export const MODEL_CONFIGS: ModelConfig[] = [
  // OpenAI GPT 系列
  {
    id: 'gpt-5.1',
    displayName: 'GPT-5.1',
    dmxApiModelId: 'gpt-5.1',
    provider: 'openai',
    available: true
  },
  {
    id: 'gpt-4o',
    displayName: 'GPT-4o',
    dmxApiModelId: 'gpt-4o',
    provider: 'openai',
    available: true
  },
  // Google Gemini 系列
  {
    id: 'gemini-2.5-pro',
    displayName: 'Gemini-2.5-Pro',
    dmxApiModelId: 'gemini-2.5-pro',
    provider: 'gemini',
    available: true
  },
  {
    id: 'gemini-3-pro-preview',
    displayName: 'Gemini-3-Pro-Preview',
    dmxApiModelId: 'gemini-3-pro-preview',
    provider: 'gemini',
    available: true
  },
  // DeepSeek 系列
  {
    id: 'deepseek-r1',
    displayName: 'DeepSeek-R1',
    dmxApiModelId: 'deepseek-ai/DeepSeek-R1',
    provider: 'deepseek',
    available: true
  },
  {
    id: 'deepseek-v3',
    displayName: 'DeepSeek-V3',
    dmxApiModelId: 'deepseek-ai/DeepSeek-V3',
    provider: 'deepseek',
    available: true
  },
  // Qwen 系列
  {
    id: 'qwen3-max',
    displayName: 'Qwen3-Max',
    dmxApiModelId: 'qwen3-max',
    provider: 'qwen',
    available: true
  },
  {
    id: 'qwen3-max-preview',
    displayName: 'Qwen3-Max-Preview',
    dmxApiModelId: 'qwen3-max-preview',
    provider: 'qwen',
    available: true
  },
  // Kimi 系列
  {
    id: 'kimi-k2',
    displayName: 'Kimi-K2',
    dmxApiModelId: 'Kimi-K2',
    provider: 'kimi',
    available: true
  }
];

/**
 * 获取模型配置
 * @param modelId 模型ID
 * @returns 模型配置，如果不存在则返回null
 */
export function getModelConfig(modelId: ModelId): ModelConfig | null {
  return MODEL_CONFIGS.find(config => config.id === modelId) || null;
}

/**
 * 获取所有可用模型
 * @returns 可用模型列表
 */
export function getAvailableModels(): ModelConfig[] {
  const dmxConfig = getDmxApiConfig();
  const isAvailable = dmxConfig !== null;
  
  return MODEL_CONFIGS.map(config => ({
    ...config,
    available: isAvailable && config.available
  }));
}

/**
 * 根据模型ID获取DMXAPI中的实际模型ID
 * @param modelId 模型ID
 * @returns DMXAPI中的模型ID
 */
export function getDmxApiModelId(modelId: ModelId): string {
  const config = getModelConfig(modelId);
  if (!config) {
    throw new Error(`未找到模型配置：${modelId}`);
  }
  return config.dmxApiModelId;
}

/**
 * 根据模型ID获取提供商
 * @param modelId 模型ID
 * @returns API提供商
 */
export function getProviderByModelId(modelId: ModelId): ApiProvider {
  const config = getModelConfig(modelId);
  if (!config) {
    throw new Error(`未找到模型配置：${modelId}`);
  }
  return config.provider;
}

/**
 * 统一的DMXAPI调用函数
 * 所有模型都通过DMXAPI使用OpenAI兼容格式
 * @param request 分析请求参数
 * @returns 分析结果
 */
async function analyzeWithDmxApi(request: AnalyzeRequest): Promise<AnalysisResult> {
  const { text, modelId } = request;

  // 获取模型配置
  const modelConfig = getModelConfig(modelId);
  if (!modelConfig) {
    throw new Error(`不支持的模型：${modelId}`);
  }

  // 获取DMXAPI配置
  const dmxConfig = getDmxApiConfig();
  if (!dmxConfig) {
    throw new Error('未配置DMXAPI API密钥');
  }

  try {
    // 初始化OpenAI客户端（使用DMXAPI的base_url，兼容OpenAI格式）
    const openai = new OpenAI({
      apiKey: dmxConfig.apiKey,
      baseURL: dmxConfig.baseUrl,
      dangerouslyAllowBrowser: true // 注意：在生产环境中应该使用后端代理
    });

    // 构建messages
    const messages = buildMessages(text);

    // 获取DMXAPI中的实际模型ID
    const dmxApiModelId = modelConfig.dmxApiModelId;

    // 调用API（尝试使用response_format强制JSON输出）
    let completion;
    try {
      completion = await openai.chat.completions.create({
        model: dmxApiModelId,
        messages: messages,
        temperature: 0.3,  // 降低temperature提高输出稳定性
        max_tokens: 4000,
        response_format: { type: "json_object" }  // 强制JSON输出
      });
    } catch (formatError) {
      // 如果response_format不支持，降级为不使用该参数
      if (formatError instanceof Error && formatError.message.includes('response_format')) {
        console.warn('DMXAPI可能不支持response_format参数，降级处理');
        completion = await openai.chat.completions.create({
          model: dmxApiModelId,
          messages: messages,
          temperature: 0.3,
          max_tokens: 4000
        });
      } else {
        throw formatError;
      }
    }

    const responseText = completion.choices[0]?.message?.content || '';

    if (!responseText) {
      throw new Error('API返回空响应');
    }

    // 解析响应（使用模型配置中的provider）
    const parsedResult = parseAnalysisResponse(responseText, modelConfig.provider);

    // 返回结果，包含模型ID和提供商信息
    return {
      ...parsedResult,
      provider: modelConfig.provider,
      modelId
    };
  } catch (error) {
    // 处理错误
    if (error instanceof Error) {
      throw new Error(`API调用失败：${error.message}`);
    }
    throw new Error('API调用失败：未知错误');
  }
}

/**
 * 分析职位描述
 * @param request 分析请求参数
 * @returns 分析结果
 */
export async function analyzeJobDescription(request: AnalyzeRequest): Promise<AnalysisResult> {
  // 所有模型统一使用DMXAPI调用
  return analyzeWithDmxApi(request);
}

/**
 * DMXAPI 配置接口
 */
export interface DmxApiConfig {
  apiKey: string;
  baseUrl: string;
}

/**
 * 获取DMXAPI配置
 * @returns DMXAPI配置，如果未配置则返回null
 */
export function getDmxApiConfig(): DmxApiConfig | null {
  const apiKey = import.meta.env.VITE_DMXAPI_API_KEY;
  const baseUrl = import.meta.env.VITE_DMXAPI_BASE_URL || 'https://www.dmxapi.com/v1';

  if (!apiKey || typeof apiKey !== 'string') {
    return null;
  }

  return {
    apiKey,
    baseUrl
  };
}

/**
 * 获取API密钥（统一使用DMXAPI）
 * @param provider API提供商（保留参数以保持接口兼容性）
 * @returns API密钥，如果未配置则返回null
 */
export function getApiKey(provider: ApiProvider): string | null {
  const config = getDmxApiConfig();
  return config?.apiKey || null;
}

/**
 * 检查API是否可用（是否配置了DMXAPI密钥）
 * @param provider API提供商（保留参数以保持接口兼容性）
 * @returns 是否可用
 */
export function isApiAvailable(provider: ApiProvider): boolean {
  return getDmxApiConfig() !== null;
}
