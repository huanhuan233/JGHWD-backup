from django.urls import path
from .views import knowledge_config_api, update_knowledge_config,delete_orphan_file

urlpatterns = [
    path('configs/', knowledge_config_api),
    path('configs/<int:pk>/', update_knowledge_config),  # 👈 加这一行！
    path('delete-orphan-file/', delete_orphan_file),
]