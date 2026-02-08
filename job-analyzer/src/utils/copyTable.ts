import { AnalysisItem } from '../types';

/**
 * 将HTML内容转换为纯文本（移除所有HTML标签）
 */
function stripHtml(html: string): string {
  const tmp = document.createElement('div');
  tmp.innerHTML = html;
  return tmp.textContent || tmp.innerText || '';
}

/**
 * 转义HTML特殊字符
 */
function escapeHtml(text: string): string {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

/**
 * 转义Markdown特殊字符
 */
function escapeMarkdown(text: string): string {
  return text
    .replace(/\\/g, '\\\\')
    .replace(/\|/g, '\\|')
    .replace(/\n/g, ' ');
}

/**
 * 将表格数据复制为HTML格式
 */
export async function copyTableAsHTML(items: AnalysisItem[]): Promise<void> {
  if (!items || items.length === 0) {
    throw new Error('没有可复制的数据');
  }

  let html = '<table border="1" cellpadding="5" cellspacing="0">\n';
  html += '  <thead>\n';
  html += '    <tr>\n';
  html += '      <th>职位描述原文</th>\n';
  html += '      <th>大白话解读</th>\n';
  html += '      <th>面试准备哪些问题</th>\n';
  html += '    </tr>\n';
  html += '  </thead>\n';
  html += '  <tbody>\n';

  items.forEach((item) => {
    html += '    <tr>\n';
    html += `      <td>${escapeHtml(item.original)}</td>\n`;
    html += `      <td>${escapeHtml(item.interpretation)}</td>\n`;
    // questions字段可能包含HTML，保留HTML结构
    html += `      <td>${item.questions}</td>\n`;
    html += '    </tr>\n';
  });

  html += '  </tbody>\n';
  html += '</table>';

  try {
    await navigator.clipboard.writeText(html);
  } catch (error) {
    // 降级方案：使用传统的复制方法
    const textArea = document.createElement('textarea');
    textArea.value = html;
    textArea.style.position = 'fixed';
    textArea.style.opacity = '0';
    document.body.appendChild(textArea);
    textArea.select();
    try {
      document.execCommand('copy');
      document.body.removeChild(textArea);
    } catch (err) {
      document.body.removeChild(textArea);
      throw new Error('复制失败，请检查浏览器权限设置');
    }
  }
}

/**
 * 将表格数据复制为Markdown格式
 */
export async function copyTableAsMarkdown(items: AnalysisItem[]): Promise<void> {
  if (!items || items.length === 0) {
    throw new Error('没有可复制的数据');
  }

  let markdown = '| 职位描述原文 | 大白话解读 | 面试准备哪些问题 |\n';
  markdown += '| --- | --- | --- |\n';

  items.forEach((item) => {
    // 将HTML转换为纯文本，并转义Markdown特殊字符
    const original = escapeMarkdown(item.original);
    const interpretation = escapeMarkdown(item.interpretation);
    const questions = escapeMarkdown(stripHtml(item.questions));
    
    markdown += `| ${original} | ${interpretation} | ${questions} |\n`;
  });

  try {
    await navigator.clipboard.writeText(markdown);
  } catch (error) {
    // 降级方案：使用传统的复制方法
    const textArea = document.createElement('textarea');
    textArea.value = markdown;
    textArea.style.position = 'fixed';
    textArea.style.opacity = '0';
    document.body.appendChild(textArea);
    textArea.select();
    try {
      document.execCommand('copy');
      document.body.removeChild(textArea);
    } catch (err) {
      document.body.removeChild(textArea);
      throw new Error('复制失败，请检查浏览器权限设置');
    }
  }
}

/**
 * 将表格数据复制为纯文本格式（制表符分隔）
 */
export async function copyTableAsPlainText(items: AnalysisItem[]): Promise<void> {
  if (!items || items.length === 0) {
    throw new Error('没有可复制的数据');
  }

  let text = '职位描述原文\t大白话解读\t面试准备哪些问题\n';

  items.forEach((item) => {
    // 移除HTML标签，只保留纯文本
    const original = stripHtml(item.original).replace(/\n/g, ' ').replace(/\t/g, ' ');
    const interpretation = stripHtml(item.interpretation).replace(/\n/g, ' ').replace(/\t/g, ' ');
    const questions = stripHtml(item.questions).replace(/\n/g, ' ').replace(/\t/g, ' ');
    
    text += `${original}\t${interpretation}\t${questions}\n`;
  });

  try {
    await navigator.clipboard.writeText(text);
  } catch (error) {
    // 降级方案：使用传统的复制方法
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.opacity = '0';
    document.body.appendChild(textArea);
    textArea.select();
    try {
      document.execCommand('copy');
      document.body.removeChild(textArea);
    } catch (err) {
      document.body.removeChild(textArea);
      throw new Error('复制失败，请检查浏览器权限设置');
    }
  }
}
