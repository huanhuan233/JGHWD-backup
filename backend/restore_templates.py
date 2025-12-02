#!/usr/bin/env python
"""
模板恢复/导出脚本
用于检查和导出数据库中的所有模板
"""
import os
import sys
import django
import json
from datetime import datetime

# 设置Django环境
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from templates_config.models import Template
from django.contrib.auth.models import User

def export_all_templates():
    """导出所有模板到JSON文件"""
    print("=" * 60)
    print("模板恢复/导出工具")
    print("=" * 60)
    
    # 统计信息
    total_templates = Template.objects.count()
    print(f"\n数据库中共有 {total_templates} 个模板\n")
    
    # 按用户分组
    users = User.objects.all()
    print("按用户分组的模板：")
    for user in users:
        user_templates = Template.objects.filter(user=user)
        count = user_templates.count()
        if count > 0:
            print(f"  用户 {user.username} (ID: {user.id}): {count} 个模板")
    
    # 无用户关联的模板
    no_user_templates = Template.objects.filter(user__isnull=True)
    no_user_count = no_user_templates.count()
    if no_user_count > 0:
        print(f"  无用户关联: {no_user_count} 个模板")
    
    print("\n" + "=" * 60)
    
    # 导出所有模板
    all_templates = []
    for template in Template.objects.all().order_by('-created_at'):
        template_data = {
            'id': template.id,
            'name': template.name,
            'structure': template.structure,
            'user_id': template.user.id if template.user else None,
            'username': template.user.username if template.user else None,
            'created_at': template.created_at.isoformat() if template.created_at else None,
            'updated_at': template.updated_at.isoformat() if template.updated_at else None,
        }
        all_templates.append(template_data)
    
    # 保存到文件
    backup_filename = f"templates_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    backup_path = os.path.join(os.path.dirname(__file__), backup_filename)
    
    with open(backup_path, 'w', encoding='utf-8') as f:
        json.dump({
            'export_time': datetime.now().isoformat(),
            'total_count': total_templates,
            'templates': all_templates
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 所有模板已导出到: {backup_path}")
    print(f"   共导出 {total_templates} 个模板")
    
    # 显示最近10个模板
    print("\n最近10个模板：")
    recent_templates = Template.objects.all().order_by('-created_at')[:10]
    for i, template in enumerate(recent_templates, 1):
        user_info = f"{template.user.username} (ID:{template.user.id})" if template.user else "无用户"
        print(f"  {i}. {template.name} (ID: {template.id}) - {user_info}")
    
    return backup_path

def restore_template_from_json(json_file):
    """从JSON文件恢复模板"""
    print(f"\n从 {json_file} 恢复模板...")
    
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    templates_data = data.get('templates', [])
    print(f"找到 {len(templates_data)} 个模板")
    
    restored_count = 0
    skipped_count = 0
    
    for template_data in templates_data:
        template_id = template_data.get('id')
        template_name = template_data.get('name')
        structure = template_data.get('structure', [])
        user_id = template_data.get('user_id')
        
        try:
            user = User.objects.get(id=user_id) if user_id else None
        except User.DoesNotExist:
            user = None
            print(f"  ⚠️  用户 ID {user_id} 不存在，模板 {template_name} 将不关联用户")
        
        template, created = Template.objects.update_or_create(
            id=template_id,
            defaults={
                'name': template_name,
                'structure': structure,
                'user': user
            }
        )
        
        if created:
            restored_count += 1
            print(f"  ✅ 创建模板: {template_name} (ID: {template_id})")
        else:
            skipped_count += 1
            print(f"  ⏭️  模板已存在: {template_name} (ID: {template_id})")
    
    print(f"\n恢复完成: 创建 {restored_count} 个，跳过 {skipped_count} 个")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        # 恢复模式
        json_file = sys.argv[1]
        if os.path.exists(json_file):
            restore_template_from_json(json_file)
        else:
            print(f"❌ 文件不存在: {json_file}")
    else:
        # 导出模式
        export_all_templates()

