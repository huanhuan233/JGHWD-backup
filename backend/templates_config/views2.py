from django.shortcuts import render
from .models import Template
from rest_framework.decorators import api_view,authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
# Create your views here.
import os
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.db.models import Q
from .template import extract_word_titles, allowed_file, extract_pdf_titles, build_title_hierarchy
import uuid

@csrf_exempt
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def save_template(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': '只允许POST请求'}, status=405)
    
    try:
        data = json.loads(request.body)
        template_id = data.get('id')
        template_name = data.get('name')
        structure = data.get('structure', [])
        is_public = data.get('is_public', False)
        user = request.user

        if not template_id:
            return JsonResponse({'success': False, 'error': '缺少模板ID'}, status=400)
        if not template_name:
            return JsonResponse({'success': False, 'error': '缺少模板名称'}, status=400)

        template, created = Template.objects.update_or_create(
            id=template_id,
            user=user,
            defaults={'name': template_name, 'structure': structure}
        )
        message = '模板创建成功' if created else '模板更新成功'
        return JsonResponse({
            'success': True, 
            'created': created,
            'type': 'personal',
            'message': message
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'JSON数据格式错误'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'服务器错误: {str(e)}'}, status=500)

@csrf_exempt
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def extract_titles_view(request):
    if request.method == 'POST':
        # 检查是否有文件上传
        if 'file' not in request.FILES:
            return JsonResponse({"error": "未上传文件"}, status=400)
        
        file = request.FILES['file']
        filename = file.name
        # 检查文件类型
        if not allowed_file(filename):
            return JsonResponse({"error": "仅支持docx、pdf和txt格式"}, status=400)
        
        try:
            user = request.user
            # 读取文件内容（内存中处理）
            file_content = file.read()
            
            # 1. 处理 .txt 文件（从JSON获取id和name）
            if filename.lower().endswith('.txt'):
                try:
                    # 解析请求体中的JSON数据
                    data = json.loads(request.body)
                    template_id = data.get('id')
                    template_name = data.get('name')
                    structure = data.get('structure', [])
                    is_public = data.get('is_public', False)

                    # 校验必填字段
                    if not template_id:
                        return JsonResponse({'success': False, 'error': '缺少模板ID'}, status=400)
                    if not template_name:
                        return JsonResponse({'success': False, 'error': '缺少模板名称'}, status=400)

                    # 创建或更新模板
                    template, created = Template.objects.update_or_create(
                        id=template_id,
                        user=user,
                        defaults={'name': template_name, 'structure': structure, 'is_public': is_public}
                    )
                    message = '模板创建成功' if created else '模板更新成功'
                    return JsonResponse({
                        'success': True, 
                        'created': created,
                        'type': 'personal',
                        'message': message
                    })
                    
                except json.JSONDecodeError:
                    return JsonResponse({'success': False, 'error': 'JSON数据格式错误'}, status=400)
            
            # 2. 处理 .docx 文件（自动生成id和name）
            elif filename.lower().endswith('.docx'):
                # 提取标题结构
                titles = extract_word_titles(file_content)
                structure = build_title_hierarchy(titles)
                
                # 自动生成id（如果是新模板）和name
                template_id = request.POST.get('id')  # 允许前端传递id（更新场景）
                # 如果前端没传id，生成新的唯一ID
                if not template_id:
                    template_id = str(uuid.uuid4())  # 生成UUID作为唯一标识
                # 模板名称默认使用文件名（不含后缀）
                template_name = request.POST.get('name', os.path.splitext(filename)[0])

                # 创建或更新模板
                template, created = Template.objects.update_or_create(
                    id=template_id,
                    user=user,
                    defaults={'name': template_name, 'structure': structure}
                )
                message = '模板创建成功' if created else '模板更新成功'
                return JsonResponse({
                    'success': True, 
                    'created': created,
                    'type': 'personal',
                    'message': message,
                    'id': template_id  # 返回生成的ID给前端
                })
            
            # 3. 处理 .pdf 文件（逻辑同docx）
            elif filename.lower().endswith('.pdf'):
                titles = extract_pdf_titles(file_content)
                structure = build_title_hierarchy(titles)
                
                # 自动生成id和name
                template_id = request.POST.get('id')
                if not template_id:
                    template_id = str(uuid.uuid4())
                template_name = request.POST.get('name', os.path.splitext(filename)[0])

                template, created = Template.objects.update_or_create(
                    id=template_id,
                    user=user,
                    defaults={'name': template_name, 'structure': structure}
                )
                message = '模板创建成功' if created else '模板更新成功'
                return JsonResponse({
                    'success': True, 
                    'created': created,
                    'type': 'personal',
                    'message': message,
                    'id': template_id
                })
        
        except Exception as e:
            return JsonResponse({'success': False, 'error': f'服务器错误: {str(e)}'}, status=500)
    
    # 非POST请求
    return JsonResponse({"error": "仅支持POST请求"}, status=405)

#每次左侧载入本地模板
@csrf_exempt
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def list_templates(request):
   
    try:
        templates = Template.objects.filter(
             Q(user=request.user)
        )
        data = [{
            'id': t.id,
            'name': t.name,
            'structure': t.structure,
            'count':count_title_cycles(t.structure)
        } for t in templates]
        return JsonResponse({'success': True, 'templates': data})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

def count_title_cycles(structure):
    total_count = 0
    if not structure:  # 判空：如果structure是None或空列表
        return total_count
    
    for item in structure:
        total_count += 1  # 计数当前标题
        
        # 递归处理子标题（children本身就是下一级的structure列表）
        children = item.get('children', [])  # 用get()避免键不存在报错
        if children:
            total_count += count_title_cycles(children)  # 直接传入子列表
    
    return total_count

@csrf_exempt
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def delete_template(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Only POST method allowed'}, status=405)
    try:
        data = json.loads(request.body)
        template_id = data.get('id')
        if not template_id:
            return JsonResponse({'success': False, 'error': 'Missing id'}, status=400)

        deleted, _ = Template.objects.filter(id=template_id).delete()
        if deleted == 0:
            return JsonResponse({'success': False, 'error': 'Template not found'}, status=404)

        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@csrf_exempt
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def default_template(request):
    try:
        user = request.user
        
        default_templates_data = [
            # 模板一：立项论证报告
            {
                "id": f"default_1_{user.id}",  # 用用户ID确保ID唯一
                "name": "立项论证报告",
            "structure": [
                {
                    "id": "1760509574830",
                    "title": "一、背景需求",
                    "font": "宋体",
                    "size": 14,
                    "color": "rgb(0,0,0)",
                    "bold": True,
                    "italic": False,
                    "id_level": 1,
                    "children": [
                        {
                            "id": "1760603128225",
                            "title": "（一）项目内涵",
                            "font": "宋体",
                            "size": 14,
                            "color": "rgb(0,0,0)",
                            "bold": True,
                            "italic": False,
                            "id_level": 2,
                            "children": []
                        },
                        {
                            "id": "1760603168497",
                            "title": "（二）市场/武器装备需求",
                            "font": "宋体",
                            "size": 14,
                            "color": "rgb(0,0,0)",
                            "bold": True,
                            "italic": False,
                            "id_level": 2,
                            "children": []
                        }
                    ]
                },
                {
                    "id": "1760509577605",
                    "title": "二、国内外同类技术或产品发展现状分析",
                    "font": "宋体",
                    "size": 14,
                    "color": "rgb(0,0,0)",
                    "bold": True,
                    "italic": False,
                    "id_level": 1,
                    "children": []
                },
                {
                    "id": "1760603192267",
                    "title": "三、主要研究内容和预期达到的目标",
                    "font": "宋体",
                    "size": 14,
                    "color": "rgb(0,0,0)",
                    "bold": True,
                    "italic": False,
                    "id_level": 1,
                    "children": [
                        {
                            "id": "1760603199535",
                            "title": "（一）预期达到的总目标",
                            "font": "宋体",
                            "size": 14,
                            "color": "rgb(0,0,0)",
                            "bold": True,
                            "italic": False,
                            "id_level": 2,
                            "children": []
                        },
                        {
                            "id": "1760603209267",
                            "title": "（二）研究内容",
                            "font": "宋体",
                            "size": 14,
                            "color": "rgb(0,0,0)",
                            "bold": True,
                            "italic": False,
                            "id_level": 2,
                            "children": []
                        },
                        {
                            "id": "1760603216749",
                            "title": "（三）技术指标",
                            "font": "宋体",
                            "size": 14,
                            "color": "rgb(0,0,0)",
                            "bold": True,
                            "italic": False,
                            "id_level": 2,
                            "children": []
                        },
                        {
                            "id": "1760603227425",
                            "title": "（四）关键技术",
                            "font": "宋体",
                            "size": 14,
                            "color": "rgb(0,0,0)",
                            "bold": True,
                            "italic": False,
                            "id_level": 2,
                            "children": []
                        },
                        {
                            "id": "1760603258347",
                            "title": "（五）成果形式",
                            "font": "宋体",
                            "size": 14,
                            "color": "rgb(0,0,0)",
                            "bold": True,
                            "italic": False,
                            "id_level": 2,
                            "children": []
                        }
                    ]
                },
                {
                    "id": "1760603267455",
                    "title": "四、研究途径",
                    "font": "宋体",
                    "size": 14,
                    "color": "rgb(0,0,0)",
                    "bold": True,
                    "italic": False,
                    "id_level": 1,
                    "children": []
                },
                {
                    "id": "1760603277101",
                    "title": "五、预期效益分析",
                    "font": "宋体",
                    "size": 14,
                    "color": "rgb(0,0,0)",
                    "bold": True,
                    "italic": False,
                    "id_level": 1,
                    "children": [
                        {
                            "id": "1760603285264",
                            "title": "（一）应用前景分析",
                            "font": "宋体",
                            "size": 14,
                            "color": "rgb(0,0,0)",
                            "bold": True,
                            "italic": False,
                            "id_level": 2,
                            "children": []
                        },
                        {
                            "id": "1760603294734",
                            "title": "（二）对技术发展的推动作用及经济效益",
                            "font": "宋体",
                            "size": 14,
                            "color": "rgb(0,0,0)",
                            "bold": True,
                            "italic": False,
                            "id_level": 2,
                            "children": []
                        }
                    ]
                },
                {
                    "id": "1760603307821",
                    "title": "六、研究进度及经费需求",
                    "font": "宋体",
                    "size": 14,
                    "color": "rgb(0,0,0)",
                    "bold": True,
                    "italic": False,
                    "id_level": 1,
                    "children": [
                        {
                            "id": "1760603319835",
                            "title": "（一）研究进度（表格）",
                            "font": "宋体",
                            "size": 14,
                            "color": "rgb(0,0,0)",
                            "bold": True,
                            "italic": False,
                            "id_level": 2,
                            "children": []
                        },
                        {
                            "id": "1760603330389",
                            "title": "（二）经费需求（表格）",
                            "font": "宋体",
                            "size": 14,
                            "color": "rgb(0,0,0)",
                            "bold": True,
                            "italic": False,
                            "id_level": 2,
                            "children": []
                        },
                        {
                            "id": "1760603336997",
                            "title": "（三）经费概算详细说明表",
                            "font": "宋体",
                            "size": 14,
                            "color": "rgb(0,0,0)",
                            "bold": True,
                            "italic": False,
                            "id_level": 2,
                            "children": []
                        }
                    ]
                },
                {
                    "id": "1760603348026",
                    "title": "七、保障条件分析（从人员、设备、技术等方面）",
                    "font": "宋体",
                    "size": 14,
                    "color": "rgb(0,0,0)",
                    "bold": True,
                    "italic": False,
                    "id_level": 1,
                    "children": [
                        {
                            "id": "1760603357129",
                            "title": "（一）现有条件",
                            "font": "宋体",
                            "size": 14,
                            "color": "rgb(0,0,0)",
                            "bold": True,
                            "italic": False,
                            "id_level": 2,
                            "children": []
                        },
                        {
                            "id": "1760603364867",
                            "title": "（二）需补充条件",
                            "font": "宋体",
                            "size": 14,
                            "color": "rgb(0,0,0)",
                            "bold": True,
                            "italic": False,
                            "id_level": 2,
                            "children": []
                        },
                        {
                            "id": "1760603370764",
                            "title": "（三）主要研究人员概况",
                            "font": "宋体",
                            "size": 14,
                            "color": "rgb(0,0,0)",
                            "bold": True,
                            "italic": False,
                            "id_level": 2,
                            "children": []
                        },
                        {
                            "id": "1760603386877",
                            "title": "（四）主要协作单位",
                            "font": "宋体",
                            "size": 14,
                            "color": "rgb(0,0,0)",
                            "bold": True,
                            "italic": False,
                            "id_level": 2,
                            "children": []
                        }
                    ]
                },
                {
                    "id": "1760603394993",
                    "title": "八、风险分析",
                    "font": "宋体",
                    "size": 14,
                    "color": "rgb(0,0,0)",
                    "bold": True,
                    "italic": False,
                    "id_level": 1,
                    "children": []
                },
                {
                    "id": "1760603403140",
                    "title": "九、现有类似技术和适用的法律法规要求",
                    "font": "宋体",
                    "size": 14,
                    "color": "rgb(0,0,0)",
                    "bold": True,
                    "italic": False,
                    "id_level": 1,
                    "children": []
                }
            ]
        },
            # 模板二：项目任务书
            {
                "id": f"default_2_{user.id}",
                "name": "项目任务书",
                "structure": [
                    {
                        "id": "1760603479630",
                        "title": "一、研究目标",
                        "font": "宋体",
                        "size": 14,
                        "color": "rgb(0,0,0)",
                        "bold": True,
                        "italic": False,
                        "id_level": 1,
                        "children": []
                    },
                    {
                        "id": "1760603489646",
                        "title": "二、主要研究内容",
                        "font": "宋体",
                        "size": 14,
                        "color": "rgb(0,0,0)",
                        "bold": True,
                        "italic": False,
                        "id_level": 1,
                        "children": []
                    },
                    {
                        "id": "1760603496063",
                        "title": "三、技术指标",
                        "font": "宋体",
                        "size": 14,
                        "color": "rgb(0,0,0)",
                        "bold": True,
                        "italic": False,
                        "id_level": 1,
                        "children": []
                    },
                    {
                        "id": "1760603501853",
                        "title": "四、成果形式",
                        "font": "宋体",
                        "size": 14,
                        "color": "rgb(0,0,0)",
                        "bold": True,
                        "italic": False,
                        "id_level": 1,
                        "children": []
                    }
                ]
            },
            # 模板三：研究工作大纲
            {
                "id": f"default_3_{user.id}",
                "name": "研究工作大纲",
                "structure": [
                    {
                        "id": "1760603546532",
                        "title": "一、研究目标、研究内容、指标和成果要求",
                        "font": "宋体",
                        "size": 14,
                        "color": "rgb(0,0,0)",
                        "bold": True,
                        "italic": False,
                        "id_level": 1,
                        "children": [
                            {
                                "id": "1760603571616",
                                "title": "（一）研究目标",
                                "font": "宋体",
                                "size": 14,
                                "color": "rgb(0,0,0)",
                                "bold": True,
                                "italic": False,
                                "id_level": 2,
                                "children": []
                            },
                            {
                                "id": "1760603579154",
                                "title": "（二）研究内容",
                                "font": "宋体",
                                "size": 14,
                                "color": "rgb(0,0,0)",
                                "bold": True,
                                "italic": False,
                                "id_level": 2,
                                "children": []
                            },
                            {
                                "id": "1760603585187",
                                "title": "（三）指标要求",
                                "font": "宋体",
                                "size": 14,
                                "color": "rgb(0,0,0)",
                                "bold": True,
                                "italic": False,
                                "id_level": 2,
                                "children": []
                            },
                            {
                                "id": "1760603591189",
                                "title": "（四）成果要求",
                                "font": "宋体",
                                "size": 14,
                                "color": "rgb(0,0,0)",
                                "bold": True,
                                "italic": False,
                                "id_level": 2,
                                "children": []
                            }
                        ]
                    },
                    {
                        "id": "1760603599425",
                        "title": "二、技术现状分析",
                        "font": "宋体",
                        "size": 14,
                        "color": "rgb(0,0,0)",
                        "bold": True,
                        "italic": False,
                        "id_level": 1,
                        "children": [
                            {
                                "id": "1760603609959",
                                "title": "（一）拟研究的基本问题及意义",
                                "font": "宋体",
                                "size": 14,
                                "color": "rgb(0,0,0)",
                                "bold": True,
                                "italic": False,
                                "id_level": 2,
                                "children": [
                                    {
                                        "id": "1760603620403",
                                        "title": "1.对项目基本问题的概念描述。",
                                        "font": "宋体",
                                        "size": 14,
                                        "color": "rgb(0,0,0)",
                                        "bold": True,
                                        "italic": False,
                                        "id_level": 3,
                                        "children": []
                                    },
                                    {
                                        "id": "1760603633200",
                                        "title": "2.项目基本问题的研究意义简述",
                                        "font": "宋体",
                                        "size": 14,
                                        "color": "rgb(0,0,0)",
                                        "bold": True,
                                        "italic": False,
                                        "id_level": 3,
                                        "children": [
                                            {
                                                "id": "1760603639908",
                                                "title": "2.1 科学意义",
                                                "font": "宋体",
                                                "size": 14,
                                                "color": "rgb(0,0,0)",
                                                "bold": True,
                                                "italic": False,
                                                "id_level": 4,
                                                "children": []
                                            },
                                            {
                                                "id": "1760603648725",
                                                "title": "2.2 技术推动意义",
                                                "font": "宋体",
                                                "size": 14,
                                                "color": "rgb(0,0,0)",
                                                "bold": True,
                                                "italic": False,
                                                "id_level": 4,
                                                "children": []
                                            },
                                            {
                                                "id": "1760603655501",
                                                "title": "2.3 实用意义",
                                                "font": "宋体",
                                                "size": 14,
                                                "color": "rgb(0,0,0)",
                                                "bold": True,
                                                "italic": False,
                                                "id_level": 4,
                                                "children": []
                                            }
                                        ]
                                    }
                                ]
                            },
                            {
                                "id": "1760603667534",
                                "title": "（二）国内外相关研究工作现状",
                                "font": "宋体",
                                "size": 14,
                                "color": "rgb(0,0,0)",
                                "bold": True,
                                "italic": False,
                                "id_level": 2,
                                "children": [
                                    {
                                        "id": "1760603677160",
                                        "title": "1.与本项目基本问题相关的国外研究概况。",
                                        "font": "宋体",
                                        "size": 14,
                                        "color": "rgb(0,0,0)",
                                        "bold": True,
                                        "italic": False,
                                        "id_level": 3,
                                        "children": []
                                    },
                                    {
                                        "id": "1760603685086",
                                        "title": "2. 与本项目基本问题相关的国内研究概况。",
                                        "font": "宋体",
                                        "size": 14,
                                        "color": "rgb(0,0,0)",
                                        "bold": True,
                                        "italic": False,
                                        "id_level": 3,
                                        "children": []
                                    },
                                    {
                                        "id": "1760603693269",
                                        "title": "3.对国内外研究工作分别存在的困难、缺失或不足的分析。",
                                        "font": "宋体",
                                        "size": 14,
                                        "color": "rgb(0,0,0)",
                                        "bold": True,
                                        "italic": False,
                                        "id_level": 3,
                                        "children": []
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        "id": "1760603700770",
                        "title": "（三）项目所提指标的先进合理性分析",
                        "font": "宋体",
                        "size": 14,
                        "color": "rgb(0,0,0)",
                        "bold": True,
                        "italic": False,
                        "id_level": 1,
                        "children": [
                            {
                                "id": "1760603715602",
                                "title": "1.所提出的指标在反映基本问题研究水平及研究目标实现程度上的合理性或充分性分析",
                                "font": "宋体",
                                "size": 14,
                                "color": "rgb(0,0,0)",
                                "bold": True,
                                "italic": False,
                                "id_level": 2,
                                "children": []
                            },
                            {
                                "id": "1760603722524",
                                "title": "2.所提指标在国内外所处的水平。",
                                "font": "宋体",
                                "size": 14,
                                "color": "rgb(0,0,0)",
                                "bold": True,
                                "italic": False,
                                "id_level": 2,
                                "children": []
                            }
                        ]
                    },
                    {
                        "id": "1760603732505",
                        "title": "三、技术总方案",
                        "font": "宋体",
                        "size": 14,
                        "color": "rgb(0,0,0)",
                        "bold": True,
                        "italic": False,
                        "id_level": 1,
                        "children": [
                            {
                                "id": "1760603747671",
                                "title": "（一）方案设计的基本考虑",
                                "font": "宋体",
                                "size": 14,
                                "color": "rgb(0,0,0)",
                                "bold": True,
                                "italic": False,
                                "id_level": 2,
                                "children": [
                                    {
                                        "id": "1760603762358",
                                        "title": "1.基于项目目标及研究内容要求，进行研究工作总体方案设计时需要考虑的基本因素。",
                                        "font": "宋体",
                                        "size": 14,
                                        "color": "rgb(0,0,0)",
                                        "bold": True,
                                        "italic": False,
                                        "id_level": 3,
                                        "children": []
                                    },
                                    {
                                        "id": "1760603771080",
                                        "title": "2.总体方案的设计依据",
                                        "font": "宋体",
                                        "size": 14,
                                        "color": "rgb(0,0,0)",
                                        "bold": True,
                                        "italic": False,
                                        "id_level": 3,
                                        "children": [
                                            {
                                                "id": "1760603777881",
                                                "title": "2.1 科学依据",
                                                "font": "宋体",
                                                "size": 14,
                                                "color": "rgb(0,0,0)",
                                                "bold": True,
                                                "italic": False,
                                                "id_level": 4,
                                                "children": []
                                            },
                                            {
                                                "id": "1760603784475",
                                                "title": "2.2 经验依据",
                                                "font": "宋体",
                                                "size": 14,
                                                "color": "rgb(0,0,0)",
                                                "bold": True,
                                                "italic": False,
                                                "id_level": 4,
                                                "children": []
                                            },
                                            {
                                                "id": "1760603791166",
                                                "title": "2.3 方法依据",
                                                "font": "宋体",
                                                "size": 14,
                                                "color": "rgb(0,0,0)",
                                                "bold": True,
                                                "italic": False,
                                                "id_level": 4,
                                                "children": []
                                            },
                                            {
                                                "id": "1760603798792",
                                                "title": "2.4 运作可行性依据",
                                                "font": "宋体",
                                                "size": 14,
                                                "color": "rgb(0,0,0)",
                                                "bold": True,
                                                "italic": False,
                                                "id_level": 4,
                                                "children": []
                                            }
                                        ]
                                    }
                                ]
                            },
                            {
                                "id": "1760603753980",
                                "title": "（二）总体方案",
                                "font": "宋体",
                                "size": 14,
                                "color": "rgb(0,0,0)",
                                "bold": True,
                                "italic": False,
                                "id_level": 2,
                                "children": [
                                    {
                                        "id": "1760603805992",
                                        "title": "1.项目研究工作的总体方案",
                                        "font": "宋体",
                                        "size": 14,
                                        "color": "rgb(0,0,0)",
                                        "bold": True,
                                        "italic": False,
                                        "id_level": 3,
                                        "children": []
                                    },
                                    {
                                        "id": "1760603812082",
                                        "title": "2.对项目研究工作时间进程和考核验证点的设想。",
                                        "font": "宋体",
                                        "size": 14,
                                        "color": "rgb(0,0,0)",
                                        "bold": True,
                                        "italic": False,
                                        "id_level": 3,
                                        "children": []
                                    },
                                    {
                                        "id": "1760603817546",
                                        "title": "3.能够充分反映项目目标实现情况的考核方案。",
                                        "font": "宋体",
                                        "size": 14,
                                        "color": "rgb(0,0,0)",
                                        "bold": True,
                                        "italic": False,
                                        "id_level": 3,
                                        "children": []
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        "id": "1760603828087",
                        "title": "四、关键科学技术问题分析",
                        "font": "宋体",
                        "size": 14,
                        "color": "rgb(0,0,0)",
                        "bold": True,
                        "italic": False,
                        "id_level": 1,
                        "children": [
                            {
                                "id": "1760603836091",
                                "title": "（一）以第一个关键科学技术问题为标题",
                                "font": "宋体",
                                "size": 14,
                                "color": "rgb(0,0,0)",
                                "bold": True,
                                "italic": False,
                                "id_level": 2,
                                "children": []
                            },
                            {
                                "id": "1760603843506",
                                "title": "（二）以第二个关键问题为标题",
                                "font": "宋体",
                                "size": 14,
                                "color": "rgb(0,0,0)",
                                "bold": True,
                                "italic": False,
                                "id_level": 2,
                                "children": []
                            }
                        ]
                    },
                    {
                        "id": "1760603854262",
                        "title": "五、项目实施计划及研究阶段划分",
                        "font": "宋体",
                        "size": 14,
                        "color": "rgb(0,0,0)",
                        "bold": True,
                        "italic": False,
                        "id_level": 1,
                        "children": []
                    }
                ]
            }

        ]

        # 2. 批量创建/更新默认模板（不存在则创建，存在则跳过）
        for template_data in default_templates_data:
            Template.objects.get_or_create(
                id=template_data["id"],  # 用唯一ID匹配，避免重复创建
                user=user,               # 关联当前用户，确保数据隔离
                defaults={
                    "name": template_data["name"],
                    "structure": template_data["structure"]
                }
            )

        # 3. 查询当前用户的所有默认模板并返回
        user_default_templates = Template.objects.filter(user=user)

        # 4. 格式化返回数据（与list_templates格式保持一致）
        response_data = [{
            "id": t.id,
            "name": t.name,
            "structure": t.structure
        } for t in user_default_templates]

        return JsonResponse({
            "success": True,
            "templates": response_data
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)