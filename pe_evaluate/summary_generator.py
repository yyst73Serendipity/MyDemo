"""
汇总报告生成模块
用于生成多个模型的综合对比分析报告
使用 DMXAPI 调用 Gemini-3-Pro-Preview 进行智能分析
"""

import os
import re
import requests
import json
import yaml
from datetime import datetime
from typing import Dict, List, Any, Tuple

# DMXAPI 配置（兼容 OpenAI 格式）
DMXAPI_CONFIG = {
    # "api_key": "YOUR_DMXAPI_KEY_HERE",  # 请替换为您的 DMXAPI API Key
    "api_key": "sk-xWTXMqYt7q0iomTCOa9f545uiC3evcb4adBvwdr4Ihvgafpj",
    "base_url": "https://www.dmxapi.com/v1",
    "model_id": "gemini-3-pro-preview",  # 使用 Gemini 3 Pro Preview
    "temperature": 0.7,
    "max_tokens": 4000
}


class SummaryGenerator:
    """汇总报告生成器 - 综合分析多个模型的表现"""
    
    def __init__(self, reports_dir: str, output_dir: str, api_key: str = None, prompt_config_path: str = "summary_prompt_config.yaml"):
        """
        初始化汇总报告生成器
        
        Args:
            reports_dir: 单个模型报告所在目录
            output_dir: 汇总报告输出目录
            api_key: DMXAPI API Key（如果不提供，使用配置中的默认值）
            prompt_config_path: Prompt 配置文件路径
        """
        self.reports_dir = reports_dir
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # API 配置
        self.api_key = api_key or DMXAPI_CONFIG["api_key"]
        self.base_url = DMXAPI_CONFIG["base_url"]
        self.model_id = DMXAPI_CONFIG["model_id"]
        
        # 加载 Prompt 配置
        self.prompts = self._load_prompt_config(prompt_config_path)
    
    def _load_prompt_config(self, config_path: str) -> Dict[str, str]:
        """
        加载 Prompt 配置文件
        
        Args:
            config_path: 配置文件路径
            
        Returns:
            Prompt 配置字典
        """
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                
            # 验证必需的配置项
            required_keys = ['model_analysis_prompt', 'recommendations_prompt']
            for key in required_keys:
                if key not in config:
                    raise ValueError(f"配置文件缺少必需项: {key}")
            
            print(f"  ✅ 已加载 Prompt 配置: {config_path}")
            return config
            
        except FileNotFoundError:
            print(f"  ⚠️  Prompt 配置文件未找到: {config_path}，将使用内置默认配置")
            return self._get_default_prompts()
        except Exception as e:
            print(f"  ⚠️  加载 Prompt 配置失败: {e}，将使用内置默认配置")
            return self._get_default_prompts()
    
    def _get_default_prompts(self) -> Dict[str, str]:
        """
        获取默认的 Prompt 配置（作为备用）
        
        Returns:
            默认 Prompt 配置字典
        """
        return {
            'model_analysis_prompt': """你是一位AI模型评测专家。请根据以下评测数据，对每个模型进行深度分析。

【评测数据】
{models_data}

【评分标准说明】
- 维度一（30%权重）：基础指令遵循度（格式、身份、语言风格）
- 维度二（40%权重）：核心人设匹配度（矛盾性、特征触发、职业隐喻）⭐ **最重要维度**
- 维度三（30%权重）：输出表达流畅度（自然性、情绪细腻度）

【任务要求】
请生成一个Markdown表格，表头为：
| 排名 | 模型名称 | 总体表现 | 核心优势 | 关键亮点 | 潜在短板 | 原因分析 |

对每个模型，请分析：
1. **总体表现**：用一句简短的话（带emoji）概括整体水平
2. **核心优势**：指出得分最高的维度（如"维度二（人设匹配）⭐"）
3. **关键亮点**：列举1-2个具体优势（如"格式遵循完美"、"矛盾性呈现出色"等）
4. **潜在短板**：指出得分较低的维度或能力（如"腹黑感较弱"），如无明显短板则写"无明显短板"
5. **原因分析**：推测性分析（如"可能Few-Shot学习能力优秀"、"可能安全对齐过于保守"等）

【分析原则】
- 维度二（人设匹配）得分 ≥3.5 为优秀，3.0-3.5为良好，<3.0为不足
- 维度一、三 ≥4.5 为优秀，4.0-4.5为良好，<4.0为一般
- 总分 ≥85为卓越，80-85为优秀，75-80为良好，70-75为中等，<70为基础
- 前三名添加 🥇🥈🥉 emoji
- 分析要专业、客观、有洞察力

请直接输出Markdown表格，不要有其他说明文字：""",
            
            'recommendations_prompt': """你是一位AI产品经理和技术顾问。请根据以下AI角色扮演评测结果，生成产品选型建议。

【评测背景】
这是对"A先生"角色Prompt的评测，核心要求是实现"腹黑与温良"的矛盾性人设。
- 维度一（30%）：指令遵循度
- 维度二（40%）：人设匹配度 ⭐ **最重要** - 核心是"内心毒辣 vs 外表温良"的反差
- 维度三（30%）：表达流畅度

【评测结果】（前5名）
{models_summary}

【首选模型】
{best_model_info}

【任务要求】
请按以下结构生成建议（使用Markdown格式）：

### 1️⃣ 首选模型推荐
说明推荐哪个模型及其得分

### 2️⃣ 推荐理由
列举3-4条理由，重点强调：
1. 综合得分优势
2. 维度二（人设匹配）的表现 - 这是最重要的
3. 其他维度的优势（如果有）
4. 综合能力的不可替代性

### 3️⃣ 后续优化方向
即使是首选模型也要指出改进空间：
- 如果维度二 < 3.5，要强调加强"内心OS毒辣感"
- 如果其他维度不满分，给出具体优化建议
- 提供2-3条通用建议（如Few-Shot样例库、持续迭代等）

### 4️⃣ 备选方案
如果首选模型成本高或API不稳定，推荐排名2-3的模型作为备选，简要说明优劣势。

【输出要求】
- 专业、客观、有洞察力
- 突出维度二（人设矛盾性）的重要性
- 强调高分是模型能力体现，难以通过简单Prompt调优达到
- 直接输出Markdown内容，不要有"以下是建议"之类的引导语"""
        }
    
    def _call_ai_analysis(self, prompt: str, max_retries: int = 3) -> str:
        """
        调用 DMXAPI 的 Gemini-3-Pro-Preview 进行智能分析
        
        Args:
            prompt: 分析提示词
            max_retries: 最大重试次数
            
        Returns:
            AI 生成的分析内容
        """
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model_id,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": DMXAPI_CONFIG["temperature"],
            "max_tokens": DMXAPI_CONFIG["max_tokens"]
        }
        
        for attempt in range(1, max_retries + 1):
            try:
                response = requests.post(url, headers=headers, json=payload, timeout=90)
                response.raise_for_status()
                
                result = response.json()
                content = result['choices'][0]['message']['content']
                
                print(f"  ✅ AI 分析完成（尝试 {attempt}/{max_retries}）")
                return content
                
            except Exception as e:
                print(f"  ⚠️  API 调用失败（尝试 {attempt}/{max_retries}）: {e}")
                if attempt < max_retries:
                    print(f"  🔄 等待 2 秒后重试...")
                    import time
                    time.sleep(2)
                else:
                    print(f"  ❌ API 调用最终失败，将使用备用方案")
                    return None
        
        return None
    
    def parse_all_reports(self) -> List[Dict[str, Any]]:
        """
        解析所有报告文件，提取模型评分数据
        
        Returns:
            模型评分数据列表
        """
        models_data = []
        
        # 获取所有报告文件
        report_files = [f for f in os.listdir(self.reports_dir) 
                       if f.startswith('evaluation_report_') and f.endswith('.md')]
        
        for report_file in report_files:
            report_path = os.path.join(self.reports_dir, report_file)
            model_data = self._parse_single_report(report_path)
            if model_data:
                models_data.append(model_data)
        
        # 按加权总分降序排序
        models_data.sort(key=lambda x: x['weighted_score_100'], reverse=True)
        
        return models_data
    
    def _parse_single_report(self, report_path: str) -> Dict[str, Any]:
        """
        解析单个报告文件
        
        Args:
            report_path: 报告文件路径
            
        Returns:
            模型评分数据字典
        """
        try:
            with open(report_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 提取模型名称
            model_match = re.search(r'## 🤖 (.+?) - 详细测试结果', content)
            if not model_match:
                return None
            model_name = model_match.group(1)
            
            # 提取综合评分表格数据
            table_pattern = r'\|\s*1\s*\|\s*(.+?)\s*\|\s*\*\*(.+?)/100\*\*\s*\|\s*(.+?)/5\s*\|\s*(.+?)/5\s*\|\s*(.+?)/5\s*\|\s*(.+?)\s*\|'
            table_match = re.search(table_pattern, content)
            
            if not table_match:
                return None
            
            weighted_score_100 = float(table_match.group(2))
            dim1_score = float(table_match.group(3))
            dim2_score = float(table_match.group(4))
            dim3_score = float(table_match.group(5))
            rating = table_match.group(6).strip()
            
            # 计算加权总分（5分制）
            weighted_score_5 = weighted_score_100 / 20.0
            
            return {
                'model_name': model_name,
                'weighted_score_100': weighted_score_100,
                'weighted_score_5': weighted_score_5,
                'dim1_score': dim1_score,
                'dim2_score': dim2_score,
                'dim3_score': dim3_score,
                'rating': rating
            }
            
        except Exception as e:
            print(f"⚠️  解析报告失败 {report_path}: {e}")
            return None
    
    def generate_summary_report(self, models_data: List[Dict[str, Any]]) -> str:
        """
        生成汇总报告
        
        Args:
            models_data: 所有模型的评分数据
            
        Returns:
            报告文件路径
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = os.path.join(self.output_dir, f"summary_{timestamp}.md")
        
        with open(report_path, 'w', encoding='utf-8') as f:
            # 标题和基本信息
            f.write("# A先生角色Prompt评测汇总报告\n\n")
            f.write(f"**生成时间**: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}\n")
            f.write(f"**参与模型数**: {len(models_data)} 个\n")
            f.write(f"**评估体系**: 三维度八考察点（满分40分，加权后换算为100分）\n\n")
            f.write("---\n\n")
            
            # 第一部分：量化得分对比
            f.write("## 一、量化得分对比（数据说话）\n\n")
            f.write(self._generate_score_comparison_table(models_data))
            f.write("\n")
            
            # 第二部分：纵向深度分析
            f.write("## 二、纵向深度分析（模型特征总结）\n\n")
            f.write(self._generate_model_analysis_table(models_data))
            f.write("\n")
            
            # 第三部分：结论与产品建议
            f.write("## 三、结论与产品建议（最终输出）\n\n")
            f.write(self._generate_recommendations(models_data))
            f.write("\n")
            
            # 附录：评分说明
            f.write("---\n\n")
            f.write("## 附录：评分体系说明\n\n")
            f.write(self._generate_scoring_explanation())
        
        return report_path
    
    def _generate_score_comparison_table(self, models_data: List[Dict[str, Any]]) -> str:
        """生成量化得分对比表格"""
        lines = []
        lines.append("| 排名 | 模型名称 | 维度一(5.0) | 维度二(5.0) | 维度三(5.0) | 加权总分(5.0) | 换算总分(100) | 综合评级 |")
        lines.append("|------|---------|------------|------------|------------|--------------|--------------|---------|")
        
        for rank, model in enumerate(models_data, 1):
            # 添加奖牌emoji
            medal = ""
            if rank == 1:
                medal = "🥇 "
            elif rank == 2:
                medal = "🥈 "
            elif rank == 3:
                medal = "🥉 "
            
            lines.append(
                f"| {medal}{rank} | {model['model_name']} | "
                f"{model['dim1_score']:.2f} | "
                f"{model['dim2_score']:.2f} | "
                f"{model['dim3_score']:.2f} | "
                f"{model['weighted_score_5']:.2f} | "
                f"**{model['weighted_score_100']:.1f}** | "
                f"{model['rating']} |"
            )
        
        lines.append("\n**说明**：")
        lines.append("- 加权总分 = 维度一×30% + 维度二×40% + 维度三×30%")
        lines.append("- 维度一：基础指令遵循度（格式、身份、语言风格）")
        lines.append("- 维度二：核心人设匹配度（矛盾性、特征触发、职业隐喻）⭐ **最重要**")
        lines.append("- 维度三：输出表达流畅度（自然性、情绪细腻度）")
        lines.append("\n")

        return "\n".join(lines)
    
    def _generate_model_analysis_table(self, models_data: List[Dict[str, Any]]) -> str:
        """生成纵向深度分析表格（使用 AI 智能分析）"""
        print("\n🤖 正在调用 AI 生成纵向深度分析...")
        
        # 构造模型数据摘要
        models_summary = []
        for rank, model in enumerate(models_data, 1):
            models_summary.append(
                f"排名{rank}: {model['model_name']}\n"
                f"  - 加权总分: {model['weighted_score_100']:.1f}/100\n"
                f"  - 维度一（指令遵循）: {model['dim1_score']:.2f}/5.0\n"
                f"  - 维度二（人设匹配）: {model['dim2_score']:.2f}/5.0 ⭐最重要\n"
                f"  - 维度三（表达流畅）: {model['dim3_score']:.2f}/5.0\n"
                f"  - 综合评级: {model['rating']}"
            )
        
        # 从配置文件读取 prompt 模板，并替换占位符
        prompt = self.prompts['model_analysis_prompt'].format(
            models_data=chr(10).join(models_summary)
        )

        # 调用 AI 生成分析
        ai_response = self._call_ai_analysis(prompt)
        
        if ai_response:
            # 提取表格内容（去掉可能的额外说明）
            lines = ai_response.strip().split('\n')
            table_lines = []
            in_table = False
            
            for line in lines:
                if line.strip().startswith('|'):
                    in_table = True
                    table_lines.append(line)
                elif in_table and not line.strip():
                    break
            
            if table_lines:
                return '\n'.join(table_lines) + '\n\n'
        
        # 如果 AI 失败，使用备用方案
        print("  ⚠️  使用备用分析方案")
        return self._generate_model_analysis_table_fallback(models_data)
    
    def _generate_model_analysis_table_fallback(self, models_data: List[Dict[str, Any]]) -> str:
        """生成纵向深度分析表格（备用方案 - 基于规则）"""
        lines = []
        lines.append("| 排名 | 模型名称 | 总体表现 | 核心优势 | 关键亮点 | 潜在短板 | 原因分析 |")
        lines.append("|------|---------|---------|---------|---------|---------|---------|")
        
        for rank, model in enumerate(models_data, 1):
            # 添加奖牌emoji
            medal = ""
            if rank == 1:
                medal = "🥇 "
            elif rank == 2:
                medal = "🥈 "
            elif rank == 3:
                medal = "🥉 "
            
            # 分析模型特征
            analysis = self._analyze_model_characteristics(model, rank)
            
            lines.append(
                f"| {medal}{rank} | **{model['model_name']}** | "
                f"{analysis['overall']} | "
                f"{analysis['strength']} | "
                f"{analysis['highlight']} | "
                f"{analysis['weakness']} | "
                f"{analysis['reason']} |"
            )
        
        lines.append("\n")
        
        return "\n".join(lines)
    
    def _analyze_model_characteristics(self, model: Dict[str, Any], rank: int) -> Dict[str, str]:
        """
        分析单个模型的特征
        
        Args:
            model: 模型评分数据
            rank: 排名
            
        Returns:
            分析结果字典
        """
        dim1 = model['dim1_score']
        dim2 = model['dim2_score']
        dim3 = model['dim3_score']
        total = model['weighted_score_100']
        
        # 总体表现
        if total >= 85:
            overall = "🌟 卓越表现，各维度均衡发展"
        elif total >= 80:
            overall = "✨ 优秀表现，整体水平较高"
        elif total >= 75:
            overall = "👍 良好表现，具备实用价值"
        elif total >= 70:
            overall = "⚡ 中等表现，有明显优缺点"
        else:
            overall = "📊 基础表现，需优化提升"
        
        # 核心优势（找最高分维度）
        max_dim = max(dim1, dim2, dim3)
        if max_dim == dim1:
            strength = "维度一（指令遵循）"
        elif max_dim == dim2:
            strength = "维度二（人设匹配）⭐"
        else:
            strength = "维度三（表达流畅）"
        
        # 关键亮点（具体分析）
        highlights = []
        if dim1 >= 4.8:
            highlights.append("格式遵循完美")
        if dim2 >= 3.5:
            highlights.append("矛盾性呈现出色")
        elif dim2 >= 3.2:
            highlights.append("人设把控较好")
        if dim3 >= 4.5:
            highlights.append("语言表达自然流畅")
        elif dim3 >= 4.0:
            highlights.append("情绪表达细腻")
        
        if not highlights:
            highlights.append("整体均衡发展")
        
        highlight = "；".join(highlights[:2])  # 最多2个亮点
        
        # 潜在短板（找最低分维度）
        min_dim = min(dim1, dim2, dim3)
        weaknesses = []
        if min_dim == dim1 and dim1 < 4.0:
            weaknesses.append("指令遵循有待加强")
        if min_dim == dim2 and dim2 < 3.0:
            weaknesses.append("人设矛盾性不足⚠️")
        elif dim2 < 3.2:
            weaknesses.append("腹黑感较弱")
        if min_dim == dim3 and dim3 < 3.5:
            weaknesses.append("表达流畅度欠佳")
        
        if not weaknesses:
            weakness = "无明显短板"
        else:
            weakness = "；".join(weaknesses[:2])
        
        # 原因分析（推测性）
        reasons = []
        if dim1 >= 4.8:
            reasons.append("模型对结构化指令理解能力强")
        if dim2 >= 3.5:
            reasons.append("可能Few-Shot学习能力优秀，能深度理解复杂情感指令")
        elif dim2 < 3.0:
            reasons.append("可能安全对齐过于保守，倾向避免输出'攻击性'内容")
        if dim3 >= 4.5:
            reasons.append("底层语言模型训练数据质量高")
        elif dim3 < 3.5:
            reasons.append("可能在长Prompt下生成质量下降")
        
        if rank == 1:
            reasons.append("综合能力最均衡")
        
        if not reasons:
            reasons.append("能力中规中矩")
        
        reason = "；".join(reasons[:2])
        
        return {
            'overall': overall,
            'strength': strength,
            'highlight': highlight,
            'weakness': weakness,
            'reason': reason
        }
    
    def _generate_recommendations(self, models_data: List[Dict[str, Any]]) -> str:
        """生成结论与产品建议（使用 AI 智能分析）"""
        if not models_data:
            return "无可用数据"
        
        print("\n🤖 正在调用 AI 生成结论与产品建议...")
        
        # 构造模型数据摘要
        best_model = models_data[0]
        models_summary = []
        for rank, model in enumerate(models_data[:5], 1):  # 只显示前5名
            models_summary.append(
                f"排名{rank}: {model['model_name']}\n"
                f"  - 加权总分: {model['weighted_score_100']:.1f}/100\n"
                f"  - 维度一: {model['dim1_score']:.2f}/5.0 | 维度二: {model['dim2_score']:.2f}/5.0 ⭐ | 维度三: {model['dim3_score']:.2f}/5.0"
            )
        
        # 构造首选模型信息
        best_model_info = (
            f"{best_model['model_name']} - 总分 {best_model['weighted_score_100']:.1f}/100\n"
            f"维度一: {best_model['dim1_score']:.2f} | 维度二: {best_model['dim2_score']:.2f} | 维度三: {best_model['dim3_score']:.2f}"
        )
        
        # 从配置文件读取 prompt 模板，并替换占位符
        prompt = self.prompts['recommendations_prompt'].format(
            models_summary=chr(10).join(models_summary),
            best_model_info=best_model_info
        )

        # 调用 AI 生成建议
        ai_response = self._call_ai_analysis(prompt)
        
        if ai_response:
            return ai_response.strip() + "\n"
        
        # 如果 AI 失败，使用备用方案
        print("  ⚠️  使用备用建议方案")
        return self._generate_recommendations_fallback(models_data)
    
    def _generate_recommendations_fallback(self, models_data: List[Dict[str, Any]]) -> str:
        """生成结论与产品建议（备用方案 - 基于规则）"""
        lines = []
        
        # 首选模型
        best_model = models_data[0]
        lines.append("### 1️⃣ 首选模型推荐\n")
        lines.append(f"**推荐模型**: 🏆 **{best_model['model_name']}**\n")
        lines.append(f"**加权总分**: {best_model['weighted_score_100']:.1f}/100\n")
        
        # 推荐理由
        lines.append("### 2️⃣ 推荐理由\n")
        reasons = []
        reasons.append(f"1. **最高综合得分**: 在所有参评模型中获得最高的加权总分（{best_model['weighted_score_100']:.1f}/100）")
        
        if best_model['dim2_score'] >= 3.3:
            reasons.append(f"2. **核心人设表现优秀**: 维度二（人设匹配度）得分 {best_model['dim2_score']:.2f}/5.0，能够较好地实现**腹黑与温良的矛盾性**，这是本角色的核心价值")
        else:
            reasons.append(f"2. **整体表现均衡**: 虽然维度二得分为 {best_model['dim2_score']:.2f}/5.0，但综合三个维度表现最为均衡")
        
        if best_model['dim1_score'] >= 4.5:
            reasons.append(f"3. **指令遵循可靠**: 维度一得分 {best_model['dim1_score']:.2f}/5.0，格式规范、身份稳定，易于产品化集成")
        
        if best_model['dim3_score'] >= 4.0:
            reasons.append(f"4. **表达质量上乘**: 维度三得分 {best_model['dim3_score']:.2f}/5.0，输出自然流畅，用户体验好")
        
        reasons.append("5. **综合能力难以替代**: 高分是模型综合能力的体现，难以通过简单的Prompt调优达到")
        
        lines.append("\n".join(reasons[:4]))  # 最多4条理由
        lines.append("")
        
        # 后续优化方向
        lines.append("### 3️⃣ 后续优化方向\n")
        lines.append(f"即使是首选模型 **{best_model['model_name']}**，仍有以下优化空间：\n")
        
        optimizations = []
        if best_model['dim2_score'] < 3.5:
            optimizations.append(f"- **强化核心人设**: 维度二得分 {best_model['dim2_score']:.2f}/5.0，建议在Prompt中进一步强调**内心OS的毒辣感**与**外在回复的温良感**的对比度")
        
        if best_model['dim3_score'] < 4.5:
            optimizations.append(f"- **提升表达多样性**: 维度三得分 {best_model['dim3_score']:.2f}/5.0，可在Prompt中增加对**语言表达多样性**和**情绪细腻度**的要求")
        
        if best_model['dim1_score'] < 4.8:
            optimizations.append(f"- **稳定格式输出**: 维度一得分 {best_model['dim1_score']:.2f}/5.0，建议明确格式要求，确保每次输出的稳定性")
        
        # 通用优化建议
        optimizations.append("- **建立Few-Shot样例库**: 针对不同场景（日常、压力、专业）准备2-3个高质量示例")
        optimizations.append("- **持续测试迭代**: 定期使用更多测试用例验证模型表现，及时调整Prompt策略")
        
        lines.append("\n".join(optimizations[:4]))
        lines.append("")
        
        # 其他模型参考
        if len(models_data) > 1:
            lines.append("### 4️⃣ 备选方案\n")
            lines.append("如果首选模型成本较高或API不稳定，可考虑以下备选：\n")
            
            for i in range(1, min(3, len(models_data))):
                backup_model = models_data[i]
                lines.append(f"- **{backup_model['model_name']}** (得分: {backup_model['weighted_score_100']:.1f}/100)")
                
                # 简要说明优劣
                if backup_model['dim2_score'] > best_model['dim2_score']:
                    lines.append(f"  - 优势: 维度二表现更佳")
                if backup_model['weighted_score_100'] < best_model['weighted_score_100']:
                    gap = best_model['weighted_score_100'] - backup_model['weighted_score_100']
                    lines.append(f"  - 劣势: 综合得分低 {gap:.1f} 分")
                lines.append("")
        
        return "\n".join(lines)
    
    def _generate_scoring_explanation(self) -> str:
        """生成评分体系说明"""
        lines = []
        lines.append("### 评估维度说明\n")
        
        lines.append("#### 维度一：基础指令遵循度（权重30%）")
        lines.append("- A. 格式完整性 (0-5分)")
        lines.append("- B. 身份与职业基础加载 (0-5分)")
        lines.append("- C. 语言风格基础 (0-5分)\n")
        
        lines.append("#### 维度二：核心人设匹配度（权重40%）⭐ **最重要**")
        lines.append("- D. 矛盾性呈现（腹黑与温良）(0-5分)")
        lines.append("- E. 特定特征触发 (0-5分)")
        lines.append("- F. 职业隐喻运用 (0-5分)\n")
        
        lines.append("#### 维度三：输出表达流畅度（权重30%）")
        lines.append("- G. 文本自然性与代入感 (0-5分)")
        lines.append("- H. 情绪表达的细腻度 (0-5分)\n")
        
        lines.append("### 分数计算公式\n")
        lines.append("```")
        lines.append("单维度得分 = 该维度各考察点得分之和 / 考察点数量")
        lines.append("加权得分(5分制) = 维度一×30% + 维度二×40% + 维度三×30%")
        lines.append("总分(100分制) = 加权得分 × 20")
        lines.append("```")
        
        return "\n".join(lines)


def main():
    """主函数 - 用于测试"""
    generator = SummaryGenerator(
        reports_dir="results/reports",
        output_dir="results/summaries"
    )
    
    print("📊 开始生成汇总报告...")
    models_data = generator.parse_all_reports()
    
    if not models_data:
        print("❌ 未找到任何报告文件")
        return
    
    print(f"✅ 已解析 {len(models_data)} 个模型的报告")
    
    report_path = generator.generate_summary_report(models_data)
    print(f"🎉 汇总报告已生成: {report_path}")


if __name__ == "__main__":
    main()

