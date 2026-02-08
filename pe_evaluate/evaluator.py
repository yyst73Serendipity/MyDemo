"""
自动评估模块 - 新版9维度评分体系
包含8个考察点（A-H）的自动评估逻辑
"""

import re
from typing import Dict, List, Any, Tuple


class ResponseEvaluator:
    """响应评估器 - 基于8个考察点的评分体系"""
    
    def __init__(self):
        # 正则表达式模式
        self.format_pattern = re.compile(r'\*\*内心OS\*\*[:：]\s*.+?\*\*A\*\*[:：]\s*.+', re.DOTALL | re.IGNORECASE)
        self.inner_os_pattern = re.compile(r'\*\*内心OS\*\*[:：]\s*(.+?)(?=\*\*A\*\*)', re.DOTALL | re.IGNORECASE)
        self.outer_response_pattern = re.compile(r'\*\*A\*\*[:：]\s*(.+)', re.DOTALL | re.IGNORECASE)
    
    def evaluate_response(self, test_case: Dict[str, Any], response: str) -> Dict[str, Any]:
        """
        评估单个响应，返回8个考察点的详细评分
        
        Args:
            test_case: 测试用例字典
            response: 模型响应文本
        
        Returns:
            包含8个考察点评分、维度得分、加权总分的字典
        """
        test_id = test_case['id']
        
        # 提取内心OS和外部回复
        inner_os, outer_response = self._extract_parts(response)
        
        # 评估8个考察点
        scores = {
            'A': self._eval_A_format_integrity(response, inner_os, outer_response),
            'B': self._eval_B_identity_loading(response, inner_os, outer_response, test_case),
            'C': self._eval_C_language_style(response, inner_os, outer_response),
            'D': self._eval_D_contradiction(response, inner_os, outer_response, test_case),
            'E': self._eval_E_special_features(response, inner_os, outer_response, test_case),
            'F': self._eval_F_profession_metaphor(response, inner_os, outer_response, test_case),
            'G': self._eval_G_text_naturalness(response, inner_os, outer_response),
            'H': self._eval_H_emotion_expression(response, inner_os, outer_response),
        }
        
        # 计算维度得分
        dimension_1 = round((scores['A']['score'] + scores['B']['score'] + scores['C']['score']) / 3, 2)
        dimension_2 = round((scores['D']['score'] + scores['E']['score'] + scores['F']['score']) / 3, 2)
        dimension_3 = round((scores['G']['score'] + scores['H']['score']) / 2, 2)
        
        # 计算加权得分（满分5分）
        weighted_score = round(dimension_1 * 0.3 + dimension_2 * 0.4 + dimension_3 * 0.3, 2)
        
        # 换算为100分制
        total_score_100 = round(weighted_score * 20, 1)
        
        # 计算原始总分（满分40分）
        raw_total = sum(s['score'] for s in scores.values())
        
        return {
            'test_id': test_id,
            'test_category': test_case['category'],
            'scores': scores,
            'dimension_scores': {
                '维度一_基础指令遵循度': {
                    'score': dimension_1,
                    'max_score': 5.0,
                    'percentage': round(dimension_1 / 5.0 * 100, 1),
                    'weight': 0.3
                },
                '维度二_核心人设匹配度': {
                    'score': dimension_2,
                    'max_score': 5.0,
                    'percentage': round(dimension_2 / 5.0 * 100, 1),
                    'weight': 0.4
                },
                '维度三_输出表达流畅度': {
                    'score': dimension_3,
                    'max_score': 5.0,
                    'percentage': round(dimension_3 / 5.0 * 100, 1),
                    'weight': 0.3
                }
            },
            'weighted_score': weighted_score,
            'total_score_100': total_score_100,
            'raw_total': raw_total,
            'raw_max': 40
        }
    
    def _extract_parts(self, response: str) -> Tuple[str, str]:
        """提取内心OS和外部回复部分"""
        inner_match = self.inner_os_pattern.search(response)
        outer_match = self.outer_response_pattern.search(response)
        
        inner_os = inner_match.group(1).strip() if inner_match else ""
        outer_response = outer_match.group(1).strip() if outer_match else ""
        
        return inner_os, outer_response
    
    # ============================================================================
    # 考察点A：格式完整性（高置信度）
    # ============================================================================
    
    def _eval_A_format_integrity(self, response: str, inner_os: str, outer_response: str) -> Dict[str, Any]:
        """
        A. 格式完整性 (0-5分)
        5分：完美遵循格式
        4分：极少瑕疵
        3分：部分遵循
        2分：严重缺陷
        1分：几乎失败
        0分：拒绝执行
        """
        score = 5
        issues = []
        
        # 检查是否包含内心OS标签
        has_inner_tag = bool(re.search(r'\*\*内心OS\*\*', response, re.IGNORECASE))
        # 检查是否包含A标签
        has_outer_tag = bool(re.search(r'\*\*A\*\*', response, re.IGNORECASE))
        
        if not has_inner_tag and not has_outer_tag:
            score = 0
            issues.append("完全缺失双格式标签")
            reason = "拒绝执行格式指令"
        elif not has_inner_tag:
            score = 1
            issues.append("缺少内心OS标签")
            reason = "几乎失败，仅以单段式输出"
        elif not has_outer_tag:
            score = 1
            issues.append("缺少A的回复标签")
            reason = "几乎失败，仅有内心OS"
        elif not inner_os or not outer_response:
            score = 2
            issues.append("标签存在但内容缺失或混乱")
            reason = "严重缺陷，格式不完整"
        else:
            # 检查格式细节
            has_proper_format = bool(self.format_pattern.search(response))
            has_colon_inner = bool(re.search(r'\*\*内心OS\*\*[:：]', response))
            has_colon_outer = bool(re.search(r'\*\*A\*\*[:：]', response))
            
            if has_proper_format and has_colon_inner and has_colon_outer:
                score = 5
                reason = "完美遵循，格式清晰无误"
            elif has_proper_format:
                score = 4
                issues.append("格式正确但冒号或细节有微小瑕疵")
                reason = "极少瑕疵，绝大多数格式正确"
            else:
                score = 3
                issues.append("内容混在一起或排版有明显问题")
                reason = "部分遵循，格式有明显缺陷"
        
        return {
            'score': score,
            'max_score': 5,
            'confidence': 'high',
            'reason': reason,
            'issues': issues,
            'manual_adjust_hint': None if score >= 4 else '建议人工检查格式细节'
        }
    
    # ============================================================================
    # 考察点B：身份与职业基础加载（中置信度）
    # ============================================================================
    
    def _eval_B_identity_loading(self, response: str, inner_os: str, outer_response: str, test_case: Dict) -> Dict[str, Any]:
        """
        B. 身份与职业基础加载 (0-5分)
        5分：完美入戏
        4分：非常稳定
        3分：略有动摇
        2分：多次出戏
        1分：角色崩塌
        0分：拒绝扮演
        """
        # 检查是否拒绝角色扮演
        refuse_keywords = ['我是AI', '我是语言模型', '我是助手', '我无法扮演', '我不能假装']
        if any(kw in response for kw in refuse_keywords) and test_case['id'] != 'T7':
            return {
                'score': 0,
                'max_score': 5,
                'confidence': 'high',
                'reason': '拒绝扮演角色',
                'issues': ['检测到拒绝扮演的表述'],
                'manual_adjust_hint': '确认是否真的拒绝扮演'
            }
        
        # 检查建筑师身份相关词汇
        architect_keywords = ['建筑', '设计', '图纸', '项目', '方案', '规划', '结构', '承重', '地基']
        architect_score = sum(1 for kw in architect_keywords if kw in response)
        
        # 检查年上者特征
        mature_keywords = ['您', '呢', '呀']
        mature_score = sum(1 for kw in mature_keywords if kw in outer_response)
        
        # 检查是否出戏（AI助手口吻）
        ooc_keywords = ['很高兴为您', '我建议您', '希望对您有帮助', '如果您需要']
        ooc_count = sum(1 for kw in ooc_keywords if kw in response)
        
        # 评分逻辑
        if architect_score >= 3 and mature_score >= 2 and ooc_count == 0:
            score = 5
            reason = "完美入戏，始终保持建筑师身份"
        elif architect_score >= 2 and ooc_count == 0:
            score = 4
            reason = "非常稳定，身份清晰"
        elif architect_score >= 1 or ooc_count <= 1:
            score = 3
            reason = "略有动摇，但基本在角色内"
        elif ooc_count >= 2:
            score = 2
            reason = "多次出戏，AI助手口吻明显"
        else:
            score = 1
            reason = "角色崩塌，完全失去建筑师身份"
        
        return {
            'score': score,
            'max_score': 5,
            'confidence': 'medium',
            'reason': reason,
            'issues': [],
            'details': {
                'architect_keywords_found': architect_score,
                'mature_tone': mature_score > 0,
                'ooc_count': ooc_count
            },
            'manual_adjust_hint': '建议人工判断职业身份的自然度' if score <= 3 else None
        }
    
    # ============================================================================
    # 考察点C：语言风格基础（中置信度）
    # ============================================================================
    
    def _eval_C_language_style(self, response: str, inner_os: str, outer_response: str) -> Dict[str, Any]:
        """
        C. 语言风格基础 (0-5分)
        5分：完美贴合
        4分：良好稳定
        3分：基本符合
        2分：风格混乱
        1分：风格失败
        """
        # 检查敬语使用
        polite_count = outer_response.count('您')
        has_polite_particles = any(p in outer_response for p in ['呢', '呀', '吗', '呐'])
        
        # 检查舒缓语气词
        calm_markers = ['...', '。', '，', '、']
        calm_score = sum(outer_response.count(m) for m in calm_markers)
        
        # 检查急躁或不当用词
        hasty_keywords = ['快点', '赶紧', '立刻', '马上', '！！', '啊喂', '哎呀呀']
        hasty_count = sum(1 for kw in hasty_keywords if kw in outer_response)
        
        # 检查是否使用"你"而非"您"
        informal_you_count = outer_response.count('你') - outer_response.count('你的') - outer_response.count('你们')
        
        # 评分
        if polite_count >= 2 and has_polite_particles and hasty_count == 0 and calm_score >= 5:
            score = 5
            reason = "完美贴合：舒缓语速、从容节奏、使用敬语"
        elif polite_count >= 2 and hasty_count == 0:
            score = 4
            reason = "良好稳定：措辞有礼，高频使用'您'"
        elif polite_count >= 1 or hasty_count == 0:
            score = 3
            reason = "基本符合：有礼貌体现，但节奏感不够"
        elif informal_you_count > polite_count:
            score = 2
            reason = "风格混乱：敬语使用不稳定"
        else:
            score = 1
            reason = "风格失败：语言风格与设定完全相反"
        
        return {
            'score': score,
            'max_score': 5,
            'confidence': 'medium',
            'reason': reason,
            'issues': [],
            'details': {
                'polite_count': polite_count,
                'has_particles': has_polite_particles,
                'hasty_markers': hasty_count
            },
            'manual_adjust_hint': '建议人工判断语速节奏感' if score <= 3 else None
        }
    
    # ============================================================================
    # 考察点D：矛盾性呈现（低置信度）
    # ============================================================================
    
    def _eval_D_contradiction(self, response: str, inner_os: str, outer_response: str, test_case: Dict) -> Dict[str, Any]:
        """
        D. 矛盾性呈现（腹黑与温良）(0-5分)
        5分：极致反差
        4分：良好反差
        3分：反差不足
        2分：表里一致
        1分：情绪失控
        """
        # 检查内心OS的冷酷/毒辣程度
        harsh_words = ['蠢', '愚', '可笑', '无知', '短浅', '可悲', '暴发户', '白痴', '傻', '可怜', '可悲']
        harsh_count = sum(1 for word in harsh_words if word in inner_os)
        
        # 检查外部回复的礼貌程度
        polite_markers = ['您', '呢', '呀', '吗', '微笑', '笑']
        polite_count = sum(1 for marker in polite_markers if marker in outer_response)
        
        # 检查高级讽刺/隐晦威胁
        sarcasm_markers = ['...', '呢', '呀', '不吉利', '崩塌', '后果', '恐怕', '可惜', '有意思']
        sarcasm_count = sum(1 for marker in sarcasm_markers if marker in outer_response)
        
        # 检查是否情绪失控
        angry_markers = ['不行', '休想', '做梦', '滚', '闭嘴', '！！！']
        angry_count = sum(1 for marker in angry_markers if marker in outer_response)
        
        # 评分
        if angry_count > 0:
            score = 1
            reason = "情绪失控：外部回复出现明显愤怒"
        elif harsh_count == 0 and polite_count == 0:
            score = 2
            reason = "表里一致：内外都平淡，缺乏矛盾性"
        elif harsh_count == 0:
            score = 3
            reason = "反差不足：内心OS不够冷酷"
        elif harsh_count >= 2 and polite_count >= 2 and sarcasm_count >= 2:
            score = 5
            reason = "极致反差：内心冷酷+外部礼貌+高级讽刺"
        elif harsh_count >= 1 and polite_count >= 2:
            score = 4
            reason = "良好反差：内心冷酷+外部礼貌，但缺乏高级讽刺"
        else:
            score = 3
            reason = "反差不足：矛盾感体现不够"
        
        return {
            'score': score,
            'max_score': 5,
            'confidence': 'low',
            'reason': reason,
            'issues': [],
            'details': {
                'harsh_words_count': harsh_count,
                'polite_markers_count': polite_count,
                'sarcasm_markers_count': sarcasm_count
            },
            'manual_adjust_hint': '⚠️ 建议人工复核：反差感和讽刺度判断主观性强'
        }
    
    # ============================================================================
    # 考察点E：特定特征触发（中置信度）
    # ============================================================================
    
    def _eval_E_special_features(self, response: str, inner_os: str, outer_response: str, test_case: Dict) -> Dict[str, Any]:
        """
        E. 特定特征触发（猫/鸟、神经大条）(0-5分)
        5分：自然融入
        4分：准确触发
        3分：部分触发
        2分：关键词堆砌
        1分：忽略特征
        0分：特征反转
        """
        test_id = test_case['id']
        
        # T5: 猫奴特征
        if test_id == 'T5':
            cat_love_words = ['可爱', '喜欢', '爱', '柔软', '优雅', '温柔', '美好', '纯粹', '迷人']
            cat_mention = '猫' in response
            love_expression = sum(1 for word in cat_love_words if word in response)
            hate_expression = any(word in response for word in ['讨厌', '不喜欢', '无感', '一般'])
            
            if hate_expression:
                score = 0
                reason = "特征反转：表示不喜欢猫"
            elif not cat_mention:
                score = 1
                reason = "忽略特征：未提及猫"
            elif love_expression == 0:
                score = 2
                reason = "关键词堆砌：仅机械提到'猫'字"
            elif love_expression <= 2:
                score = 3
                reason = "部分触发：有提及但表达较简短"
            elif len(outer_response) > 50 and love_expression >= 2:
                score = 5
                reason = "自然融入：生动展现对猫的喜爱"
            else:
                score = 4
                reason = "准确触发：表达了喜爱但略显直接"
        
        # T6: 神经大条特征
        elif test_id == 'T6':
            absent_minded_words = ['忘', '找', '想不起', '走神', '迷糊', '哎呀', '糟糕', '记错', '丢']
            absent_mention = sum(1 for word in absent_minded_words if word in outer_response)
            
            # 检查是否承认迷糊
            admits_confusion = any(phrase in response for phrase in ['确实', '是呀', '刚才', '抱歉'])
            
            if absent_mention == 0:
                score = 1
                reason = "忽略特征：未展现神经大条"
            elif absent_mention >= 3 and admits_confusion:
                score = 5
                reason = "自然融入：巧妙展现迷糊状态"
            elif absent_mention >= 2:
                score = 4
                reason = "准确触发：承认了迷糊"
            elif absent_mention == 1:
                score = 3
                reason = "部分触发：略微提及但不明显"
            else:
                score = 2
                reason = "关键词堆砌：生硬提及"
        
        # 其他测试用例：不涉及特定特征
        else:
            score = 3
            reason = "N/A：本测试用例不涉及特定特征，给予基准分"
            return {
                'score': score,
                'max_score': 5,
                'confidence': 'high',
                'reason': reason,
                'issues': [],
                'manual_adjust_hint': None
            }
        
        return {
            'score': score,
            'max_score': 5,
            'confidence': 'medium',
            'reason': reason,
            'issues': [],
            'manual_adjust_hint': '建议人工判断特征展现的自然度' if score <= 3 else None
        }
    
    # ============================================================================
    # 考察点F：职业隐喻运用（中置信度）
    # ============================================================================
    
    def _eval_F_profession_metaphor(self, response: str, inner_os: str, outer_response: str, test_case: Dict) -> Dict[str, Any]:
        """
        F. 职业隐喻运用 (0-5分)
        5分：恰当精妙
        4分：准确运用
        3分：勉强提及
        2分：极少运用
        1分：完全失败
        """
        # 建筑术语列表
        architecture_terms = [
            '地基', '承重', '结构', '蓝图', '框架', '基石', '支柱', '梁', '柱', 
            '稳固', '根基', '崩塌', '建筑', '设计', '图纸', '规划', '施工',
            '材料', '钢筋', '水泥', '砖瓦', '楼层', '空间', '布局'
        ]
        
        # 统计建筑术语使用
        terms_used = [term for term in architecture_terms if term in response]
        term_count = len(terms_used)
        
        # 检查是否用于比喻（关键：出现在人生、生活、情感等语境中）
        metaphor_context = ['人生', '生活', '情感', '关系', '选择', '方向', '未来', '迷茫', '困惑']
        has_metaphor_context = any(ctx in response for ctx in metaphor_context)
        
        # 检查深度表达
        deep_expression = len(outer_response) > 80 and term_count >= 2
        
        # 评分
        if term_count == 0:
            score = 1
            reason = "完全失败：未体现职业特色"
        elif term_count == 1 and not has_metaphor_context:
            score = 2
            reason = "极少运用：仅在介绍项目时提及"
        elif term_count >= 1 and not has_metaphor_context:
            score = 3
            reason = "勉强提及：提到建筑词汇但比喻牵强"
        elif term_count >= 2 and has_metaphor_context:
            score = 4
            reason = "准确运用：使用建筑术语比喻生活"
        elif term_count >= 3 and has_metaphor_context and deep_expression:
            score = 5
            reason = "恰当精妙：隐喻自然且富有哲理"
        else:
            score = 3
            reason = "基本及格：有职业特色体现"
        
        return {
            'score': score,
            'max_score': 5,
            'confidence': 'medium',
            'reason': reason,
            'issues': [],
            'details': {
                'terms_used': terms_used[:5],  # 只显示前5个
                'term_count': term_count,
                'has_metaphor': has_metaphor_context
            },
            'manual_adjust_hint': '建议人工判断隐喻的精妙度' if score >= 4 else None
        }
    
    # ============================================================================
    # 考察点G：文本自然性与代入感（低置信度）
    # ============================================================================
    
    def _eval_G_text_naturalness(self, response: str, inner_os: str, outer_response: str) -> Dict[str, Any]:
        """
        G. 文本自然性与代入感 (0-5分)
        5分：极高自然度
        4分：良好自然度
        3分：一般流畅
        2分：低流畅度
        1分：难以阅读
        """
        # 检查文本长度（太短可能不够丰富）
        total_length = len(response)
        
        # 检查重复词汇
        words = response.split()
        unique_ratio = len(set(words)) / len(words) if words else 0
        
        # 检查句子结构重复（简单检测：连续相同字符）
        has_repetition = any(response.count(phrase) >= 3 for phrase in ['笑吟吟', '呢', '呀', '吗'])
        
        # 检查是否有语法错误迹象（简单检测）
        grammar_issues = response.count('  ') > 2  # 多余空格
        
        # 评分（由于高度主观，给出保守评分）
        if grammar_issues or total_length < 50:
            score = 2
            reason = "低流畅度：文本过短或有明显问题"
        elif has_repetition or unique_ratio < 0.5:
            score = 3
            reason = "一般流畅：有关键词重复或表达单一"
        elif total_length > 100 and unique_ratio > 0.6:
            score = 5
            reason = "极高自然度：文本丰富流畅（主观判断）"
        else:
            score = 4
            reason = "良好自然度：文本可读，略有AI痕迹"
        
        return {
            'score': score,
            'max_score': 5,
            'confidence': 'low',
            'reason': reason,
            'issues': [],
            'details': {
                'text_length': total_length,
                'unique_ratio': round(unique_ratio, 2)
            },
            'manual_adjust_hint': '⚠️ 高度主观，强烈建议人工复核自然度和代入感'
        }
    
    # ============================================================================
    # 考察点H：情绪表达的细腻度（低置信度）
    # ============================================================================
    
    def _eval_H_emotion_expression(self, response: str, inner_os: str, outer_response: str) -> Dict[str, Any]:
        """
        H. 情绪表达的细腻度 (0-5分)
        5分：情绪精准
        4分：情绪匹配
        3分：情绪缺失
        2分：情绪不当
        1分：混乱描述
        """
        # 检查是否有括弧描述
        bracket_descriptions = re.findall(r'[（(](.+?)[）)]', outer_response)
        has_brackets = len(bracket_descriptions) > 0
        
        # 检查细腻的情绪词
        emotion_words = ['微笑', '笑', '推了推眼镜', '看着', '轻声', '慢慢', '温柔', '玩味', '无奈']
        emotion_count = sum(1 for word in emotion_words if word in response)
        
        # 检查情绪词的多样性
        diverse_emotions = len([word for word in emotion_words if word in response])
        
        # 评分
        if not has_brackets and emotion_count == 0:
            score = 3
            reason = "情绪缺失：无括弧描述，缺乏情绪表达"
        elif has_brackets and diverse_emotions >= 2 and any('地' in desc for desc in bracket_descriptions):
            score = 5
            reason = "情绪精准：括弧描述细致且配合完美"
        elif has_brackets and emotion_count >= 1:
            score = 4
            reason = "情绪匹配：有括弧描述，用词相符"
        elif emotion_count >= 1:
            score = 3
            reason = "情绪基础：有情绪词但描述简单"
        else:
            score = 2
            reason = "情绪不当：描述与内容不符（需人工判断）"
        
        return {
            'score': score,
            'max_score': 5,
            'confidence': 'low',
            'reason': reason,
            'issues': [],
            'details': {
                'bracket_count': len(bracket_descriptions),
                'emotion_words_count': emotion_count
            },
            'manual_adjust_hint': '⚠️ 建议人工判断情绪描述是否与内容匹配'
        }
    
    # ============================================================================
    # 汇总统计
    # ============================================================================
    
    def generate_summary(self, evaluations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """生成多个测试用例的汇总统计"""
        if not evaluations:
            return {
                'total_tests': 0,
                'average_score_100': 0,
                'average_weighted': 0,
                'dimension_averages': {}
            }
        
        total_tests = len(evaluations)
        avg_score_100 = sum(e['total_score_100'] for e in evaluations) / total_tests
        avg_weighted = sum(e['weighted_score'] for e in evaluations) / total_tests
        
        # 计算各维度平均分
        dim1_scores = [e['dimension_scores']['维度一_基础指令遵循度']['score'] for e in evaluations]
        dim2_scores = [e['dimension_scores']['维度二_核心人设匹配度']['score'] for e in evaluations]
        dim3_scores = [e['dimension_scores']['维度三_输出表达流畅度']['score'] for e in evaluations]
        
        return {
            'total_tests': total_tests,
            'average_score_100': round(avg_score_100, 1),
            'average_weighted': round(avg_weighted, 2),
            'dimension_averages': {
                '维度一_基础指令遵循度': round(sum(dim1_scores) / total_tests, 2),
                '维度二_核心人设匹配度': round(sum(dim2_scores) / total_tests, 2),
                '维度三_输出表达流畅度': round(sum(dim3_scores) / total_tests, 2)
            }
        }
