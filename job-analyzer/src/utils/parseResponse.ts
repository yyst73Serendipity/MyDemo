import { AnalysisResult, ApiProvider, AnalysisItem } from '../types';

/**
 * 解析API响应的工具函数
 */

/**
 * 从文本中提取JSON内容
 * @param text 可能包含markdown代码块的文本
 * @returns JSON字符串
 */
function extractJson(text: string): string {
  // 1. 优先尝试提取JSON代码块中的内容
  const jsonMatch = text.match(/```(?:json)?\s*([\s\S]*?)\s*```/);
  if (jsonMatch) {
    return jsonMatch[1].trim();
  }

  // 2. 尝试提取第一个完整的大括号包裹的JSON对象
  // 使用括号计数法找到最外层的完整JSON对象
  let braceCount = 0;
  let startIndex = -1;
  let endIndex = -1;
  
  for (let i = 0; i < text.length; i++) {
    const char = text[i];
    if (char === '{') {
      if (startIndex === -1) {
        startIndex = i;
      }
      braceCount++;
    } else if (char === '}') {
      braceCount--;
      if (braceCount === 0 && startIndex !== -1) {
        endIndex = i;
        break;
      }
    }
  }
  
  if (startIndex !== -1 && endIndex !== -1) {
    const extracted = text.substring(startIndex, endIndex + 1);
    // 验证提取的内容看起来像JSON（以{开头，以}结尾）
    if (extracted.trim().startsWith('{') && extracted.trim().endsWith('}')) {
      return extracted;
    }
  }

  // 3. 尝试查找包含"items"关键词的JSON对象（更精确的匹配）
  const itemsMatch = text.match(/\{[^{}]*"items"\s*:[\s\S]*\}/);
  if (itemsMatch) {
    // 验证是否是完整的JSON（通过括号计数）
    let count = 0;
    let valid = true;
    for (const char of itemsMatch[0]) {
      if (char === '{') count++;
      if (char === '}') count--;
      if (count < 0) {
        valid = false;
        break;
      }
    }
    if (valid && count === 0) {
      return itemsMatch[0];
    }
  }

  // 4. 如果都没有，尝试简单的正则匹配（作为后备方案）
  const simpleBraceMatch = text.match(/\{[\s\S]*\}/);
  if (simpleBraceMatch) {
    return simpleBraceMatch[0];
  }

  // 5. 如果都没有，返回原文本（让JSON.parse抛出更明确的错误）
  return text.trim();
}

/**
 * 解析API返回的JSON响应
 * @param responseText API返回的文本
 * @param provider 使用的API提供商
 * @returns 解析后的分析结果
 */
export function parseAnalysisResponse(
  responseText: string,
  provider: ApiProvider
): AnalysisResult {
  try {
    // 提取JSON内容
    const jsonText = extractJson(responseText);
    
    // 解析JSON
    let parsed: any;
    try {
      parsed = JSON.parse(jsonText);
    } catch (parseError) {
      // 如果JSON解析失败，提供更详细的错误信息
      const errorMessage = parseError instanceof Error ? parseError.message : '未知错误';
      const preview = jsonText.substring(0, 100);
      throw new Error(
        `JSON解析失败：${errorMessage}\n` +
        `提取的文本预览：${preview}${jsonText.length > 100 ? '...' : ''}\n` +
        `提示：请确保AI返回的是有效的JSON格式，不要包含额外的说明文字`
      );
    }

    // 验证数据结构
    if (!parsed.items || !Array.isArray(parsed.items)) {
      throw new Error('响应格式错误：缺少items数组。请确保返回的JSON包含items字段');
    }

    // 验证每个item的结构
    const items: AnalysisItem[] = parsed.items.map((item: any, index: number) => {
      if (!item.original || !item.interpretation || !item.questions) {
        throw new Error(`第${index + 1}个item缺少必要字段（需要original、interpretation、questions）`);
      }
      return {
        original: String(item.original),
        interpretation: String(item.interpretation),
        questions: String(item.questions)
      };
    });

    return {
      items,
      provider
    };
  } catch (error) {
    // 如果解析失败，抛出更友好的错误信息，包含原始响应的预览
    const errorMessage = error instanceof Error ? error.message : '未知错误';
    const responsePreview = responseText.substring(0, 200);
    throw new Error(
      `解析API响应失败：${errorMessage}\n` +
      `原始响应预览：${responsePreview}${responseText.length > 200 ? '...' : ''}`
    );
  }
}
