from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.upload_header),
    path('', views.list_headers),
    path('<int:id>/', views.delete_header),
]
