from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import json
import os
from .ai_model import call_siliconflow_model, query_dify_knowledge, query_fastGpt_knowledge
from .config import MODEL_CHOICES
from outlines.models import Outline  # ✅ 用于保存结构
from templates_config.views import list_templates
from utils.writer_utils import build_prompt
from rest_framework.decorators import api_view,authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

def homepage_view(request):
    return HttpResponse("这是 Homepage 根路径，欢迎访问！")


def list_models(request):
    return JsonResponse({'success': True, 'models': MODEL_CHOICES})


@csrf_exempt

def generate_outline(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': '仅支持 POST 请求'}, status=405)

    try:
        data = json.loads(request.body)
        title = data.get('title')
        template = data.get('template')
        model = data.get('model')
        prompt = data.get('prompt') or f"请根据模板 {template}，为《{title}》生成结构清晰的大纲"

        if model not in MODEL_CHOICES:
            return JsonResponse({'success': False, 'error': f'非法模型名称：{model}'}, status=400)

        outline = call_siliconflow_model(model, prompt)
        return JsonResponse({'success': True, 'outline': outline})

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


def load_knowledge_config(knowledge_name: str):
    folder = os.path.join(settings.BASE_DIR, 'template_storage', 'knowledge_configs')
    print("📂 当前配置文件夹内容：", os.listdir(folder))

    for filename in os.listdir(folder):
        if filename.startswith(knowledge_name) and filename.endswith('.json'):
            filepath = os.path.join(folder, filename)
            print("✅ 找到配置文件：", filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)

    print("⚠️ 未找到匹配知识库配置文件:", knowledge_name)
    return None


@csrf_exempt
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def generate_outline_items(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': '仅支持 POST 请求'}, status=405)

    try:
        print("📥 收到生成请求！")
        print("🧾 原始请求体:", request.body.decode('utf-8'))

        data = json.loads(request.body)
        model = data.get('model')
        prompt_base = data.get('prompt', '')
        titles = data.get('titles')
        knowledge = data.get('knowledge')
        use_kb = data.get('use_kb', False)
        use_hw = data.get("use_hw", False)
        hwKnowledge = data.get("hw_knowledge")
        title_setting = data.get("title_setting")
        article_title = data.get('article_title') or '未命名文章'

        if model not in MODEL_CHOICES:
            return JsonResponse({'success': False, 'error': f'非法模型名称：{model}'}, status=400)

        # 初始化输出内容
        sections = []
        debug_info = {"prompts": [], "knowledge_snippets": []}

        # 加载知识库配置
        config = None
        if use_kb and knowledge:
            config = load_knowledge_config(knowledge)
            if not config:
                return JsonResponse({'success': False, 'error': f'未找到知识库配置文件: {knowledge}'}, status=404)
            print(f"🧠 使用知识库: {knowledge}, 类型: {config.get('type')}")

        # 逐段处理标题
        prev_content = ''
        for section_title in titles:
            # 检索知识库内容
            kb_text = ""
            if use_kb and config :
                if config.get("type") == "dify":
                    kb_text = query_dify_knowledge(api_key=config["api_key"], query=section_title)
                    debug_info["knowledge_snippets"].append({"title": section_title, "kb": kb_text})
                if config.get("type") == "FastGpt":
                    kb_text = query_fastGpt_knowledge(api_key=config["api_key"], query=section_title)
                    debug_info["knowledge_snippets"].append({"title": section_title, "kb": kb_text})
            else:
                debug_info["knowledge_snippets"].append({"title": section_title, "kb": "未启用或未配置"})
            hw_text = ""
            if use_hw and hwKnowledge:
                config = load_knowledge_config(hwKnowledge)
                if config and config.get("type") == "dify":
                    hw_text = query_dify_knowledge(api_key=config["api_key"], query=section_title)
                if config and config.get("type") == "FastGpt":
                    hw_text = query_fastGpt_knowledge(api_key=config["api_key"], query=section_title)
            # ✅ 构造 prompt（调用 utils 中封装好的函数）
            prompt = build_prompt(article_title, section_title, kb_text,hw_text,prev_content)
           
            debug_info["prompts"].append({"title": section_title, "prompt": prompt})

            print("\n==============================")
            print(f"🤖 正在调用模型 [{model}]，标题: {section_title}")
            print("📨 最终 prompt：", prompt)

            content_lines = call_siliconflow_model(model, prompt)
            prev_content = content_lines
            print("📩 模型返回内容:", content_lines)

            sections.append({
                "title": section_title,
                "content": "\n".join(content_lines)
            })

        # ✅ 保存为 Outline 记录
        outline_obj = Outline.objects.create(
            title=article_title,
            structure=sections,
            model_name=model,
            title_setting=title_setting,
            user=request.user
        )

        return JsonResponse({
            'success': True,
            'outline': {
                "id": outline_obj.id,
                "title": article_title,
                "structure": sections,
                "title_setting": title_setting

            },
            'debug': debug_info
        })

    except Exception as e:
        print("❌ 出现错误:", e)
        return JsonResponse({'success': False, 'error': str(e)}, status=500)