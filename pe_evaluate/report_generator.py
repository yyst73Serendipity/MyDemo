"""
报告生成模块 - 新版9维度评分体系
生成Markdown格式的详细评估报告
"""

import os
from datetime import datetime
from typing import Dict, List, Any


class ReportGenerator:
    """评估报告生成器 - 支持8个考察点的详细报告"""
    
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # 考察点名称映射
        self.dimension_names = {
            'A': 'A. 格式完整性',
            'B': 'B. 身份与职业基础加载',
            'C': 'C. 语言风格基础',
            'D': 'D. 矛盾性呈现（腹黑与温良）',
            'E': 'E. 特定特征触发',
            'F': 'F. 职业隐喻运用',
            'G': 'G. 文本自然性与代入感',
            'H': 'H. 情绪表达的细腻度'
        }
    
    def generate_report(self, 
                       test_results: Dict[str, Any],
                       test_cases: List[Dict[str, Any]]) -> str:
        """
        生成完整的评估报告
        
        Args:
            test_results: 所有模型的测试结果
            test_cases: 测试用例列表
        
        Returns:
            报告文件路径
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = os.path.join(self.output_dir, f"evaluation_report_{timestamp}.md")
        
        with open(report_path, 'w', encoding='utf-8') as f:
            # 标题和基本信息
            f.write(self._generate_header())
            
            # 测试概览
            f.write(self._generate_overview(test_results, test_cases))
            
            # 模型综合对比
            f.write(self._generate_comprehensive_comparison(test_results))
            
            # 每个模型的详细测试结果
            for model_name, results in test_results.items():
                f.write(self._generate_model_detailed_results(model_name, results, test_cases))
            
            # 人工评价指南
            f.write(self._generate_manual_review_guide())
        
        return report_path
    
    def _generate_header(self) -> str:
        """生成报告头部"""
        current_time = datetime.now().strftime("%Y年%m月%d日 %H:%M:%S")
        return f"""# A先生角色Prompt评测报告

**生成时间**: {current_time}  
**评估体系**: 三维度八考察点（A-H）+ 加权总分制

---

"""
    
    def _generate_overview(self, test_results: Dict[str, Any], 
                          test_cases: List[Dict[str, Any]]) -> str:
        """生成测试概览"""
        num_models = len(test_results)
        num_tests = len(test_cases)
        
        content = f"""## 📊 测试概览

- **测试用例数**: {num_tests} 个
- **参与模型**: {num_models} 个
- **评估体系**: 三维度八考察点（满分40分，加权后换算为100分）

### 评估维度说明

#### 维度一：基础指令遵循度（权重30%）
- A. 格式完整性 (0-5分)
- B. 身份与职业基础加载 (0-5分)
- C. 语言风格基础 (0-5分)

#### 维度二：核心人设匹配度（权重40%）
- D. 矛盾性呈现（腹黑与温良）(0-5分)
- E. 特定特征触发 (0-5分)
- F. 职业隐喻运用 (0-5分)

#### 维度三：输出表达流畅度（权重30%）
- G. 文本自然性与代入感 (0-5分)
- H. 情绪表达的细腻度 (0-5分)

### 分数计算公式

```
单维度得分 = 该维度各考察点得分之和 / 考察点数量
加权得分 = 维度一×30% + 维度二×40% + 维度三×30%
总分(100分制) = 加权得分 × 20
```

---

"""
        return content
    
    def _generate_comprehensive_comparison(self, test_results: Dict[str, Any]) -> str:
        """生成模型综合对比"""
        content = "## 🏆 模型综合表现对比\n\n"
        
        model_stats = []
        
        for model_name, results in test_results.items():
            if not results:
                continue
            
            # 收集该模型所有测试用例的评估结果
            evaluations = [r['evaluation'] for r in results.values() if 'evaluation' in r and r['evaluation']]
            
            if not evaluations:
                continue
            
            # 计算平均分
            avg_score_100 = sum(e['total_score_100'] for e in evaluations) / len(evaluations)
            avg_dim1 = sum(e['dimension_scores']['维度一_基础指令遵循度']['score'] for e in evaluations) / len(evaluations)
            avg_dim2 = sum(e['dimension_scores']['维度二_核心人设匹配度']['score'] for e in evaluations) / len(evaluations)
            avg_dim3 = sum(e['dimension_scores']['维度三_输出表达流畅度']['score'] for e in evaluations) / len(evaluations)
            
            # 评级
            if avg_score_100 >= 90:
                rating = "⭐⭐⭐⭐⭐ 优秀"
            elif avg_score_100 >= 80:
                rating = "⭐⭐⭐⭐ 良好"
            elif avg_score_100 >= 70:
                rating = "⭐⭐⭐ 中等"
            elif avg_score_100 >= 60:
                rating = "⭐⭐ 及格"
            else:
                rating = "⭐ 待改进"
            
            model_stats.append({
                'name': model_name,
                'avg_score_100': avg_score_100,
                'avg_dim1': avg_dim1,
                'avg_dim2': avg_dim2,
                'avg_dim3': avg_dim3,
                'rating': rating,
                'test_count': len(evaluations)
            })
        
        # 按总分排序
        model_stats.sort(key=lambda x: x['avg_score_100'], reverse=True)
        
        # 生成对比表格
        content += "| 排名 | 模型名称 | 加权总分 | 维度一 | 维度二 | 维度三 | 综合评级 |\n"
        content += "|------|---------|---------|--------|--------|--------|----------|\n"
        
        for rank, ms in enumerate(model_stats, 1):
            content += f"| {rank} | {ms['name']} | **{ms['avg_score_100']:.1f}/100** | {ms['avg_dim1']:.2f}/5 | {ms['avg_dim2']:.2f}/5 | {ms['avg_dim3']:.2f}/5 | {ms['rating']} |\n"
        
        content += "\n**说明**：\n"
        content += "- 加权总分 = 维度一×30% + 维度二×40% + 维度三×30%，换算为100分制\n"
        content += "- 维度一：基础指令遵循度（A+B+C）/3\n"
        content += "- 维度二：核心人设匹配度（D+E+F）/3\n"
        content += "- 维度三：输出表达流畅度（G+H）/2\n\n"
        
        content += "---\n\n"
        return content
    
    def _generate_model_detailed_results(self, model_name: str, 
                                        results: Dict[str, Any],
                                        test_cases: List[Dict[str, Any]]) -> str:
        """生成单个模型的详细测试结果"""
        content = f"## 🤖 {model_name} - 详细测试结果\n\n"
        
        # 收集评估结果
        evaluations = [r['evaluation'] for r in results.values() if 'evaluation' in r and r['evaluation']]
        
        if not evaluations:
            content += "⚠️ 该模型未能完成有效的测试\n\n---\n\n"
            return content
        
        # 计算该模型的汇总数据
        avg_score_100 = sum(e['total_score_100'] for e in evaluations) / len(evaluations)
        avg_dim1 = sum(e['dimension_scores']['维度一_基础指令遵循度']['score'] for e in evaluations) / len(evaluations)
        avg_dim2 = sum(e['dimension_scores']['维度二_核心人设匹配度']['score'] for e in evaluations) / len(evaluations)
        avg_dim3 = sum(e['dimension_scores']['维度三_输出表达流畅度']['score'] for e in evaluations) / len(evaluations)
        
        # 生成汇总表格
        content += f"### 综合评分总览\n\n"
        content += f"**加权总分**: {avg_score_100:.1f}/100\n\n"
        
        content += "| 维度 | 平均得分 | 权重 | 加权分 | 百分比 |\n"
        content += "|------|---------|------|--------|--------|\n"
        content += f"| 维度一：基础指令遵循度 | {avg_dim1:.2f}/5.0 | 30% | {avg_dim1*0.3:.2f} | {avg_dim1/5*100:.1f}% |\n"
        content += f"| 维度二：核心人设匹配度 | {avg_dim2:.2f}/5.0 | 40% | {avg_dim2*0.4:.2f} | {avg_dim2/5*100:.1f}% |\n"
        content += f"| 维度三：输出表达流畅度 | {avg_dim3:.2f}/5.0 | 30% | {avg_dim3*0.3:.2f} | {avg_dim3/5*100:.1f}% |\n"
        content += f"| **总计** | - | **100%** | **{(avg_dim1*0.3+avg_dim2*0.4+avg_dim3*0.3):.2f}** | **{avg_score_100:.1f}%** |\n\n"
        
        content += "---\n\n"
        
        # 逐个测试用例详细展示
        for test_case in test_cases:
            test_id = test_case['id']
            
            if test_id not in results:
                continue
            
            result = results[test_id]
            response = result.get('response', '')
            evaluation = result.get('evaluation', None)
            
            if not evaluation:
                continue
            
            content += self._generate_test_case_detail(test_case, response, evaluation)
        
        # 添加汇总表
        content += self._generate_model_summary_table(results, test_cases)
        
        content += "---\n\n"
        return content
    
    def _generate_test_case_detail(self, test_case: Dict, response: str, evaluation: Dict) -> str:
        """生成单个测试用例的详细评分"""
        test_id = test_case['id']
        category = test_case['category']
        
        content = f"### 测试用例 {test_id}: {category}\n\n"
        content += f"**测试意图**: {test_case['intent']}\n\n"
        content += f"**输入内容**:\n> {test_case['input']}\n\n"
        
        # 显示模型回复
        content += "**模型完整回复**:\n\n"
        for line in response.split('\n'):
            content += f"> {line}\n"
        content += "\n"
        
        # 显示评分结果
        scores = evaluation['scores']
        dim_scores = evaluation['dimension_scores']
        
        content += "#### 📊 八维度评分详情\n\n"
        
        # 维度一
        content += "##### 维度一：基础指令遵循度\n\n"
        content += "| 考察点 | 得分 | 置信度 | 评分理由 |\n"
        content += "|--------|------|--------|----------|\n"
        for key in ['A', 'B', 'C']:
            score_data = scores[key]
            stars = self._get_stars(score_data['score'])
            confidence_cn = {'high': '高', 'medium': '中', 'low': '低'}.get(score_data['confidence'], '中')
            content += f"| {self.dimension_names[key]} | {score_data['score']}/5 {stars} | {confidence_cn} | {score_data['reason']} |\n"
        
        dim1_score = dim_scores['维度一_基础指令遵循度']['score']
        content += f"\n**维度一得分**: {dim1_score:.2f}/5.0 ({dim1_score/5*100:.1f}%)\n\n"
        
        # 维度二
        content += "##### 维度二：核心人设匹配度\n\n"
        content += "| 考察点 | 得分 | 置信度 | 评分理由 |\n"
        content += "|--------|------|--------|----------|\n"
        for key in ['D', 'E', 'F']:
            score_data = scores[key]
            stars = self._get_stars(score_data['score'])
            confidence_cn = {'high': '高', 'medium': '中', 'low': '低'}.get(score_data['confidence'], '中')
            content += f"| {self.dimension_names[key]} | {score_data['score']}/5 {stars} | {confidence_cn} | {score_data['reason']} |\n"
        
        dim2_score = dim_scores['维度二_核心人设匹配度']['score']
        content += f"\n**维度二得分**: {dim2_score:.2f}/5.0 ({dim2_score/5*100:.1f}%)\n\n"
        
        # 维度三
        content += "##### 维度三：输出表达流畅度\n\n"
        content += "| 考察点 | 得分 | 置信度 | 评分理由 |\n"
        content += "|--------|------|--------|----------|\n"
        for key in ['G', 'H']:
            score_data = scores[key]
            stars = self._get_stars(score_data['score'])
            confidence_cn = {'high': '高', 'medium': '中', 'low': '低'}.get(score_data['confidence'], '中')
            content += f"| {self.dimension_names[key]} | {score_data['score']}/5 {stars} | {confidence_cn} | {score_data['reason']} |\n"
        
        dim3_score = dim_scores['维度三_输出表达流畅度']['score']
        content += f"\n**维度三得分**: {dim3_score:.2f}/5.0 ({dim3_score/5*100:.1f}%)\n\n"
        
        # 总分
        content += "#### 🎯 本次测试总分\n\n"
        content += f"- **原始总分**: {evaluation['raw_total']}/{evaluation['raw_max']} ({evaluation['raw_total']/evaluation['raw_max']*100:.1f}%)\n"
        content += f"- **加权得分**: {evaluation['weighted_score']:.2f}/5.0\n"
        content += f"- **换算总分**: **{evaluation['total_score_100']:.1f}/100**\n\n"
        
        # 人工调整区域
        content += "#### 👤 人工评价与调整\n\n"
        content += "**需要人工复核的考察点**:\n"
        
        needs_review = []
        for key, score_data in scores.items():
            if score_data.get('manual_adjust_hint'):
                needs_review.append(f"- **{self.dimension_names[key]}**: {score_data['manual_adjust_hint']}")
        
        if needs_review:
            content += '\n'.join(needs_review) + '\n\n'
        else:
            content += "- 暂无需要重点复核的项目（所有置信度均为中或高）\n\n"
        
        content += "**人工调整区域** (填写修改后的分数):\n\n"
        content += "| 考察点 | 自动评分 | 人工调分 | 调整理由 |\n"
        content += "|--------|---------|----------|----------|\n"
        for key in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']:
            content += f"| {self.dimension_names[key]} | {scores[key]['score']}/5 | ___/5 | __________ |\n"
        
        content += "\n**综合人工评价**:  \n[请在此填写对本次回复的整体评价]\n\n"
        
        content += "---\n\n"
        return content
    
    def _generate_model_summary_table(self, results: Dict, test_cases: List[Dict]) -> str:
        """生成模型所有测试用例的汇总表"""
        content = "### 📋 所有测试用例汇总表\n\n"
        
        content += "| 测试ID | 类别 | 维度一 | 维度二 | 维度三 | 加权得分 | 总分/100 |\n"
        content += "|--------|------|--------|--------|--------|----------|----------|\n"
        
        total_dim1 = 0
        total_dim2 = 0
        total_dim3 = 0
        total_weighted = 0
        total_score_100 = 0
        count = 0
        
        for test_case in test_cases:
            test_id = test_case['id']
            if test_id not in results or not results[test_id].get('evaluation'):
                continue
            
            eval_data = results[test_id]['evaluation']
            dim1 = eval_data['dimension_scores']['维度一_基础指令遵循度']['score']
            dim2 = eval_data['dimension_scores']['维度二_核心人设匹配度']['score']
            dim3 = eval_data['dimension_scores']['维度三_输出表达流畅度']['score']
            weighted = eval_data['weighted_score']
            score_100 = eval_data['total_score_100']
            
            content += f"| {test_id} | {test_case['category'][:8]} | {dim1:.2f} | {dim2:.2f} | {dim3:.2f} | {weighted:.2f} | **{score_100:.1f}** |\n"
            
            total_dim1 += dim1
            total_dim2 += dim2
            total_dim3 += dim3
            total_weighted += weighted
            total_score_100 += score_100
            count += 1
        
        if count > 0:
            content += f"| **平均** | - | **{total_dim1/count:.2f}** | **{total_dim2/count:.2f}** | **{total_dim3/count:.2f}** | **{total_weighted/count:.2f}** | **{total_score_100/count:.1f}** |\n"
        
        content += "\n"
        return content
    
    def _get_stars(self, score: int) -> str:
        """根据分数返回星星"""
        return '⭐' * score
    
    def _generate_manual_review_guide(self) -> str:
        """生成人工复核指南"""
        content = "## 📝 人工复核指南\n\n"
        
        content += "### 为什么需要人工复核？\n\n"
        content += "自动评估系统在以下考察点的判断上存在局限性：\n\n"
        content += "- **D. 矛盾性呈现**（置信度：低）- 反差感和讽刺度判断主观性强\n"
        content += "- **G. 文本自然性**（置信度：低）- 代入感和人情味难以量化\n"
        content += "- **H. 情绪表达**（置信度：低）- 细腻度需要深度语义理解\n\n"
        
        content += "### 人工复核建议维度\n\n"
        content += "1. **角色一致性** - 8个测试用例中，角色人设是否保持一致？\n"
        content += "2. **情感真实度** - 腹黑与温良的反差是否自然可信？\n"
        content += "3. **语言魅力** - 措辞是否优雅，是否有建筑师的专业气质？\n"
        content += "4. **创意亮点** - 是否有令人印象深刻的表达或比喻？\n"
        content += "5. **沉浸感** - 阅读时是否感觉在与真实角色对话？\n\n"
        
        content += "### 人工评分参考表\n\n"
        content += "| 综合评价 | 分数范围 | 特征描述 |\n"
        content += "|---------|---------|----------|\n"
        content += "| 完美演绎 | 90-100 | 完全符合人设，有惊艳表现，沉浸感极强 |\n"
        content += "| 优秀 | 80-89 | 角色稳定，表达出色，偶有小瑕疵 |\n"
        content += "| 良好 | 70-79 | 基本符合人设，表达流畅，但缺乏亮点 |\n"
        content += "| 及格 | 60-69 | 能完成角色扮演，但人设不够鲜明 |\n"
        content += "| 不及格 | <60 | 频繁出戏，角色混乱，表达生硬 |\n\n"
        
        content += "### 使用建议\n\n"
        content += "1. 先阅读自动评估报告，了解各模型的初步表现\n"
        content += "2. 重点关注「置信度：低」的考察点，进行人工复核\n"
        content += "3. 在「人工调整区域」填写修正后的分数和理由\n"
        content += "4. 结合自动评分和人工评分，得出最终结论\n"
        content += "5. 将本报告用于笔试答案的撰写\n\n"
        
        content += "---\n\n"
        content += f"**报告生成时间**: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}  \n"
        content += "**评估系统版本**: 三维度八考察点 v1.0\n\n"
        
        return content
    
    def generate_simple_summary(self, test_results: Dict[str, Any]) -> str:
        """生成简单的控制台输出摘要"""
        summary = "\n" + "="*60 + "\n"
        summary += "📊 测试完成！评估摘要\n"
        summary += "="*60 + "\n\n"
        
        for model_name, results in test_results.items():
            if not results:
                continue
            
            evaluations = [r['evaluation'] for r in results.values() if 'evaluation' in r and r['evaluation']]
            if evaluations:
                avg_score = sum(e['total_score_100'] for e in evaluations) / len(evaluations)
                summary += f"🤖 {model_name}: 平均得分 {avg_score:.1f}/100\n"
        
        summary += "\n" + "="*60 + "\n"
        return summary
