# contents/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # ✅ 获取文章列表
    path('articles/', views.list_articles, name='list_articles'),

    # ✅ 删除正文内容
    path('delete_content/<int:article_id>', views.delete_content, name='delete_content'),

    # ✅ 更新段落内容
    path('articles/<int:outline_id>/sections/<str:section_id>/', views.update_section_content, name='update_section_content'),

    # ✅ 获取模型选项
    path('models/', views.list_models_for_content),

    # ✅ 自动生成正文并保存
    path('auto-generate/', views.auto_generate_and_save),

    path('export/', views.parse_export),
    
]
