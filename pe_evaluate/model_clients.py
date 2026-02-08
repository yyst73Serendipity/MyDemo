"""
AI模型API客户端封装
支持多个AI服务提供商的统一调用接口
"""

import json
import time
from typing import Dict, Any, Optional
import requests
from abc import ABC, abstractmethod

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class BaseModelClient(ABC):
    """模型客户端基类"""
    
    def __init__(self, config: Dict[str, Any]):
        self.name = config['name']
        self.model_id = config['model_id']
        self.api_key = config['api_key']
        self.base_url = config['base_url']
        self.params = config.get('params', {})
    
    @abstractmethod
    def chat(self, system_prompt: str, user_message: str) -> Dict[str, Any]:
        """发送聊天请求并返回响应"""
        pass
    
    def _handle_error(self, error: Exception, attempt: int) -> None:
        """处理API调用错误"""
        print(f"  ⚠️  模型 {self.name} 第 {attempt} 次调用失败: {str(error)}")


class OpenAIClient(BaseModelClient):
    """OpenAI GPT 客户端"""
    
    def chat(self, system_prompt: str, user_message: str) -> Dict[str, Any]:
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model_id,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            "temperature": self.params.get('temperature', 0.7),
            "max_tokens": self.params.get('max_tokens', 2000)
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        return {
            "content": result['choices'][0]['message']['content'],
            "raw": result,
            "usage": result.get('usage', {})
        }


class GoogleGeminiClient(BaseModelClient):
    """Google Gemini 客户端"""
    
    def chat(self, system_prompt: str, user_message: str) -> Dict[str, Any]:
        url = f"{self.base_url}/models/{self.model_id}:generateContent?key={self.api_key}"
        headers = {
            "Content-Type": "application/json"
        }
        
        # Gemini的system instruction需要特殊处理
        full_prompt = f"{system_prompt}\n\n用户输入：{user_message}"
        
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": full_prompt}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": self.params.get('temperature', 0.7),
                "maxOutputTokens": self.params.get('max_output_tokens', 2000)
            }
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        content = result['candidates'][0]['content']['parts'][0]['text']
        
        return {
            "content": content,
            "raw": result,
            "usage": result.get('usageMetadata', {})
        }


class DeepSeekClient(BaseModelClient):
    """DeepSeek 客户端"""
    
    def chat(self, system_prompt: str, user_message: str) -> Dict[str, Any]:
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model_id,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            "temperature": self.params.get('temperature', 0.7),
            "max_tokens": self.params.get('max_tokens', 2000)
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        return {
            "content": result['choices'][0]['message']['content'],
            "raw": result,
            "usage": result.get('usage', {})
        }


class QwenClient(BaseModelClient):
    """Qwen (通义千问) 客户端"""
    
    def chat(self, system_prompt: str, user_message: str) -> Dict[str, Any]:
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model_id,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            "temperature": self.params.get('temperature', 0.7),
            "max_tokens": self.params.get('max_tokens', 2000)
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        return {
            "content": result['choices'][0]['message']['content'],
            "raw": result,
            "usage": result.get('usage', {})
        }


class MoonshotClient(BaseModelClient):
    """Moonshot (Kimi) 客户端"""
    
    def chat(self, system_prompt: str, user_message: str) -> Dict[str, Any]:
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model_id,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            "temperature": self.params.get('temperature', 0.7),
            "max_tokens": self.params.get('max_tokens', 2000)
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        return {
            "content": result['choices'][0]['message']['content'],
            "raw": result,
            "usage": result.get('usage', {})
        }


class DMXAPIClient(BaseModelClient):
    """DMXAPI 聚合平台客户端（使用 OpenAI SDK）"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
        if not OPENAI_AVAILABLE:
            raise ImportError(
                "使用 DMXAPI 需要安装 OpenAI SDK。请运行: pip install openai"
            )
        
        # 初始化 OpenAI 客户端
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
    
    def chat(self, system_prompt: str, user_message: str) -> Dict[str, Any]:
        """使用 OpenAI SDK 调用 DMXAPI"""
        try:
            response = self.client.chat.completions.create(
                model=self.model_id,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=self.params.get('temperature', 0.7),
                max_tokens=self.params.get('max_tokens', 4000)
            )
            
            # 将 OpenAI 响应对象转换为字典格式
            return {
                "content": response.choices[0].message.content,
                "raw": response.model_dump(),  # 转换为字典
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                    "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                    "total_tokens": response.usage.total_tokens if response.usage else 0
                }
            }
        except Exception as e:
            # 捕获并重新抛出异常，保持与其他客户端一致
            raise Exception(f"DMXAPI 调用失败: {str(e)}")


class ModelClientFactory:
    """模型客户端工厂类"""
    
    _client_map = {
        'openai': OpenAIClient,
        'google': GoogleGeminiClient,
        'deepseek': DeepSeekClient,
        'qwen': QwenClient,
        'moonshot': MoonshotClient,
        'dmxapi': DMXAPIClient
    }
    
    @classmethod
    def create_client(cls, config: Dict[str, Any]) -> BaseModelClient:
        """根据配置创建对应的客户端"""
        provider = config.get('provider', '').lower()
        
        if provider not in cls._client_map:
            raise ValueError(f"不支持的服务提供商: {provider}")
        
        client_class = cls._client_map[provider]
        return client_class(config)
    
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
                    msg = f"✅ 已加载模型: {config['name']}"
                    if logger:
                        logger.print(msg)
                    else:
                        print(msg)
                except Exception as e:
                    msg = f"❌ 加载模型 {config['name']} 失败: {str(e)}"
                    if logger:
                        logger.print(msg)
                    else:
                        print(msg)
        
        return clients


def test_client(client: BaseModelClient, system_prompt: str, test_message: str, logger=None) -> Optional[Dict[str, Any]]:
    """测试单个客户端，包含重试逻辑"""
    max_retries = 3
    
    def log(msg):
        """统一的日志输出"""
        if logger:
            logger.print(msg)
        else:
            print(msg)
    
    for attempt in range(1, max_retries + 1):
        try:
            log(f"  🔄 尝试第 {attempt} 次调用...")
            result = client.chat(system_prompt, test_message)
            log(f"  ✅ 调用成功")
            return result
        except Exception as e:
            error_msg = f"  ⚠️  模型 {client.name} 第 {attempt} 次调用失败: {str(e)}"
            log(error_msg)
            if attempt < max_retries:
                wait_time = 2 ** attempt  # 指数退避
                log(f"  ⏳ 等待 {wait_time} 秒后重试...")
                time.sleep(wait_time)
            else:
                log(f"  ❌ 已达到最大重试次数，跳过此模型")
                return None
    
    return None

