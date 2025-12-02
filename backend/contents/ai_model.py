import requests
import os
import time
from .config import MODEL_CHOICES
from typing import List

def call_siliconflow_model(model: str, prompt: str, max_retries=3, timeout=200) -> List[str]:
    """
    调用硅基流动模型API，支持重试机制
    
    Args:
        model: 模型名称
        prompt: 提示词
        max_retries: 最大重试次数
        timeout: 超时时间（秒）
        
    Returns:
        生成的文本行列表
    """
    if model not in MODEL_CHOICES:
        raise ValueError(f"非法模型名: {model}，请从配置中选择")

    url = "https://api.siliconflow.cn/v1/chat/completions"

    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "stream": False,
        "max_tokens": 2048,  # 增加 token 数量以生成更长的内容
        "enable_thinking": False,
        "thinking_budget": 4096,
        "min_p": 0.05,
        "stop": None,
        "temperature": 0.7,
        "top_p": 0.7,
        "top_k": 50,
        "frequency_penalty": 0.5,
        "n": 1,
        "response_format": {"type": "text"},
        "tools": [
            {
                "type": "function",
                "function": {
                    "description": "<string>",
                    "name": "<string>",
                    "parameters": {},
                    "strict": False
                }
            }
        ]
    }

    headers = {
        "Authorization": f"Bearer {get_siliconflow_api_key()}",
        "Content-Type": "application/json"
    }

    retry_count = 0
    last_error = None
    
    while retry_count < max_retries:
        try:
            print(f"📡 正在调用硅基流动API (尝试 {retry_count + 1}/{max_retries})...")
            response = requests.post(url, json=payload, headers=headers, timeout=timeout)
            response.raise_for_status()
            data = response.json()
            text = data["choices"][0]["message"]["content"]
            outline = [line.strip() for line in text.splitlines() if line.strip()]
            print(f"✅ API调用成功，生成了 {len(outline)} 行内容")
            return outline
        except requests.exceptions.Timeout:
            retry_count += 1
            last_error = f"API请求超时 (timeout={timeout}s)"
            print(f"⚠️ {last_error}，正在重试 ({retry_count}/{max_retries})...")
            time.sleep(2)  # 等待2秒后重试
        except requests.exceptions.RequestException as e:
            retry_count += 1
            last_error = f"请求异常: {e}"
            print(f"⚠️ {last_error}，正在重试 ({retry_count}/{max_retries})...")
            time.sleep(2)  # 等待2秒后重试
    
    # 所有重试都失败
    raise RuntimeError(f"调用硅基流动API失败: {last_error}")

def get_siliconflow_api_key():
    key = os.getenv("SILICONFLOW_API_KEY")
    if not key:
        raise ValueError("未设置 SILICONFLOW_API_KEY 环境变量，请在 .env 文件中添加")
    return key

def query_dify_knowledge(api_key: str, query: str) -> str:
    url = "http://localhost:8080/v1/completion-messages"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "inputs": {"query": query},
        "response_mode": "blocking",
        "user": "abc-123"
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=200)
        response.raise_for_status()
        data = response.json()
        answer = data.get("answer", "")
        resources = data.get("metadata", {}).get("retriever_resources", [])
        top_chunks = "\n".join([r.get("content", "") for r in resources[:2]])
        return f"{answer}\n\n引用内容：\n{top_chunks}"
    except Exception as e:
        print("❌ Dify 知识库调用失败：", e)
        return ""
def query_fastGpt_knowledge(api_key: str, query: str) -> str:
    url = "http://localhost:3000/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
       "stream": False,
       "detail": False, 
       "messages": [
            {
                "content":query,
                "role":"user"
            }
        ] ,
    }
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=200)
        response.raise_for_status()
        data = response.json()
        answer = data['choices'][0]['message']['content']
      
        return f"{answer}\n\n"
    except Exception as e:
        print("❌ fastGpt 知识库调用失败：", e)
        return ""