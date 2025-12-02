import json
import re
import string
import random
from rest_framework.request import Request
from django.shortcuts import get_object_or_404
from django.contrib.auth import login, authenticate
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view,authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import User

# 管理员账号密码写死在这里
ADMIN_USERNAME = 'Admin'
ADMIN_PASSWORD = 'Root1234'


@csrf_exempt
def register(request):
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'error': '仅支持POST请求'
        }, status=405)

    try:
        # 解析JSON请求体
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        confirm_password = data.get('confirm_password')
        hint_question = data.get('password_hint_question', '')
        hint_answer = data.get('password_hint_answer', '')

        # 基础验证
        if not all([username, password, confirm_password]):
            return JsonResponse({
                'success': False,
                'error': '用户名、密码和确认密码为必填项'
            }, status=400)

        # 用户名唯一性验证
        if User.objects.filter(username=username).exists():
            return JsonResponse({
                'success': False,
                'error': '用户名已存在'
            }, status=400)

        # 密码长度验证（不少于8位）
        if len(password) < 8:
            return JsonResponse({
                'success': False,
                'error': '密码长度不少于8位'
            }, status=400)

        # 密码一致性验证
        if password != confirm_password:
            return JsonResponse({
                'success': False,
                'error': '两次密码输入不一致'
            }, status=400)

        # 创建用户（密码自动加密）
        user = User.objects.create_user(
            username=username,
            password=password,
            password_hint_question=hint_question,
            password_hint_answer=hint_answer
        )
        
        # 为新用户生成Token
        token, _ = Token.objects.get_or_create(user=user)

        return JsonResponse({
            'success': True,
            'message': '注册成功',
            'user_id': user.id,
            'token': token.key  # 返回用户Token
        }, status=201)

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': '无效的JSON格式'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'服务器错误: {str(e)}'
        }, status=500)



@csrf_exempt
def admin_login(request):
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'error': '仅支持POST请求'
        }, status=405)
    
    try:
        data = json.loads(request.body)
        input_username = data.get('username')  # 用户输入的账号
        input_password = data.get('password')  # 用户输入的密码
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': '无效的JSON格式'
        }, status=400)
    
    if not input_username or not input_password:
        return JsonResponse({
            'success': False,
            'error': '用户名和密码为必填项'
        }, status=400)
    
    # --------------------------
    # 管理员登录逻辑（优化顺序：先验证密码，再处理账号）
    # --------------------------
    try:
        # 1. 第一步：先判断输入的账号是否是配置中的管理员账号
        if input_username != ADMIN_USERNAME:
            # 账号不对，直接进入普通用户登录逻辑（或返回错误）
            pass
        
        # 2. 第二步：验证输入的密码是否匹配配置项（关键优化：先验密码）
        else:
            # 密码和配置项不匹配，直接返回错误（无需操作数据库）
            if input_password != ADMIN_PASSWORD:
                return JsonResponse({
                    'success': False,
                    'error': '用户名或密码错误'
                }, status=401)
            
            # 3. 第三步：密码正确，再处理数据库中的管理员账号（同步逻辑）
            existing_superusers = User.objects.filter(is_superuser=True)
            target_admin = existing_superusers.filter(username=ADMIN_USERNAME).first()
            
            # 3.1 数据库中没有该管理员 → 新建
            if not target_admin:
                target_admin = User.objects.create_superuser(
                    username=ADMIN_USERNAME,
                    password=ADMIN_PASSWORD  # Django 自动哈希存储
                )
                            # 清理多余的超级管理员（保证唯一）
            if existing_superusers.count() > 1:
                old_admins = existing_superusers.exclude(username=ADMIN_USERNAME)
                old_admins.delete()
            # 3.2 数据库中有该管理员 → 检查密码是否需要更新（防止配置变更）
            else:
                # 配置的密码变了，更新数据库中的密码
                if not target_admin.check_password(ADMIN_PASSWORD):
                    target_admin.set_password(ADMIN_PASSWORD)
                    target_admin.save()
                
                # 清理多余的超级管理员（保证唯一）
                if existing_superusers.count() > 1:
                    old_admins = existing_superusers.exclude(username=ADMIN_USERNAME)
                    old_admins.delete()
            
            # 4. 第四步：生成 Token，返回登录成功
            def generate_unique_admin_token_key():
                while True:
                    key = f"admin_{''.join(random.choices(string.ascii_letters + string.digits, k=32))}"
                    if not Token.objects.filter(key=key).exists():
                        return key
            
            #Token.objects.filter(user=target_admin).delete()
            token, _ = Token.objects.get_or_create(
                key=generate_unique_admin_token_key,
                defaults={'user': target_admin}
            )
            
            return JsonResponse({
                'success': True,
                'message': '管理员登录成功',
                'token': token.key,
                'username': target_admin.username,
                'is_admin': target_admin.is_superuser,
                'admin_id': target_admin.id
            })
        
        # --------------------------
        # 普通用户登录逻辑（不变）
        # --------------------------
        user = authenticate(username=input_username, password=input_password)
        if user and not user.is_superuser:
            login(request, user)
            #Token.objects.filter(user=user).delete()
            token, _ = Token.objects.get_or_create(user=user)
            return JsonResponse({
                'success': True,
                'message': '用户登录成功',
                'user_id': user.id,
                'username': user.username,
                'is_admin': user.is_superuser,
                'token': token.key
            })
        else:
            return JsonResponse({
                'success': False,
                'error': '用户名或密码错误'
            }, status=401)
    
    # 捕获异常并返回详情（方便调试）
    except Exception as e:
        print(f"管理员登录异常：{type(e).__name__} - {str(e)}")  # 生产环境替换为日志
        return JsonResponse({
            'success': False,
            'error': '服务器内部错误'
        }, status=500)


@csrf_exempt
@api_view(['GET', 'POST']) 
@authentication_classes([TokenAuthentication])  # 启用Token认证
@permission_classes([IsAuthenticated])  # 要求必须通过认证
def admin_dashboard(request):
    # 验证是否为管理员Token
    if not request.auth.key.startswith('admin_'):
        return JsonResponse({
            'success': False,
            'error': '无管理员权限'
        }, status=403)
    
    users = User.objects.all().values('id', 'username', 'date_joined', 'is_active','is_superuser')
 
    return JsonResponse({
        'success': True,
        'users': list(users)
    })


@csrf_exempt
@api_view(['GET', 'POST']) 
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def reset_user_password(request, user_id):
    # 验证是否为管理员Token
    if not request.auth.key.startswith('admin_'):
        return JsonResponse({
            'success': False,
            'error': '无管理员权限'
        }, status=403)
    
    user = get_object_or_404(User, id=user_id)
    new_password = User.generate_random_password()
    user.set_password(new_password)
    user.save()
    
    # 重置密码后更新用户Token（增强安全性）
    Token.objects.filter(user=user).delete()
    new_token, _ = Token.objects.get_or_create(user=user)
    
    return JsonResponse({
        'success': True,
        'new_password': new_password,
        'new_token': new_token.key  # 返回更新后的用户Token
    })


@csrf_exempt
@api_view(['GET']) 
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def logout(request):
    """注销接口：删除当前Token"""
    request.auth.delete()
    return JsonResponse({
        'success': True,
        'message': '已成功注销'
    })

@csrf_exempt
def verify_user(request):
    data = json.loads(request.body)
    input_username = data.get('username')  # 用户输入的账号
    try:
        user = User.objects.get(username=input_username)
        if user.is_superuser:
            return JsonResponse({
                'success': False,
                'error': '用户不存在'
            }, status=403)
    except User.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': '用户不存在'
        }, status=404)
    return JsonResponse({
        'success': True,
        'hint_question': user.password_hint_question,
        'username': input_username
    })

@csrf_exempt
def verify_user_question(request):
    data = json.loads(request.body)
    input_username = data.get('username') 
    hint_answer = data.get('hint_answer') 
    user = User.objects.get(username=input_username)
    if user.password_hint_answer == hint_answer:
        Token.objects.filter(user=user).delete()
        new_token, _ = Token.objects.get_or_create(user=user)
        return JsonResponse({
            'success': True,
            'message': '回答正确',
            'token': new_token.key  

        })
    else:
        return JsonResponse({
            'success': False,
            'error': '回答错误'
        }, status=401)

@csrf_exempt
@api_view(['POST']) 
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def reset_password(request):
    data = json.loads(request.body)
    new_password = data.get('new_password')
    confirm_password = data.get('confirm_password')
    user = request.user
    if user.is_superuser:
            return JsonResponse({
                'success': False,
                'error': '管理员账户不能通过此方式修改密码'
            }, status=403)
    if new_password != confirm_password:
        return JsonResponse({
            'success': False,
            'error': '两次输入的新密码不一致'
        }, status=400)
    else:
        user.set_password(new_password)
        user.save()
        Token.objects.filter(user=user).delete()
        new_token, _ = Token.objects.get_or_create(user=user)
        return JsonResponse({
            'success': True,
            'token': new_token.key
            })
