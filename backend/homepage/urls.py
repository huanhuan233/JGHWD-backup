from django.urls import path
from .views import generate_outline, list_models, homepage_view, list_templates,generate_outline_items

urlpatterns = [
    path('', homepage_view, name='homepage'),  # 加了这个根路径处理
    path('generate-outline/', generate_outline, name='generate_outline'),
    path('list-models/', list_models, name='list_models'),
    path('list-templates/', list_templates, name='list_templates'), 
    path('generate-outline-items/', generate_outline_items, name='generate_outline_items'),
]
