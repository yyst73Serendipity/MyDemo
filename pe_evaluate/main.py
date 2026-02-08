"""
AI角色Prompt评测系统 - 主程序
用于自动化测试多个AI模型对角色扮演的表现
"""

import os
import json
import yaml
from datetime import datetime
from typing import Dict, List, Any

from model_clients import ModelClientFactory, test_client
from evaluator import ResponseEvaluator
from report_generator import ReportGenerator
from logger import DualLogger


class PromptEvaluationSystem:
    """Prompt评测系统主类"""
    
    def __init__(self, logger: DualLogger, config_path: str = "config.yaml"):
        """初始化评测系统"""
        self.logger = logger
        self.logger.print("🚀 初始化AI角色Prompt评测系统...")
        
        # 加载配置
        self.config = self._load_config(config_path)
        
        # 加载角色prompt
        self.system_prompt = self._load_prompt_template()
        
        # 加载测试用例
        self.test_cases = self._load_test_cases()
        
        # 创建模型客户端
        self.logger.print("\n📦 正在加载AI模型客户端...")
        
        # 读取 DMXAPI 统一配置（如果存在）
        dmxapi_config = self.config.get('dmxapi', None)
        if dmxapi_config:
            self.logger.print(f"  🔗 使用 DMXAPI 聚合平台: {dmxapi_config.get('base_url', 'N/A')}")
        
        self.clients = ModelClientFactory.create_all_clients(
            self.config['models'], 
            self.logger, 
            dmxapi_config
        )
        
        if not self.clients:
            raise RuntimeError("❌ 没有成功加载任何模型客户端，请检查配置文件")
        
        # 创建评估器和报告生成器
        self.evaluator = ResponseEvaluator()
        
        raw_responses_dir = self.config['output']['raw_responses_dir']
        reports_dir = self.config['output']['reports_dir']
        
        os.makedirs(raw_responses_dir, exist_ok=True)
        os.makedirs(reports_dir, exist_ok=True)
        
        self.raw_responses_dir = raw_responses_dir
        self.report_generator = ReportGenerator(reports_dir)
        
        self.logger.print(f"✅ 系统初始化完成！")
        self.logger.print(f"   - 已加载 {len(self.clients)} 个模型")
        self.logger.print(f"   - 已加载 {len(self.test_cases)} 个测试用例")
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """加载配置文件"""
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _load_prompt_template(self) -> str:
        """加载角色prompt模板"""
        with open('prompt_template.txt', 'r', encoding='utf-8') as f:
            return f.read()
    
    def _load_test_cases(self) -> List[Dict[str, Any]]:
        """加载测试用例"""
        with open('test_cases.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data['test_cases']
    
    def run_evaluation(self) -> Dict[str, Any]:
        """运行完整的评测流程"""
        self.logger.print("\n" + "="*60)
        self.logger.print("🎯 开始执行评测...")
        self.logger.print("="*60 + "\n")
        
        all_results = {}
        
        # 对每个模型进行测试
        for model_name, client in self.clients.items():
            self.logger.print(f"\n{'='*60}")
            self.logger.print(f"🤖 正在测试模型: {model_name}")
            self.logger.print(f"{'='*60}\n")
            
            model_results = {}
            
            # 对每个测试用例进行测试
            for i, test_case in enumerate(self.test_cases, 1):
                test_id = test_case['id']
                self.logger.print(f"\n[{i}/{len(self.test_cases)}] 测试用例 {test_id}: {test_case['category']}")
                self.logger.print(f"  📝 输入: {test_case['input'][:50]}...")
                
                # 调用模型
                result = test_client(client, self.system_prompt, test_case['input'], self.logger)
                
                if result:
                    response_text = result['content']
                    
                    # 保存原始响应
                    self._save_raw_response(model_name, test_id, test_case, result)
                    
                    # 自动评估
                    evaluation = self.evaluator.evaluate_response(test_case, response_text)
                    
                    # 显示评分（使用新的数据结构）
                    self.logger.print(f"  📊 评估得分: {evaluation['raw_total']}/{evaluation['raw_max']} (原始分)")
                    self.logger.print(f"  🎯 加权总分: {evaluation['total_score_100']:.1f}/100")
                    self.logger.print(f"  ✅ 测试完成")
                    
                    model_results[test_id] = {
                        'response': response_text,
                        'evaluation': evaluation,
                        'raw_result': result
                    }
                else:
                    self.logger.print(f"  ❌ 调用失败，跳过此测试")
                    model_results[test_id] = {
                        'response': None,
                        'evaluation': None,
                        'error': 'API调用失败'
                    }
            
            all_results[model_name] = model_results
        
        return all_results
    
    def _save_raw_response(self, model_name: str, test_id: str, 
                          test_case: Dict[str, Any], result: Dict[str, Any]) -> None:
        """保存原始响应到JSON文件"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # 清理模型名称中的特殊字符（替换 / 为 _）
        safe_model_name = model_name.replace('/', '_').replace('\\', '_')
        filename = f"{safe_model_name}_{test_id}_{timestamp}.json"
        filepath = os.path.join(self.raw_responses_dir, filename)
        
        data = {
            "model": model_name,
            "test_case_id": test_id,
            "test_category": test_case['category'],
            "timestamp": timestamp,
            "input": test_case['input'],
            "intent": test_case['intent'],
            "response": result['content'],
            "raw_api_response": result.get('raw', {}),
            "usage": result.get('usage', {})
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def generate_report(self, test_results: Dict[str, Any]) -> str:
        """生成评估报告"""
        self.logger.print("\n" + "="*60)
        self.logger.print("📄 正在生成评估报告...")
        self.logger.print("="*60 + "\n")
        
        report_path = self.report_generator.generate_report(test_results, self.test_cases)
        
        self.logger.print(f"✅ 报告已生成: {report_path}")
        
        # 打印简单摘要
        summary = self.report_generator.generate_simple_summary(test_results)
        self.logger.print(summary)
        
        return report_path


def main():
    """主函数"""
    # 创建日志记录器
    logger = DualLogger(log_dir="results/logs", enable_console=True)
    
    try:
        # 创建评测系统实例
        system = PromptEvaluationSystem(logger)
        
        # 运行评测
        results = system.run_evaluation()
        
        # 生成报告
        report_path = system.generate_report(results)
        
        logger.print("\n" + "="*60)
        logger.print("🎉 评测完成！")
        logger.print("="*60)
        logger.print(f"\n📊 详细报告: {report_path}")
        logger.print(f"📁 原始响应: {system.raw_responses_dir}")
        logger.print(f"📋 执行日志: {logger.get_log_path()}")
        logger.print("\n💡 提示: 请查看报告并填写人工评价部分\n")
        
    except FileNotFoundError as e:
        logger.print(f"❌ 文件未找到: {e}")
        logger.print("请确保以下文件存在:")
        logger.print("  - config.yaml")
        logger.print("  - prompt_template.txt")
        logger.print("  - test_cases.json")
    except Exception as e:
        logger.print(f"❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        # 同时将traceback写入日志
        import io
        trace_str = io.StringIO()
        traceback.print_exc(file=trace_str)
        logger.print(trace_str.getvalue())
    finally:
        # 关闭日志文件
        logger.close()


if __name__ == "__main__":
    main()

