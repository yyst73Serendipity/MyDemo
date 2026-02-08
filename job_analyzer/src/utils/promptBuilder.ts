/**
 * 构建分析Prompt的工具函数
 */

/**
 * 构建统一的Prompt内容
 * @param jobDescription 职位描述文本
 * @returns 完整的Prompt字符串
 */
export function buildPrompt(jobDescription: string): string {
  return `你是一个专业的职位分析助手。请分析以下职位描述，并按照以下格式输出JSON：

{
  "items": [
    {
      "original": "职位描述原文的第一条（保持原格式，包括编号）",
      "interpretation": "用大白话解释这条要求实际是做什么工作、需要什么能力",
      "questions": "问题1<br>问题2<br>问题3"
    },
    {
      "original": "职位描述原文的第二条",
      "interpretation": "大白话解读",
      "questions": "问题1<br>问题2"
    }
  ]
}

职位描述：
${jobDescription}

重要要求：
1. 职位描述原文（original字段）必须严格按照原文的分点来拆解，保持原有的编号、格式和措辞
2. 大白话解读（interpretation字段）要说明这个岗位实际可能做什么工作、需要什么能力，用通俗易懂的语言
3. 面试准备问题（questions字段）要结合前两项分析，思考面试官可能会问什么问题，每个问题用<br>分隔，问题要有针对性和实用性
4. 输出必须是有效的JSON格式，不要包含markdown代码块标记（如\`\`\`json）
5. 如果职位描述中有多条要求，请拆解成多个items`;
}

/**
 * 构建OpenAI/DeepSeek格式的messages数组
 * @param jobDescription 职位描述文本
 * @returns messages数组
 */
export function buildMessages(jobDescription: string) {
  const systemPrompt = `你是一个专业的职位分析助手。你必须以JSON格式输出分析结果。

重要：只返回JSON格式的数据，不要添加任何说明文字、前缀或后缀。直接返回JSON对象。

输出格式（必须是有效的JSON）：
{
  "items": [
    {
      "original": "职位描述原文的第一条（保持原格式，包括编号）",
      "interpretation": "用大白话解释这条要求实际是做什么工作、需要什么能力",
      "questions": "问题1<br>问题2<br>问题3"
    }
  ]
}

要求：
1. 职位描述原文（original字段）必须严格按照原文的分点来拆解，保持原有的编号、格式和措辞
2. 大白话解读（interpretation字段）要说明这个岗位实际可能做什么工作、需要什么能力，用通俗易懂的语言
3. 面试准备问题（questions字段）要结合前两项分析，思考面试官可能会问什么问题，每个问题用<br>分隔，问题要有针对性和实用性
4. 输出必须是有效的JSON格式，不要包含markdown代码块标记
5. 不要添加任何说明文字，直接返回JSON对象`;

  const userPrompt = `请分析以下职位描述：

${jobDescription}`;

  return [
    { role: 'system' as const, content: systemPrompt },
    { role: 'user' as const, content: userPrompt }
  ];
}
