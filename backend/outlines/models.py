from django.db import models
from django.conf import settings 
from templates_config.models import Template  # 如果有模板
from knowledge.models import KnowledgeConfig  # 如果用知识库
from django.contrib.auth.models import User  # 如果有登录系统

class Outline(models.Model):
    title = models.CharField(max_length=200)
    structure = models.JSONField()  # 保存多段结构化大纲
    original_structure = models.JSONField(null=True, blank=True)
    model_name = models.CharField(max_length=100)
    title_setting = models.JSONField(null=True, blank=True)
    template = models.ForeignKey(Template, on_delete=models.SET_NULL, null=True, blank=True)
    knowledge_config = models.ForeignKey(KnowledgeConfig, on_delete=models.SET_NULL, null=True, blank=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # 关键修改
        on_delete=models.CASCADE, 
        null=True, 
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
