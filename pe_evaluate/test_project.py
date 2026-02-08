"""
简单的项目测试脚本
验证项目能否正常运行
"""

print("=" * 60)
print("🧪 项目环境测试")
print("=" * 60)

# 测试基础导入
try:
    from logger import DualLogger
    from evaluator import ResponseEvaluator
    from report_generator import ReportGenerator
    from model_clients import ModelClientFactory
    import yaml
    import json
    print("✅ 所有模块导入成功")
except ImportError as e:
    print(f"❌ 模块导入失败: {e}")
    exit(1)

# 测试配置文件
try:
    with open('config.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    print("✅ config.yaml 读取成功")
except Exception as e:
    print(f"❌ config.yaml 读取失败: {e}")
    exit(1)

# 测试测试用例文件
try:
    with open('test_cases.json', 'r', encoding='utf-8') as f:
        test_cases = json.load(f)
    print(f"✅ test_cases.json 读取成功 (共 {len(test_cases.get('test_cases', []))} 个测试用例)")
except Exception as e:
    print(f"❌ test_cases.json 读取失败: {e}")
    exit(1)

# 测试prompt模板
try:
    with open('prompt_template.txt', 'r', encoding='utf-8') as f:
        prompt = f.read()
    print("✅ prompt_template.txt 读取成功")
except Exception as e:
    print(f"❌ prompt_template.txt 读取失败: {e}")
    exit(1)

# 测试评估器
try:
    evaluator = ResponseEvaluator()
    print("✅ ResponseEvaluator 初始化成功")
except Exception as e:
    print(f"❌ ResponseEvaluator 初始化失败: {e}")
    exit(1)

print("=" * 60)
print("🎉 所有测试通过！项目可以正常运行！")
print("=" * 60)
print("\n📝 使用提示:")
print("1. 编辑 config.yaml 填入你的 API Key")
print("2. 将需要测试的模型的 enabled 设置为 true")
print("3. 运行: python main.py")
print()

