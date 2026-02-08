"""
测试 DMXAPI 使用 OpenAI SDK 的调用
"""

from openai import OpenAI

# 配置
# API_KEY = "sk-xxxxxxx"
API_KEY = "sk-xWTXMqYt7q0iomTCOa9f545uiC3evcb4adBvwdr4Ihvgafpj"
BASE_URL = "https://www.dmxapi.com/v1"
MODEL = "deepseek-ai/DeepSeek-R1"

print("=" * 60)
print("测试 DMXAPI 调用（使用 OpenAI SDK）")
print("=" * 60)

try:
    # 初始化客户端
    client = OpenAI(
        api_key=API_KEY,
        base_url=BASE_URL
    )
    
    print(f"\n✅ OpenAI 客户端初始化成功")
    print(f"   Base URL: {BASE_URL}")
    print(f"   Model: {MODEL}")
    
    # 发送测试请求
    print(f"\n🔄 发送测试请求...")
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "你是一个友好的助手。"},
            {"role": "user", "content": "你好，请简单介绍一下你自己。"}
        ],
        temperature=0.7,
        max_tokens=100
    )
    
    # 输出结果
    print(f"\n✅ 调用成功！")
    print(f"\n📝 模型回复:")
    print("-" * 60)
    print(response.choices[0].message.content)
    print("-" * 60)
    
    # 输出使用统计
    if response.usage:
        print(f"\n📊 Token 使用统计:")
        print(f"   Prompt tokens: {response.usage.prompt_tokens}")
        print(f"   Completion tokens: {response.usage.completion_tokens}")
        print(f"   Total tokens: {response.usage.total_tokens}")
    
    print(f"\n🎉 测试成功！DMXAPI 调用正常。")

except Exception as e:
    print(f"\n❌ 测试失败！")
    print(f"错误信息: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)

