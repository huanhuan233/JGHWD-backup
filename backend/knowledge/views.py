from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import KnowledgeConfig
from .serializers import KnowledgeConfigSerializer
from django.conf import settings
import os, json, time
from rest_framework.decorators import api_view,authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.csrf import csrf_exempt

# ✅ 保存配置模板到文件
def save_template_format(config_dict):
    folder = os.path.join(settings.BASE_DIR, 'template_storage', 'knowledge_configs')
    os.makedirs(folder, exist_ok=True)
    timestamp = time.strftime('%Y%m%d_%H%M%S')
    safe_name = config_dict['name'].replace(' ', '_')
    filename = f"{config_dict['type']}_{safe_name}_{timestamp}.json"
    filepath = os.path.join(folder, filename)

    print("📁 模板保存路径：", filepath)

    if config_dict['type'] == 'dify':
        print("🧩 正在生成 Dify 模板...")

        # ✅ 包含 type 和 api_key，确保能被后续识别
        template = {
            "type": config_dict["type"],
            "api_key": config_dict["api_key"],
            "method": "POST",
            "url": "http://host.docker.internal:8080/v1/completion-messages",
            "headers": {
                "Authorization": f"Bearer {config_dict['api_key']}",
                "Content-Type": "application/json"
            },
            "body": {
                "inputs": {
                    "query": "请输入您的问题"
                },
                "response_mode": "streaming",
                "user": "abc-123"
            }
        }
    elif config_dict['type'] == 'FastGpt':
        print("🧩 正在生成 FastGPT 模板...")
        # ✅ 包含 type 和 api_key，确保能被后续识别
        template = {
            "type": config_dict["type"],
            "api_key": config_dict["api_key"],
            "method": "POST",
            "url": "http://host.docker.internal:3000/v1/chat/completions",
            "headers": {
                "Authorization": f"Bearer {config_dict['api_key']}",
                "Content-Type": "application/json"
            },
            "body": {
                "stream": False,
                "detail": False, 
                "messages": [{
                         "content":"请输入您的问题",
                         "role":"user"
                        }] 
            }
        }    
    else:
        print("⚠️ 未知类型，无法生成模板：", config_dict['type'])
        template = {
            "type": config_dict["type"],
            "api_key": config_dict["api_key"],
            "message": "未知知识库类型，无法生成模板"
        }

    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(template, f, ensure_ascii=False, indent=2)
        print("✅ 模板保存成功！")
    except Exception as e:
        print("❌ 模板保存失败：", e)


# ✅ 主配置接口：GET 返回所有配置 + 多余文件，POST 添加，DELETE 删除
@csrf_exempt
@api_view(['GET', 'POST', 'DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def knowledge_config_api(request):
    folder = os.path.join(settings.BASE_DIR, 'template_storage', 'knowledge_configs')

    if request.method == 'GET':
        configs = KnowledgeConfig.objects.filter(user = request.user).order_by('-created_at')
        serializer = KnowledgeConfigSerializer(configs, many=True)

        # 查找所有实际文件
        file_list = [f for f in os.listdir(folder) if f.endswith('.json')]

        # 构造数据库中已有的“类型_配置名”前缀
        db_prefixes = set(
            f"{c['type']}_{c['name'].replace(' ', '_')}"
            for c in serializer.data
        )

        # 找出文件中存在但数据库中没有的
        # extra_files = []
        # for filename in file_list:
        #     if not any(prefix in filename for prefix in db_prefixes):
        #         extra_files.append(filename)

        return Response({
            'configs': serializer.data,
            #'extra_files': extra_files
        })

    elif request.method == 'POST':
        serializer = KnowledgeConfigSerializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.save(user=request.user)
            save_template_format(config_dict=serializer.data)
            return Response({'success': True, 'data': serializer.data}, status=status.HTTP_201_CREATED)
        return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        config_id = request.query_params.get('id')
        try:
            config = KnowledgeConfig.objects.get(id=config_id)
            config_name = config.name.replace(' ', '_')
            config_type = config.type
            config.delete()

            # 删除对应文件
            for filename in os.listdir(folder):
                if config_name in filename and config_type in filename and filename.endswith('.json'):
                    os.remove(os.path.join(folder, filename))
                    print(f"🗑 已删除配置文件: {filename}")

            return Response({'success': True, 'message': '配置及文件已删除'})
        except KnowledgeConfig.DoesNotExist:
            return Response({'success': False, 'error': '配置不存在'}, status=404)


# ✅ PUT 接口：更新配置并保存新文件
@csrf_exempt
@api_view(['PUT'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def update_knowledge_config(request, pk):
    try:
        config = KnowledgeConfig.objects.get(pk=pk)
    except KnowledgeConfig.DoesNotExist:
        return Response({'success': False, 'error': '配置不存在'}, status=404)

    serializer = KnowledgeConfigSerializer(config, data=request.data)
    if serializer.is_valid():
        instance = serializer.save()
        save_template_format(config_dict=serializer.data)
        return Response({'success': True, 'data': serializer.data})
    return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
@csrf_exempt
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def delete_orphan_file(request):
    filename = request.data.get('filename')
    folder = os.path.join(settings.BASE_DIR, 'template_storage', 'knowledge_configs')
    filepath = os.path.join(folder, filename)
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
            print(f"🗑 删除了孤立文件: {filename}")
            return Response({'success': True})
        else:
            return Response({'success': False, 'error': '文件不存在'}, status=404)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=500)
