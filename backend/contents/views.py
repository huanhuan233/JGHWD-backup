# contents/views.py
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from rest_framework.decorators import api_view,authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from outlines.models import Outline
from django.shortcuts import get_object_or_404
import json
import os
from django.conf import settings
from utils.writer_utils import build_prompt
from utils.content_utils import build_content_prompt
from .ai_model import call_siliconflow_model, query_dify_knowledge, query_fastGpt_knowledge
from .export import DocGenerator
from .config import MODEL_CHOICES
import copy

@api_view(['GET'])
def list_models_for_content(request):
    return JsonResponse({'success': True, 'models': MODEL_CHOICES})

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def list_articles(request):
    articles = Outline.objects.filter(user=request.user).order_by('-updated_at')
    result = []
    for article in articles:
        if article.structure is None or not article.structure:
            continue
            
        structure = []
        for i, item in enumerate(article.structure):
            structure.append({
                "id": item.get("id", f"s{i}"),
                "title": item.get("title", ""),
                "outline": item.get("outline", ""),
                "content": item.get("content", "")
            })
        
        result.append({
            "id": article.id,
            "title": article.title,
            "structure": structure,
            "title_setting": article.title_setting
        })
    
    return Response(result)

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def delete_content(request, article_id):
    # 根据ID查询要删除的文章
    article = Outline.objects.get(id=article_id)
    if article.original_structure is None:
        article.original_structure = article.structure
    article.structure = []
    article.save()
    return Response(status=status.HTTP_204_NO_CONTENT)
    
@api_view(['DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def delete_article(request, article_id):
    try:
        # 根据ID查询要删除的文章
        article = Outline.objects.get(id=article_id)
    except Outline.DoesNotExist:
        # 如果文章不存在，返回404状态码
        return Response(
            {"error": "文章不存在"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # 执行删除操作
    article.delete()
    
    # 返回成功响应（204状态码表示无内容，符合RESTful规范）
    return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['PATCH'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def update_section_content(request, outline_id, section_id):
    outline = get_object_or_404(Outline, id=outline_id)
    data = request.data
    new_content = data.get("content")

    if new_content is None:
        return Response({"error": "缺少 content 字段"}, status=400)

    updated = False
    for i, section in enumerate(outline.structure):
        sid = section.get("id", f"s{i}")
        if sid == section_id:
            outline.structure[i]["content"] = new_content
            updated = True
            break

    if not updated:
        return Response({"error": f"未找到 ID 为 {section_id} 的段落"}, status=404)

    outline.save()
    return Response({"success": True})

@csrf_exempt
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def generate_content(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': '仅支持 POST 请求'}, status=405)

    try:
        data = json.loads(request.body)
        outline_id = data.get('outline_id')  # 🔁 新增字段，前端传入大纲 ID
        model = data.get('model')
        article_title = data.get('article_title') or '未命名文章'
        section_title = data.get('section_title')
        section_outline = data.get('section_outline') or ''
        custom_prompt = data.get('custom_prompt') or ''
        knowledge_name = data.get('knowledge_config_id')
        use_kb = data.get('use_kb', False)
        use_hw = data.get("use_hw", False)
        hwKnowledge = data.get("hw_knowledge")
        # ✅ 自动备份结构：仅首次生成时复制结构
        if outline_id:
            outline = Outline.objects.get(id=outline_id)
            if outline.original_structure is None:
                outline.original_structure = outline.structure
                outline.save()
        #知识库查询
        kb_text = ''
        if use_kb and knowledge_name:
            config = load_knowledge_config(knowledge_name)
            if config and config.get('type') == 'dify':
                kb_text = query_dify_knowledge(api_key=config['api_key'], query=section_title)
            if config and config.get("type") == "FastGpt":
                kb_text = query_fastGpt_knowledge(api_key=config["api_key"], query=section_title)
        hw_text = ""
        if use_hw and hwKnowledge:
            config = load_knowledge_config(hwKnowledge)
            if config and config.get("type") == "FastGpt":
                hw_text = query_fastGpt_knowledge(api_key=config["api_key"], query=section_title)
            if config and config.get('type') == 'dify':
                hw_text = query_dify_knowledge(api_key=config['api_key'], query=section_title)
        #正文Promot
        final_prompt = build_prompt(article_title, section_title, section_outline + "\n" + kb_text + "\n" + custom_prompt + "\n" + hw_text)
        print("📨 正文生成 prompt：", final_prompt)

        content_lines = call_siliconflow_model(model, final_prompt)
        full_content = "\n".join(content_lines)

        return JsonResponse({
            'success': True,
            'content': full_content
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
@csrf_exempt
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def parse_export(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': '仅支持 POST 请求'}, status=405)
    
    try:
        data = json.loads(request.body)
        font_name = data.get('font_name') or '宋体'
        font_size = int(data.get('font_size', 14))
        italic = bool(data.get('italic', False))
        bold = bool(data.get('bold', False))
        table_style = data.get('table_style') or 'default'
        header = data.get('header')
        content_lines = data.get('content_lines')
        line_spacing = data.get('line_spacing')
        title_setting = data.get('title_setting')
        file_type = data.get('file_type', 'docx').lower()

        # 验证文件类型
        if file_type not in ['docx', 'pdf']:
            return JsonResponse({'success': False, 'error': '不支持的文件类型'}, status=400)
        print("Received content_lines:", data.get('content_lines'))
        full_content = content_lines
        # 创建文档生成器
        generator = DocGenerator(content_format=file_type)
        # 设置表格样式
        generator.set_table_style(table_style)
        # 添加内容
        print("开始加载Markdown内容...")
        generator.load_markdown(full_content)
        print("Markdown加载完成")
        
        # 添加标头 
        if header:
            generator.set_header_by_frontend_param(frontend_param=header)
    
        # 设置样式
        print("开始设置文本样式...")
        generator.set_text_style(
            font_name=font_name, 
            font_size=font_size, 
            bold=bold, 
            italic=italic
        )
        # 设置行间距
        if line_spacing:
            line_spacing_type = line_spacing.get('type')
            line_spacing_value = line_spacing.get('value') or ''
            try:
                int_value = int(line_spacing_value)
                generator.set_line_spacing(line_spacing_type, int_value)
            except ValueError:
                generator.set_line_spacing(line_spacing_type, 0)

        all_headings = generator.get_all_heading();
        print("获取到所有一级标题：", all_headings)
        generator.match_headings(title_setting, all_headings)    
        print("开始保存文档...")    
        return generator.save()
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': '无效的JSON数据'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

    

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def auto_generate_and_save(request):
    try:
        data = request.data
        outline_id = data.get("outline_id")
        section_id = data.get("section_id")
        article_title = data.get("article_title")
        section_title = data.get("section_title")
        section_outline = data.get("section_outline", "")
        custom_prompt = data.get("custom_prompt", "")
        model = data.get("model")
        min_words = int(data.get("minWords", 1000))
        use_kb = data.get("use_kb", False)
        use_hw = data.get("use_hw", False)
        knowledge_name = data.get("knowledge_config_id")
        hwKnowledge = data.get("hw_knowledge")

        print(f"📝 接收到生成请求: 文章《{article_title}》, 段落《{section_title}》")
        print(f"📄 段落大纲: {section_outline}")

        if not all([outline_id, section_id, article_title, section_title, model]):
            missing = [k for k in ["outline_id", "section_id", "article_title", "section_title", "model"] if not data.get(k)]
            return Response({"success": False, "error": f"缺少必要字段: {', '.join(missing)}"}, status=400)

        kb_text = ""
        if use_kb and knowledge_name:
            config = load_knowledge_config(knowledge_name)
            if config and config.get("type") == "dify":
                kb_text = query_dify_knowledge(api_key=config["api_key"], query=section_title)
            if config and config.get("type") == "FastGpt":
                kb_text = query_fastGpt_knowledge(api_key=config["api_key"], query=section_title)
        hw_text = ""
        if use_hw and hwKnowledge:
            config = load_knowledge_config(hwKnowledge)
            if config and config.get("type") == "FastGpt":
                hw_text = query_fastGpt_knowledge(api_key=config["api_key"], query=section_title)
            if config and config.get("type") == "dify":
                hw_text = query_dify_knowledge(api_key=config["api_key"], query=section_title)

        outline = get_object_or_404(Outline, id=outline_id)
        prev_content = ""
        for i, section in enumerate(outline.structure):
            sid = section.get("id", f"s{i}")
            if sid == section_id:
                if i != 0:
                    prev_content = outline.structure[i - 1]["content"]

        final_prompt = build_content_prompt(article_title, section_outline,"",hw_text,min_words,prev_content,custom_prompt)

        print("📨 自动写入生成 prompt：", final_prompt)

        content_lines = call_siliconflow_model(model, final_prompt)
        full_content = "\n".join(content_lines)

        outline = get_object_or_404(Outline, id=outline_id)

        # ✅ 添加结构备份：只备份一次
        if outline.original_structure is None:
            outline.original_structure = copy.deepcopy(outline.structure)  # 深拷贝，避免关联
            
        # 如果structure为空，先从original_structure复制内容
        if not outline.structure and outline.original_structure:
            outline.structure = copy.deepcopy(outline.original_structure)
            print("🔄 已从original_structure复制内容到structure")

        # 更新正文内容
        updated = False
        for i, section in enumerate(outline.structure):
            print("🔁 正在更新段落内容:", outline.structure)
            sid = section.get("id", f"s{i}")
            if sid == section_id:
                outline.structure[i]["content"] = full_content
                updated = True
                break

        if updated:
            outline.save()

        return Response({"success": True, "content": full_content})
    except Exception as e:
        import traceback
        print("❌ 生成内容时出错:", str(e))
        print(traceback.format_exc())
        return Response({"success": False, "error": str(e)}, status=500)

def load_knowledge_config(knowledge_name: str):
    folder = os.path.join(settings.BASE_DIR, 'template_storage', 'knowledge_configs')
    for filename in os.listdir(folder):
        if filename.startswith(knowledge_name) and filename.endswith('.json'):
            filepath = os.path.join(folder, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
    return None
