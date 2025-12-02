"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
import dotenv
from django.conf import settings
from django.conf.urls.static import static
dotenv.load_dotenv()

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('homepage.urls')),           # 给 homepage 统一加上 api 前缀
    path('api/templates/', include('templates_config.urls')),  # 给 templates_config 加个不同前缀
    path('api/knowledge/', include('knowledge.urls')),
    path('api/', include('outlines.urls')),
    path('api/contents/', include('contents.urls')),
    path('api/headers/', include('headers.urls')),
    path('api/users/', include('users.urls')), 

]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)