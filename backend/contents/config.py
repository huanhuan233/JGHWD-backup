# homepage/config.py

# 模型列表（直接从你提供的部分整理）
MODEL_CHOICES = [
    "Qwen/Qwen3-30B-A3B",
    "Qwen/Qwen3-32B",
    "Qwen/Qwen3-14B",
    "Qwen/Qwen3-8B",
    "Qwen/Qwen3-235B-A22B",
    "THUDM/GLM-Z1-32B-0414",
    "THUDM/GLM-4-32B-0414",
    "THUDM/GLM-Z1-Rumination-32B-0414",
    "THUDM/GLM-4-9B-0414",
    "Qwen/QwQ-32B",
    "Pro/deepseek-ai/DeepSeek-R1",
    "Pro/deepseek-ai/DeepSeek-V3",
    "deepseek-ai/DeepSeek-R1",
    "deepseek-ai/DeepSeek-V3",
    "deepseek-ai/DeepSeek-R1-Distill-Qwen-32B",
    "deepseek-ai/DeepSeek-R1-Distill-Qwen-14B",
    "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B",
    "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B",
    "Pro/deepseek-ai/DeepSeek-R1-Distill-Qwen-7B",
    "Pro/deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B",
    "deepseek-ai/DeepSeek-V2.5",
    "Qwen/Qwen2.5-72B-Instruct-128K",
    "Qwen/Qwen2.5-72B-Instruct",
    "Qwen/Qwen2.5-32B-Instruct",
    "Qwen/Qwen2.5-14B-Instruct",
    "Qwen/Qwen2.5-7B-Instruct",
    "Qwen/Qwen2.5-Coder-32B-Instruct",
    "Qwen/Qwen2.5-Coder-7B-Instruct",
    "Qwen/Qwen2-7B-Instruct",
    "Qwen/Qwen2-1.5B-Instruct",
    "Qwen/QwQ-32B-Preview",
    "TeleAI/TeleChat2",
    "THUDM/glm-4-9b-chat",
    "Vendor-A/Qwen/Qwen2.5-72B-Instruct",
    "internlm/internlm2_5-7b-chat",
    "internlm/internlm2_5-20b-chat",
    "Pro/Qwen/Qwen2.5-7B-Instruct",
    "Pro/Qwen/Qwen2-7B-Instruct",
    "Pro/Qwen/Qwen2-1.5B-Instruct",
    "Pro/THUDM/chatglm3-6b",
    "Pro/THUDM/glm-4-9b-cha",
]

# 转换成适合前端下拉框格式的列表（label 你可以自己改成更友好名字）
MODEL_OPTIONS = [
    {"value": model_name, "label": model_name} for model_name in MODEL_CHOICES
]
