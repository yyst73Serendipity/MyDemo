import OpenAI from 'openai';
import { buildMessages } from '../utils/promptBuilder';
import { parseAnalysisResponse } from '../utils/parseResponse';
import { AnalyzeRequest, AnalysisResult } from '../types';
import { getDmxApiConfig, getDmxApiModelId } from './apiService';

/**
 * Gemini API服务（通过DMXAPI聚合平台）
 */

/**
 * 调用Gemini API进行分析（通过DMXAPI）
 * @param request 分析请求参数
 * @returns 分析结果
 */
export async function analyzeWithGemini(request: AnalyzeRequest): Promise<AnalysisResult> {
  const { text, modelId } = request;

  try {
    // 获取DMXAPI配置
    const dmxConfig = getDmxApiConfig();
    if (!dmxConfig) {
      throw new Error('未配置DMXAPI API密钥');
    }

    // 初始化OpenAI客户端（使用DMXAPI的base_url，兼容OpenAI格式）
    const openai = new OpenAI({
      apiKey: dmxConfig.apiKey,
      baseURL: dmxConfig.baseUrl,
      dangerouslyAllowBrowser: true // 注意：在生产环境中应该使用后端代理
    });

    // 构建messages
    const messages = buildMessages(text);

    // 获取DMXAPI中的实际模型ID
    const dmxApiModelId = getDmxApiModelId(modelId);

    // 调用API
    const completion = await openai.chat.completions.create({
      model: dmxApiModelId,
      messages: messages,
      temperature: 0.7,
      max_tokens: 4000
    });

    const responseText = completion.choices[0]?.message?.content || '';

    if (!responseText) {
      throw new Error('API返回空响应');
    }

    // 解析响应
    return parseAnalysisResponse(responseText, 'gemini');
  } catch (error) {
    // 处理错误
    if (error instanceof Error) {
      throw new Error(`API调用失败：${error.message}`);
    }
    throw new Error('API调用失败：未知错误');
  }
}
