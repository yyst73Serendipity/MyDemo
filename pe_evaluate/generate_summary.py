#!/usr/bin/env python3
"""
汇总报告生成脚本
扫描 results/reports 目录下的所有评测报告，生成综合对比分析汇总报告
使用 DMXAPI 调用 Gemini-3-Pro-Preview 进行智能分析
"""

import os
import sys
from summary_generator import SummaryGenerator, DMXAPI_CONFIG


def main():
    """主函数"""
    print("="*60)
    print("🚀 A先生角色Prompt评测 - 汇总报告生成工具")
    print("="*60)
    print()
    
    # 检查 API Key 配置
    if DMXAPI_CONFIG["api_key"] == "YOUR_DMXAPI_KEY_HERE":
        print("⚠️  警告: DMXAPI API Key 未配置")
        print("   请在 summary_generator.py 文件中配置您的 API Key")
        print("   位置: DMXAPI_CONFIG['api_key']")
        print()
        user_input = input("是否继续？（将使用备用规则生成报告）[y/N]: ")
        if user_input.lower() not in ['y', 'yes']:
            print("已取消操作")
            sys.exit(0)
        print()
    else:
        print("✅ DMXAPI 配置已加载")
        print(f"   模型: {DMXAPI_CONFIG['model_id']}")
        print(f"   端点: {DMXAPI_CONFIG['base_url']}")
        print()
    
    # 设置目录路径
    reports_dir = "results/reports"
    summaries_dir = "results/summaries"
    
    # 检查reports目录是否存在
    if not os.path.exists(reports_dir):
        print(f"❌ 错误: 找不到报告目录 '{reports_dir}'")
        print("   请确保已经运行过评测程序并生成了报告")
        sys.exit(1)
    
    # 检查是否有报告文件
    report_files = [f for f in os.listdir(reports_dir) 
                   if f.startswith('evaluation_report_') and f.endswith('.md')]
    
    if not report_files:
        print(f"❌ 错误: 在 '{reports_dir}' 目录下没有找到任何报告文件")
        print("   报告文件应该以 'evaluation_report_' 开头，以 '.md' 结尾")
        sys.exit(1)
    
    print(f"📁 报告目录: {reports_dir}")
    print(f"📊 找到 {len(report_files)} 个报告文件")
    print()
    
    # 创建汇总生成器
    generator = SummaryGenerator(
        reports_dir=reports_dir,
        output_dir=summaries_dir
    )
    
    print("🔍 正在解析报告文件...")
    models_data = generator.parse_all_reports()
    
    if not models_data:
        print("❌ 错误: 无法从报告文件中提取有效数据")
        print("   请检查报告文件格式是否正确")
        sys.exit(1)
    
    print(f"✅ 成功解析 {len(models_data)} 个模型的评分数据")
    print()
    
    # 显示模型列表
    print("📋 参与评测的模型:")
    for i, model in enumerate(models_data, 1):
        print(f"   {i}. {model['model_name']} - {model['weighted_score_100']:.1f}/100")
    print()
    
    # 生成汇总报告
    print("📝 正在生成汇总报告...")
    report_path = generator.generate_summary_report(models_data)
    
    print()
    print("="*60)
    print("🎉 汇总报告生成完成！")
    print("="*60)
    print()
    print(f"📄 报告位置: {report_path}")
    print()
    print("💡 提示:")
    print(f"   - 汇总报告已保存到 '{summaries_dir}' 目录")
    print("   - 报告包含三部分：量化对比、深度分析、产品建议")
    print("   - 可使用 Markdown 阅读器查看完整格式")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断操作")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

