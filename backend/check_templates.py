#!/usr/bin/env python
"""
快速检查模板数据的脚本（不需要Django环境）
直接查询SQLite数据库
"""
import sqlite3
import json
from datetime import datetime

def check_templates():
    db_path = 'db.sqlite3'
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    print("=" * 70)
    print("模板数据检查报告")
    print("=" * 70)
    
    # 统计总数
    cursor.execute("SELECT COUNT(*) as count FROM templates_config_template")
    total = cursor.fetchone()['count']
    print(f"\n📊 数据库中共有 {total} 个模板\n")
    
    # 检查用户表名
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%user%'")
    user_tables = cursor.fetchall()
    user_table = user_tables[0][0] if user_tables else None
    
    if user_table:
        # 按用户分组统计
        cursor.execute(f"""
            SELECT 
                u.id as user_id,
                u.username,
                COUNT(t.id) as template_count
            FROM templates_config_template t
            LEFT JOIN {user_table} u ON t.user_id = u.id
            GROUP BY u.id, u.username
            ORDER BY template_count DESC
        """)
        
        print("按用户分组的模板数量：")
        user_stats = cursor.fetchall()
        for row in user_stats:
            user_info = f"{row['username']} (ID: {row['user_id']})" if row['username'] else "无用户关联"
            print(f"  {user_info}: {row['template_count']} 个模板")
        
        # 显示所有模板列表
        cursor.execute(f"""
            SELECT 
                t.id,
                t.name,
                u.username,
                u.id as user_id,
                t.created_at
            FROM templates_config_template t
            LEFT JOIN {user_table} u ON t.user_id = u.id
            ORDER BY t.created_at DESC
        """)
    else:
        # 没有用户表，直接查询模板
        cursor.execute("""
            SELECT 
                id,
                name,
                user_id,
                created_at
            FROM templates_config_template
            ORDER BY created_at DESC
        """)
    
    print("\n" + "=" * 70)
    print("所有模板列表（按创建时间倒序）：")
    print("=" * 70)
    
    templates = cursor.fetchall()
    for i, template in enumerate(templates, 1):
        if user_table:
            username = template['username'] if 'username' in template.keys() else None
            user_id = template['user_id'] if 'user_id' in template.keys() else None
            user_info = f"{username} (ID:{user_id})" if username else f"无用户 (ID:{user_id})"
        else:
            user_id = template['user_id'] if 'user_id' in template.keys() else None
            user_info = f"用户ID: {user_id if user_id else '无'}"
        created = template['created_at'][:19] if template['created_at'] else "未知"
        print(f"{i:3d}. {template['name']:<40} | 用户: {user_info:<20} | 创建: {created}")
        print(f"     ID: {template['id']}")
    
    # 导出为JSON
    if user_table:
        cursor.execute(f"""
            SELECT 
                t.id,
                t.name,
                t.structure,
                u.id as user_id,
                u.username,
                t.created_at,
                t.updated_at
            FROM templates_config_template t
            LEFT JOIN {user_table} u ON t.user_id = u.id
            ORDER BY t.created_at DESC
        """)
    else:
        cursor.execute("""
            SELECT 
                id,
                name,
                structure,
                user_id,
                created_at,
                updated_at
            FROM templates_config_template
            ORDER BY created_at DESC
        """)
    
    templates_data = []
    for row in cursor.fetchall():
        templates_data.append({
            'id': row['id'],
            'name': row['name'],
            'structure': json.loads(row['structure']) if row['structure'] else [],
            'user_id': row['user_id'] if 'user_id' in row.keys() else None,
            'username': row['username'] if 'username' in row.keys() else None,
            'created_at': row['created_at'] if 'created_at' in row.keys() else None,
            'updated_at': row['updated_at'] if 'updated_at' in row.keys() else None
        })
    
    backup_file = f"templates_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(backup_file, 'w', encoding='utf-8') as f:
        json.dump({
            'export_time': datetime.now().isoformat(),
            'total_count': total,
            'templates': templates_data
        }, f, ensure_ascii=False, indent=2)
    
    print("\n" + "=" * 70)
    print(f"✅ 模板数据已备份到: {backup_file}")
    print("=" * 70)
    
    conn.close()
    
    return backup_file

if __name__ == '__main__':
    check_templates()

