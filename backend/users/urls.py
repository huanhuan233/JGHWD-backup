from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.admin_login, name='admin_login'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/reset-password/<int:user_id>/', views.reset_user_password, name='reset_password'),
    path('logout/', views.logout, name='logout'),  # 注销接口
    path('verify-user/', views.verify_user, name='verify_user'),  # 验证用户存在性并获取提示问题
    path('verify-question/', views.verify_user_question, name='verify_user_question'),  # 验证提示问题答案
    path('reset-password/', views.reset_password, name='user_reset_password'),  # 用户自行重置密码
]