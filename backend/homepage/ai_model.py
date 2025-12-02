import requests
import os
import time
from .config import MODEL_CHOICES
from typing import List

def call_siliconflow_model(model: str, prompt: str) -> List[str]:
    if model not in MODEL_CHOICES:
        raise ValueError(f"非法模型名: {model}，请从配置中选择")

    url = "https://api.siliconflow.cn/v1/chat/completions"
    
    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "stream": False,
        "max_tokens": 512,
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

    # 重试配置
    max_retries = 3
    base_timeout = 200  # 基础超时时间
    last_exception = None
    
    for attempt in range(max_retries):
        try:
            # 动态调整超时时间，每次重试增加等待时间
            current_timeout = base_timeout + (attempt * 10)  # 每次重试增加10秒
            wait_time = attempt * 2  # 重试等待时间，指数退避
            
            if attempt > 0:
                print(f"第 {attempt} 次重试，等待 {wait_time} 秒后重新调用...")
                time.sleep(wait_time)
            
            response = requests.post(url, json=payload, headers=headers, timeout=current_timeout)
            response.raise_for_status()
            data = response.json()
            text = data["choices"][0]["message"]["content"]
            outline = [line.strip() for line in text.splitlines() if line.strip()]
            
            # 如果成功，打印重试信息（如果有重试的话）
            if attempt > 0:
                print(f"第 {attempt + 1} 次调用成功")
            return outline
            
        except requests.exceptions.Timeout:
            last_exception = f"请求超时（{current_timeout}秒）"
            print(f"第 {attempt + 1} 次调用超时: {last_exception}")
            
        except requests.exceptions.RequestException as e:
            last_exception = e
            print(f"第 {attempt + 1} 次调用失败: {e}")
            
        except (KeyError, IndexError) as e:
            last_exception = f"响应解析错误: {e}"
            print(f"第 {attempt + 1} 次调用响应解析失败: {e}")
            # 对于响应解析错误，不重试
            break

    # 所有重试都失败后抛出异常
    raise RuntimeError(f"调用硅基流动API失败，共尝试{max_retries}次。最后错误: {last_exception}")

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
    url = "http://192.168.0.97:3000/api/v1/chat/completions"
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