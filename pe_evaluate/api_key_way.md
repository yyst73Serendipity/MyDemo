# API KEY 接入方式总结

本文档总结了本项目（PE评测系统）中 API KEY 的接入方式、关键代码实现、代码规范和安全实践。

---

## 一、API KEY 配置方式

本项目支持两种 API KEY 配置方式：

### 1.1 统一配置方式（推荐）

**配置文件位置**：`config.yaml`

所有模型统一使用 DMXAPI 聚合平台，API KEY 在配置文件的 `dmxapi` 节点下统一配置：

```yaml
# DMXAPI 平台配置（统一配置）
dmxapi:
  api_key: "sk-xWTXMqYt7q0iomTCOa9f545uiC3evcb4adBvwdr4Ihvgafpj"  # 请在 dmxapi.cn 控制台生成并填写
  base_url: "https://www.dmxapi.com/v1"  # DMXAPI 固定中转地址
```

**配置特点**：
- 所有使用 `provider: "dmxapi"` 的模型共享同一个 API KEY
- 通过 `ModelClientFactory.create_all_clients()` 方法统一注入
- 配置集中管理，便于维护

**配置加载流程**：
1. `main.py` 中加载 `config.yaml` 文件
2. 提取 `dmxapi` 配置节点
3. 传递给 `ModelClientFactory.create_all_clients()` 方法
4. 工厂方法自动为所有 DMXAPI 模型注入 API KEY

**关键代码位置**：
- 配置文件：`config.yaml` 第 5-7 行
- 配置加载：`main.py` 第 39-46 行
- 注入逻辑：`model_clients.py` 第 284-288 行

### 1.2 独立配置方式

**配置文件位置**：`summary_generator.py`

汇总报告生成模块使用独立的 API KEY 配置：

```python
# DMXAPI 配置（兼容 OpenAI 格式）
DMXAPI_CONFIG = {
    "api_key": "sk-xWTXMqYt7q0iomTCOa9f545uiC3evcb4adBvwdr4Ihvgafpj",
    "base_url": "https://www.dmxapi.com/v1",
    "model_id": "gemini-3-pro-preview",
    "temperature": 0.7,
    "max_tokens": 4000
}
```

**配置特点**：
- 独立于主配置系统
- 支持通过构造函数参数覆盖（`api_key` 参数）
- 用于汇总报告生成功能

**使用方式**：
```python
# 方式1：使用默认配置
generator = SummaryGenerator(
    reports_dir="results/reports",
    output_dir="results/summaries"
)

# 方式2：通过参数覆盖
generator = SummaryGenerator(
    reports_dir="results/reports",
    output_dir="results/summaries",
    api_key="your-custom-api-key"
)
```

**关键代码位置**：
- 配置定义：`summary_generator.py` 第 16-23 行
- 参数覆盖：`summary_generator.py` 第 44 行

### 1.3 配置优先级

配置优先级从高到低：
1. **构造函数参数**：`SummaryGenerator(api_key="...")` 传入的参数
2. **模块级配置**：`summary_generator.py` 中的 `DMXAPI_CONFIG`
3. **YAML 配置**：`config.yaml` 中的 `dmxapi.api_key`

---

## 二、关键代码实现

### 2.1 ModelClientFactory 中的 API KEY 注入

**文件位置**：`model_clients.py`

**关键方法**：`create_all_clients()` （第 271-304 行）

```python
@classmethod
def create_all_clients(cls, configs: list, logger=None, dmxapi_config: Dict = None) -> Dict[str, BaseModelClient]:
    """
    创建所有启用的模型客户端
    
    Args:
        configs: 模型配置列表
        logger: 日志记录器
        dmxapi_config: DMXAPI 统一配置（包含 api_key 和 base_url）
    """
    clients = {}
    for config in configs:
        if config.get('enabled', True):
            try:
                # 如果是 DMXAPI 提供商，使用统一的 API Key 和 base_url
                if config.get('provider') == 'dmxapi' and dmxapi_config:
                    config = config.copy()  # 避免修改原配置
                    config['api_key'] = dmxapi_config.get('api_key', '')
                    config['base_url'] = dmxapi_config.get('base_url', 'https://www.dmxapi.cn/v1')
                
                client = cls.create_client(config)
                clients[config['name']] = client
                # ... 日志输出
            except Exception as e:
                # ... 错误处理
    return clients
```

**实现要点**：
- 使用 `config.copy()` 避免修改原始配置对象
- 通过 `dmxapi_config` 参数统一注入 API KEY
- 支持默认值：`dmxapi_config.get('api_key', '')`
- 自动为所有 `provider == 'dmxapi'` 的模型注入配置

### 2.2 各客户端类的 API KEY 使用

#### 2.2.1 BaseModelClient 基类

**文件位置**：`model_clients.py` 第 19-32 行

```python
class BaseModelClient(ABC):
    """模型客户端基类"""
    
    def __init__(self, config: Dict[str, Any]):
        self.name = config['name']
        self.model_id = config['model_id']
        self.api_key = config['api_key']  # 从配置中提取 API KEY
        self.base_url = config['base_url']
        self.params = config.get('params', {})
```

**规范**：
- 所有客户端类继承自 `BaseModelClient`
- API KEY 存储在实例变量 `self.api_key` 中
- 通过构造函数统一初始化

#### 2.2.2 DMXAPIClient（使用 OpenAI SDK）

**文件位置**：`model_clients.py` 第 202-244 行

```python
class DMXAPIClient(BaseModelClient):
    """DMXAPI 聚合平台客户端（使用 OpenAI SDK）"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
        # 初始化 OpenAI 客户端
        self.client = OpenAI(
            api_key=self.api_key,  # 使用继承的 API KEY
            base_url=self.base_url
        )
    
    def chat(self, system_prompt: str, user_message: str) -> Dict[str, Any]:
        """使用 OpenAI SDK 调用 DMXAPI"""
        response = self.client.chat.completions.create(
            model=self.model_id,
            messages=[...],
            temperature=self.params.get('temperature', 0.7),
            max_tokens=self.params.get('max_tokens', 4000)
        )
        # ... 返回结果处理
```

**特点**：
- 使用 OpenAI SDK，API KEY 通过 SDK 自动处理
- 无需手动设置 HTTP 请求头
- SDK 内部处理认证逻辑

#### 2.2.3 其他客户端（直接 HTTP 请求）

**文件位置**：`model_clients.py` 第 39-199 行

**OpenAIClient 示例**（第 39-67 行）：
```python
class OpenAIClient(BaseModelClient):
    """OpenAI GPT 客户端"""
    
    def chat(self, system_prompt: str, user_message: str) -> Dict[str, Any]:
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",  # 在请求头中设置 API KEY
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model_id,
            "messages": [...],
            "temperature": self.params.get('temperature', 0.7),
            "max_tokens": self.params.get('max_tokens', 2000)
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        # ... 处理响应
```

**GoogleGeminiClient 示例**（第 70-106 行）：
```python
class GoogleGeminiClient(BaseModelClient):
    """Google Gemini 客户端"""
    
    def chat(self, system_prompt: str, user_message: str) -> Dict[str, Any]:
        # Gemini API 将 API KEY 放在 URL 参数中
        url = f"{self.base_url}/models/{self.model_id}:generateContent?key={self.api_key}"
        headers = {
            "Content-Type": "application/json"
        }
        # ... 发送请求
```

**其他客户端**（DeepSeekClient、QwenClient、MoonshotClient）：
- 统一使用 `Authorization: Bearer {api_key}` 请求头
- 代码结构一致，便于维护

### 2.3 HTTP 请求头中的 Authorization 设置

**标准格式**：
```python
headers = {
    "Authorization": f"Bearer {self.api_key}",
    "Content-Type": "application/json"
}
```

**特殊处理**：
- **Google Gemini**：API KEY 放在 URL 查询参数中，而非请求头
- **DMXAPI（OpenAI SDK）**：由 SDK 自动处理，无需手动设置

---

## 三、代码规范

### 3.1 配置文件的组织结构

**YAML 配置文件规范**（`config.yaml`）：

```yaml
# 平台级配置（统一）
dmxapi:
  api_key: "..."      # 统一 API KEY
  base_url: "..."     # 统一端点地址

# 模型级配置（独立）
models:
  - name: "Model-Name"
    provider: "dmxapi"  # 指定使用统一配置
    model_id: "model-id"
    enabled: true
    params:
      temperature: 0.7
      max_tokens: 4000
```

**规范要点**：
- 平台配置与模型配置分离
- 使用 `provider` 字段标识配置来源
- 模型配置不包含 `api_key`，由工厂方法注入

### 3.2 API KEY 的传递方式

**传递链**：
```
config.yaml 
  → main.py (加载配置)
    → ModelClientFactory.create_all_clients(dmxapi_config)
      → 为每个模型注入 api_key
        → BaseModelClient.__init__(config)
          → self.api_key 存储
            → 各客户端类的 chat() 方法使用
```

**规范**：
- **不直接传递**：不在模型配置中硬编码 API KEY
- **统一注入**：通过工厂方法统一注入
- **避免修改原配置**：使用 `config.copy()` 创建副本

### 3.3 错误处理和验证机制

**配置验证**（`generate_summary.py` 第 20-30 行）：
```python
# 检查 API Key 配置
if DMXAPI_CONFIG["api_key"] == "YOUR_DMXAPI_KEY_HERE":
    print("⚠️  警告: DMXAPI API Key 未配置")
    print("   请在 summary_generator.py 文件中配置您的 API Key")
    user_input = input("是否继续？（将使用备用规则生成报告）[y/N]: ")
    if user_input.lower() not in ['y', 'yes']:
        sys.exit(0)
```

**错误处理**（`model_clients.py` 第 297-302 行）：
```python
try:
    client = cls.create_client(config)
    clients[config['name']] = client
    msg = f"✅ 已加载模型: {config['name']}"
except Exception as e:
    msg = f"❌ 加载模型 {config['name']} 失败: {str(e)}"
    # 记录错误但继续加载其他模型
```

**规范**：
- 配置缺失时给出明确提示
- 单个模型加载失败不影响其他模型
- 错误信息包含具体模型名称和错误原因

---

## 四、安全实践

### 4.1 Git 忽略配置

**文件位置**：`.gitignore` 第 43 行

```gitignore
# 项目特定
config.yaml  # 包含API Key，不要提交
results/     # 测试结果，不要提交
```

**安全措施**：
- `config.yaml` 文件被 Git 忽略，避免提交敏感信息
- 测试结果目录也被忽略，保护测试数据

### 4.2 敏感信息保护

**当前问题**：
1. ❌ `summary_generator.py` 中硬编码了 API KEY（第 18 行）
2. ❌ `config.yaml` 中包含了真实的 API KEY（第 6 行）
3. ✅ `.gitignore` 已配置忽略 `config.yaml`

**建议改进**：
1. **使用环境变量**：
   ```python
   import os
   api_key = os.getenv('DMXAPI_API_KEY', 'default_key')
   ```

2. **配置文件模板**：
   - 创建 `config.yaml.example` 作为模板
   - 在模板中使用占位符：`api_key: "YOUR_API_KEY_HERE"`
   - 实际配置保留在 `config.yaml`（已忽略）

3. **代码中移除硬编码**：
   ```python
   DMXAPI_CONFIG = {
       "api_key": os.getenv('DMXAPI_API_KEY', 'YOUR_DMXAPI_KEY_HERE'),
       # ...
   }
   ```

### 4.3 最佳实践建议

1. **配置分离**：
   - ✅ 使用配置文件管理 API KEY
   - ✅ 配置文件加入 `.gitignore`
   - ❌ 避免在代码中硬编码

2. **统一管理**：
   - ✅ 使用统一的配置注入机制
   - ✅ 通过工厂模式管理客户端创建
   - ✅ 配置集中在一个位置

3. **错误处理**：
   - ✅ 配置缺失时给出明确提示
   - ✅ API 调用失败时记录详细错误
   - ✅ 支持重试机制（`test_client` 函数）

4. **代码复用**：
   - ✅ 使用基类统一接口
   - ✅ 工厂模式统一创建逻辑
   - ✅ 配置注入避免重复代码

---

## 五、代码示例

### 5.1 完整使用流程

**步骤1：配置 API KEY**（`config.yaml`）
```yaml
dmxapi:
  api_key: "your-api-key-here"
  base_url: "https://www.dmxapi.com/v1"
```

**步骤2：加载配置并创建客户端**（`main.py`）
```python
# 加载配置
config = yaml.safe_load(open('config.yaml', 'r', encoding='utf-8'))

# 提取 DMXAPI 配置
dmxapi_config = config.get('dmxapi', None)

# 创建所有客户端（自动注入 API KEY）
clients = ModelClientFactory.create_all_clients(
    config['models'], 
    logger=self.logger, 
    dmxapi_config=dmxapi_config
)
```

**步骤3：使用客户端调用 API**（`model_clients.py`）
```python
# 客户端自动使用注入的 API KEY
result = client.chat(system_prompt, user_message)
```

### 5.2 独立配置使用示例

**汇总报告生成**（`generate_summary.py`）
```python
from summary_generator import SummaryGenerator

# 使用默认配置
generator = SummaryGenerator(
    reports_dir="results/reports",
    output_dir="results/summaries"
)

# 或使用自定义 API KEY
generator = SummaryGenerator(
    reports_dir="results/reports",
    output_dir="results/summaries",
    api_key="custom-api-key"
)

# 生成报告（内部自动使用 API KEY 调用 AI）
models_data = generator.parse_all_reports()
report_path = generator.generate_summary_report(models_data)
```

### 5.3 API KEY 在 HTTP 请求中的使用

**标准 Bearer Token 方式**：
```python
headers = {
    "Authorization": f"Bearer {self.api_key}",
    "Content-Type": "application/json"
}
response = requests.post(url, headers=headers, json=payload)
```

**URL 参数方式**（Google Gemini）：
```python
url = f"{self.base_url}/models/{self.model_id}:generateContent?key={self.api_key}"
response = requests.post(url, headers=headers, json=payload)
```

**SDK 方式**（DMXAPI）：
```python
from openai import OpenAI

client = OpenAI(
    api_key=self.api_key,
    base_url=self.base_url
)
response = client.chat.completions.create(...)
```

---

## 六、总结

### 6.1 配置方式对比

| 配置方式 | 适用场景 | 优点 | 缺点 |
|---------|---------|------|------|
| 统一配置（config.yaml） | 主评测流程 | 集中管理、易于维护 | 需要配置文件 |
| 独立配置（summary_generator.py） | 独立功能模块 | 模块独立、可覆盖 | 配置分散 |

### 6.2 关键设计模式

1. **工厂模式**：`ModelClientFactory` 统一创建客户端
2. **依赖注入**：通过参数注入 API KEY，而非硬编码
3. **模板方法模式**：`BaseModelClient` 定义统一接口
4. **策略模式**：不同 provider 使用不同的客户端实现

### 6.3 改进建议

1. ✅ **已完成**：统一配置管理、Git 忽略敏感文件
2. ⚠️ **建议改进**：移除代码中的硬编码 API KEY
3. ⚠️ **建议改进**：支持环境变量配置
4. ⚠️ **建议改进**：添加配置验证和错误提示

---

**文档生成时间**：2026-02-03  
**项目路径**：`d:\Code\python-workspace\pe评测\`
